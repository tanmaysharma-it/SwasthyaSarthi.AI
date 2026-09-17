from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/community", tags=["Community"])

# If any single symptom is logged by more users than this within 7 days,
# flag an outbreak alert. Tune based on real usage volume during the hackathon demo.
OUTBREAK_THRESHOLD = 5


@router.get("/trends", response_model=schemas.CommunityTrendsOut)
def get_trends(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    since = datetime.utcnow() - timedelta(days=7)

    rows = (
        db.query(
            func.date(models.SymptomEntry.created_at).label("date"),
            models.SymptomEntry.symptom,
            func.count(models.SymptomEntry.id).label("count"),
        )
        .filter(models.SymptomEntry.created_at >= since)
        .group_by(func.date(models.SymptomEntry.created_at), models.SymptomEntry.symptom)
        .all()
    )

    trends = [schemas.TrendPoint(date=row.date, symptom=row.symptom, count=row.count) for row in rows]

    symptom_totals = defaultdict(int)
    for row in rows:
        symptom_totals[row.symptom] += row.count
    outbreak_alert = any(total >= OUTBREAK_THRESHOLD for total in symptom_totals.values())

    return schemas.CommunityTrendsOut(trends=trends, outbreak_alert=outbreak_alert)
