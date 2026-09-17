from datetime import date as date_type
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/habits", tags=["Habits"])


def compute_health_score(sleep_hours: float, water_liters: float, steps: int) -> float:
    """
    Simple weighted score out of 100.
    Targets: 8h sleep, 3L water, 8000 steps — each capped at its own max
    contribution so no single habit can carry the whole score alone.
    Tune these weights/targets as the What-If simulator needs.
    """
    sleep_score = min(sleep_hours / 8, 1) * 35
    water_score = min(water_liters / 3, 1) * 25
    steps_score = min(steps / 8000, 1) * 40
    return round(sleep_score + water_score + steps_score, 1)


@router.get("/{log_date}", response_model=schemas.HabitOut)
def get_habit(log_date: date_type, db: Session = Depends(get_db),
              current_user: models.User = Depends(auth.get_current_user)):
    entry = db.query(models.HabitLog).filter(
        models.HabitLog.user_id == current_user.id,
        models.HabitLog.date == log_date,
    ).first()

    if not entry:
        # No log yet for this date — return zeroed-out values, not a 404,
        # so the frontend can render an empty state cleanly.
        return schemas.HabitOut(date=log_date, sleep_hours=0, water_liters=0, steps=0, score=0)

    return entry


@router.post("", response_model=schemas.HabitOut)
def upsert_habit(payload: schemas.HabitIn, db: Session = Depends(get_db),
                  current_user: models.User = Depends(auth.get_current_user)):
    entry = db.query(models.HabitLog).filter(
        models.HabitLog.user_id == current_user.id,
        models.HabitLog.date == payload.date,
    ).first()

    score = compute_health_score(payload.sleep_hours, payload.water_liters, payload.steps)

    if entry:
        entry.sleep_hours = payload.sleep_hours
        entry.water_liters = payload.water_liters
        entry.steps = payload.steps
        entry.score = score
    else:
        entry = models.HabitLog(
            user_id=current_user.id,
            date=payload.date,
            sleep_hours=payload.sleep_hours,
            water_liters=payload.water_liters,
            steps=payload.steps,
            score=score,
        )
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return entry


@router.get("/what-if/{walk_minutes}", response_model=schemas.HabitOut)
def what_if_simulator(walk_minutes: int, log_date: date_type, db: Session = Depends(get_db),
                       current_user: models.User = Depends(auth.get_current_user)):
    """
    Projects the score for `log_date` if the user added `walk_minutes` of
    extra walking, assuming ~100 steps/minute of brisk walking.
    """
    entry = db.query(models.HabitLog).filter(
        models.HabitLog.user_id == current_user.id,
        models.HabitLog.date == log_date,
    ).first()

    base_sleep = entry.sleep_hours if entry else 0
    base_water = entry.water_liters if entry else 0
    base_steps = entry.steps if entry else 0

    projected_steps = base_steps + (walk_minutes * 100)
    projected_score = compute_health_score(base_sleep, base_water, projected_steps)

    return schemas.HabitOut(date=log_date, sleep_hours=base_sleep, water_liters=base_water,
                             steps=projected_steps, score=projected_score)
