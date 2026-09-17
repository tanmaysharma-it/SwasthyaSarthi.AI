from datetime import timedelta
from statistics import mean
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/cycles", tags=["Cycles"])

DEFAULT_CYCLE_LENGTH_DAYS = 28


def predict_next_cycle(history: list[models.CycleLog]) -> Optional[object]:
    """
    Predicts the next cycle start date.
    - With 2+ past cycles: average the gap between consecutive start dates.
    - With exactly 1 cycle: fall back to the default 28-day cycle length.
    - With 0 cycles: no prediction possible.
    """
    if not history:
        return None

    sorted_history = sorted(history, key=lambda c: c.start_date)

    if len(sorted_history) == 1:
        return sorted_history[-1].start_date + timedelta(days=DEFAULT_CYCLE_LENGTH_DAYS)

    gaps = [
        (sorted_history[i].start_date - sorted_history[i - 1].start_date).days
        for i in range(1, len(sorted_history))
    ]
    avg_gap = round(mean(gaps))
    return sorted_history[-1].start_date + timedelta(days=avg_gap)


@router.get("", response_model=schemas.CycleHistoryOut)
def get_cycles(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    history = db.query(models.CycleLog).filter(models.CycleLog.user_id == current_user.id).all()
    next_date = predict_next_cycle(history)
    return schemas.CycleHistoryOut(history=history, next_predicted_date=next_date)


@router.post("", response_model=schemas.CycleOut, status_code=201)
def add_cycle(payload: schemas.CycleIn, db: Session = Depends(get_db),
              current_user: models.User = Depends(auth.get_current_user)):
    if current_user.gender.lower() != "female":
        raise HTTPException(status_code=403, detail="Cycle tracking is only available for female profiles")

    entry = models.CycleLog(
        user_id=current_user.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
