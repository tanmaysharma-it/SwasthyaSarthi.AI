"""
Mental health check-in — daily mood log (1-5 scale).
Detects consistently low mood over recent entries and returns a gentle
suggestion + a helpline/resource line. This is NOT a diagnosis.
"""
from datetime import date as date_type
from statistics import mean

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/mood", tags=["Mental Health"])

LOW_MOOD_THRESHOLD = 2.5
RECENT_ENTRIES_WINDOW = 5
MIN_ENTRIES_FOR_INSIGHT = 3

HELPLINE_MESSAGE = (
    "Agar aap consistently low feel kar rahe hain, toh kisi se baat karna madad kar sakta hai. "
    "Aap KIRAN Mental Health Helpline (1800-599-0019, 24x7, toll-free) par baat kar sakte hain, "
    "ya kisi trusted doctor/counselor se milein."
)


@router.post("", response_model=schemas.MoodOut, status_code=201)
def log_mood(payload: schemas.MoodIn, db: Session = Depends(get_db),
             current_user: models.User = Depends(auth.get_current_user)):
    entry = db.query(models.MoodLog).filter(
        models.MoodLog.user_id == current_user.id,
        models.MoodLog.date == payload.date,
    ).first()

    if entry:
        entry.mood_score = payload.mood_score
        entry.note = payload.note
    else:
        entry = models.MoodLog(
            user_id=current_user.id,
            date=payload.date,
            mood_score=payload.mood_score,
            note=payload.note,
        )
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return entry


@router.get("/{log_date}", response_model=schemas.MoodOut)
def get_mood(log_date: date_type, db: Session = Depends(get_db),
             current_user: models.User = Depends(auth.get_current_user)):
    entry = db.query(models.MoodLog).filter(
        models.MoodLog.user_id == current_user.id,
        models.MoodLog.date == log_date,
    ).first()
    if not entry:
        return schemas.MoodOut(date=log_date, mood_score=0, note=None)
    return entry


@router.get("/insights/summary", response_model=schemas.MoodInsightOut)
def mood_insights(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    entries = (
        db.query(models.MoodLog)
        .filter(models.MoodLog.user_id == current_user.id)
        .order_by(models.MoodLog.date.desc())
        .limit(RECENT_ENTRIES_WINDOW)
        .all()
    )

    if len(entries) < MIN_ENTRIES_FOR_INSIGHT:
        return schemas.MoodInsightOut(
            low_mood_alert=False,
            average_recent_score=None,
            message="Abhi tak enough mood check-ins nahi hain insight dene ke liye. Kuch din aur log karte raho.",
        )

    avg_score = round(mean(e.mood_score for e in entries), 2)

    if avg_score <= LOW_MOOD_THRESHOLD:
        return schemas.MoodInsightOut(
            low_mood_alert=True,
            average_recent_score=avg_score,
            message=HELPLINE_MESSAGE,
        )

    return schemas.MoodInsightOut(
        low_mood_alert=False,
        average_recent_score=avg_score,
        message="Aapka recent mood theek dikh raha hai. Apna khayal rakhte raho!",
    )