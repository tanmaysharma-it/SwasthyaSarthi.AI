from datetime import date as date_type, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth, schemes_engine
from app.symptom_engine import get_reply, _find_symptom

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


def _get_habit_note(db: Session, user_id: int) -> str | None:
    """
    Looks at the user's most recent habit log (last 3 days) and returns a
    gentle, relevant note if sleep/water/steps look low — used to make the
    chatbot's advice feel personalized instead of purely generic.
    """
    cutoff = date_type.today() - timedelta(days=3)
    recent = (
        db.query(models.HabitLog)
        .filter(models.HabitLog.user_id == user_id, models.HabitLog.date >= cutoff)
        .order_by(models.HabitLog.date.desc())
        .first()
    )
    if not recent:
        return None

    notes = []
    if recent.sleep_hours and recent.sleep_hours < 6:
        notes.append("aapki neend kam ho rahi hai")
    if recent.water_liters and recent.water_liters < 1.5:
        notes.append("paani bhi kam pee rahe hain")
    if recent.steps is not None and recent.steps < 2000:
        notes.append("activity bhi kaafi kam hai")

    if not notes:
        return None

    return "Waise humne dekha " + ", ".join(notes) + " — ye bhi symptoms ki ek wajah ho sakti hai."


@router.post("/message", response_model=schemas.ChatOut)
def send_message(payload: schemas.ChatIn, db: Session = Depends(get_db),
                  current_user: models.User = Depends(auth.get_current_user)):
    result = get_reply(payload.message)

    # Save the conversation turn
    chat_entry = models.ChatMessage(
        user_id=current_user.id,
        message=payload.message,
        reply=result.reply,
        severity=result.severity,
        is_emergency=result.is_emergency,
    )
    db.add(chat_entry)

    # If a known symptom was detected, log it for Community Pulse aggregation
    symptom_key, _ = _find_symptom(payload.message)
    if symptom_key:
        db.add(models.SymptomEntry(
            user_id=current_user.id,
            region=current_user.region,
            symptom=symptom_key,
            severity=result.severity,
        ))

    db.commit()

    # Habit-aware context: gently mention if recent habits look off
    habit_note = _get_habit_note(db, current_user.id)

    # Govt scheme auto-detection: if a serious condition is mentioned, attach it
    condition_key, schemes = schemes_engine.find_schemes(payload.message)
    scheme_suggestion = None
    if condition_key and schemes:
        first = schemes[0]
        scheme_suggestion = schemas.SchemeOut(
            condition=condition_key,
            scheme_name=first["scheme_name"],
            description=first["description"],
        )

    return schemas.ChatOut(
        reply=result.reply,
        severity=result.severity,
        is_emergency=result.is_emergency,
        habit_note=habit_note,
        scheme_suggestion=scheme_suggestion,
    )