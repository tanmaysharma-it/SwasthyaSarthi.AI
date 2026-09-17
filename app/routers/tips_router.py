"""
Festival/season-aware health tips — static date-range -> tip mapping.
"""
from datetime import date as date_type

from fastapi import APIRouter

from app import schemas

router = APIRouter(prefix="/tips", tags=["Tips"])

SEASONAL_RULES = [
    (10, 15, 11, 15, "Diwali Sugar Alert",
     "Tyohaar ke mithai aur snacks mein sugar zyada hota hai. Portion control rakho aur paani zyada piyo."),
    (12, 1, 2, 15, "Winter Activity Reminder",
     "Thand mein activity kam ho jaati hai. Roz thodi der dhoop mein walk karo aur garam kapde pehno."),
    (6, 1, 9, 30, "Monsoon Water Safety",
     "Baarish ke mausam mein paani ubaal ke ya filter karke piyo, aur bahar ka khula khana avoid karo."),
    (3, 1, 4, 15, "Holi Skin Care",
     "Rang khelne se pehle skin aur baalon par tel lagao, aur colors dhone ke baad moisturize zaroor karo."),
    (4, 16, 6, 15, "Summer Heat Safety",
     "Garmi mein din mein zyada paani piyo, dhoop mein bahar jaane se bacho, aur halka khana khao."),
]


def _get_tips_for_date(today: date_type) -> list[schemas.TipOut]:
    tips = []
    for start_m, start_d, end_m, end_d, title, message in SEASONAL_RULES:
        start = date_type(today.year, start_m, start_d)
        end = date_type(today.year, end_m, end_d)
        if start <= today <= end:
            tips.append(schemas.TipOut(title=title, message=message))
    return tips


@router.get("/today", response_model=schemas.TipsTodayOut)
def get_todays_tips():
    today = date_type.today()
    return schemas.TipsTodayOut(date=today, tips=_get_tips_for_date(today))