from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth
from app.symptom_engine import get_reply, _find_symptom

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


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

    return schemas.ChatOut(reply=result.reply, severity=result.severity, is_emergency=result.is_emergency)
