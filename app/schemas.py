"""
Pydantic schemas — define the exact shape of API requests/responses.
These match the API contract shared with the frontend.
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    gender: str  # "Male" | "Female" | "Other"
    age: int = Field(ge=1, le=120)
    region: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    gender: str
    age: int
    region: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    token: str
    user: UserOut


# ---------- Habits ----------

class HabitIn(BaseModel):
    date: date
    sleep_hours: float = Field(ge=0, le=24)
    water_liters: float = Field(ge=0, le=20)
    steps: int = Field(ge=0)


class HabitOut(BaseModel):
    date: date
    sleep_hours: float
    water_liters: float
    steps: int
    score: float

    class Config:
        from_attributes = True


# ---------- Cycles ----------

class CycleIn(BaseModel):
    start_date: date
    end_date: Optional[date] = None


class CycleOut(BaseModel):
    id: int
    start_date: date
    end_date: Optional[date] = None

    class Config:
        from_attributes = True


class CycleHistoryOut(BaseModel):
    history: List[CycleOut]
    next_predicted_date: Optional[date] = None


# ---------- Community ----------

class TrendPoint(BaseModel):
    date: date
    symptom: str
    count: int


class RegionTrendPoint(BaseModel):
    region: str
    symptom: str
    count: int


class CommunityTrendsOut(BaseModel):
    trends: List[TrendPoint]
    outbreak_alert: bool
    region_trends: List[RegionTrendPoint] = []
    your_region_alert: bool = False


# ---------- Medications ----------

class MedicationIn(BaseModel):
    name: str


class MedicationOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MedicationWarning(BaseModel):
    drug_a: str
    drug_b: str
    warning: str


class MedicationListOut(BaseModel):
    medications: List[MedicationOut]
    warnings: List[MedicationWarning]


# ---------- Mental Health ----------

class MoodIn(BaseModel):
    date: date
    mood_score: int = Field(ge=1, le=5)
    note: Optional[str] = None


class MoodOut(BaseModel):
    date: date
    mood_score: int
    note: Optional[str] = None

    class Config:
        from_attributes = True


class MoodInsightOut(BaseModel):
    low_mood_alert: bool
    average_recent_score: Optional[float] = None
    message: str


# ---------- Festival / Season Tips ----------

class TipOut(BaseModel):
    title: str
    message: str


class TipsTodayOut(BaseModel):
    date: date
    tips: List[TipOut]


# ---------- Govt Scheme Suggestion ----------

class SchemeOut(BaseModel):
    condition: str
    scheme_name: str
    description: str


class SchemeListOut(BaseModel):
    condition: str
    schemes: List[SchemeOut]


# ---------- Chatbot ----------
# (defined last since it references SchemeOut above)

class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    reply: str
    severity: str  # "red" | "yellow" | "green"
    is_emergency: bool
    habit_note: Optional[str] = None
    scheme_suggestion: Optional[SchemeOut] = None