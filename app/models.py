"""
SQLAlchemy ORM models — one class per table.
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    gender = Column(String, nullable=False)  # "Male" | "Female" | "Other"
    age = Column(Integer, nullable=False)
    region = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    habit_logs = relationship("HabitLog", back_populates="user", cascade="all, delete-orphan")
    cycle_logs = relationship("CycleLog", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan")
    mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    sleep_hours = Column(Float, default=0)
    water_liters = Column(Float, default=0)
    steps = Column(Integer, default=0)
    score = Column(Float, default=0)  # computed health score for that day

    user = relationship("User", back_populates="habit_logs")


class CycleLog(Base):
    __tablename__ = "cycle_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="cycle_logs")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    reply = Column(Text, nullable=False)
    severity = Column(String, nullable=True)  # "red" | "yellow" | "green"
    is_emergency = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_messages")


class SymptomEntry(Base):
    """
    A lightweight log of detected symptoms per user, used by the
    Community Pulse aggregation endpoint. Written whenever the chatbot
    detects a symptom during a conversation.
    """
    __tablename__ = "symptom_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    region = Column(String, nullable=True)
    symptom = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Medication(Base):
    """A medicine the user has told us they are taking."""
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="medications")


class MoodLog(Base):
    """Daily mood check-in entry, upserted per user per date."""
    __tablename__ = "mood_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    mood_score = Column(Integer, nullable=False)  # 1 (very low) - 5 (very good)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="mood_logs")