from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/community", tags=["Community"])

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

    # Region-wise breakdown (which diseases/symptoms are trending in which region)
    region_rows = (
        db.query(
            models.SymptomEntry.region,
            models.SymptomEntry.symptom,
            func.count(models.SymptomEntry.id).label("count"),
        )
        .filter(models.SymptomEntry.created_at >= since, models.SymptomEntry.region.isnot(None))
        .group_by(models.SymptomEntry.region, models.SymptomEntry.symptom)
        .all()
    )

    region_trends = [
        schemas.RegionTrendPoint(region=row.region, symptom=row.symptom, count=row.count)
        for row in region_rows
    ]

    # Is there an outbreak specifically in the current user's own region?
    your_region_alert = False
    if current_user.region:
        your_region_totals = defaultdict(int)
        for row in region_rows:
            if row.region == current_user.region:
                your_region_totals[row.symptom] += row.count
        your_region_alert = any(total >= OUTBREAK_THRESHOLD for total in your_region_totals.values())

    return schemas.CommunityTrendsOut(
        trends=trends,
        outbreak_alert=outbreak_alert,
        region_trends=region_trends,
        your_region_alert=your_region_alert,
    )