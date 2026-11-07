import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from .database import Base


def gen_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_demo = Column(Boolean, default=False)
    birth_date = Column(String, nullable=True)
    zodiac_sign = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    consultations = relationship("Consultation", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    important_dates = relationship("ImportantDate", back_populates="user")
    journey_events = relationship("JourneyEvent", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class Astrologer(Base):
    __tablename__ = "astrologers"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    bio = Column(Text, default="")
    experience_years = Column(Integer, default=5)
    rating = Column(Float, default=4.8)
    reviews_count = Column(Integer, default=120)
    price_per_session = Column(Integer, default=499)
    avatar_emoji = Column(String, default="\U0001F52E")
    languages = Column(JSON, default=list)

    consultations = relationship("Consultation", back_populates="astrologer")


class Consultation(Base):
    __tablename__ = "consultations"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    astrologer_id = Column(String, ForeignKey("astrologers.id"), nullable=False)
    topic = Column(String, default="Career")
    transcript = Column(Text, default="")
    status = Column(String, default="completed")  # scheduled | completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="consultations")
    astrologer = relationship("Astrologer", back_populates="consultations")
    insight = relationship("Insight", back_populates="consultation", uselist=False)


class Insight(Base):
    __tablename__ = "insights"
    id = Column(String, primary_key=True, default=gen_id)
    consultation_id = Column(String, ForeignKey("consultations.id"), nullable=False)
    summary = Column(Text, default="")
    key_points = Column(JSON, default=list)
    category = Column(String, default="Career")
    saved_to_memory = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    consultation = relationship("Consultation", back_populates="insight")


class Goal(Base):
    __tablename__ = "goals"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    insight_id = Column(String, ForeignKey("insights.id"), nullable=True)
    title = Column(String, nullable=False)
    category = Column(String, default="Career")
    description = Column(Text, default="")
    progress = Column(Integer, default=0)  # 0-100
    status = Column(String, default="active")  # active | completed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="goals")
    actions = relationship("Action", back_populates="goal", order_by="Action.order")


class Action(Base):
    __tablename__ = "actions"
    id = Column(String, primary_key=True, default=gen_id)
    goal_id = Column(String, ForeignKey("goals.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    is_completed = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    goal = relationship("Goal", back_populates="actions")


class ImportantDate(Base):
    __tablename__ = "important_dates"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)  # ISO date string
    description = Column(Text, default="")
    reminder_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="important_dates")


class JourneyEvent(Base):
    __tablename__ = "journey_events"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # consultation_completed | goal_created | action_completed | ...
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="journey_events")


class ShareCard(Base):
    __tablename__ = "share_cards"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    headline = Column(String, default="")
    stats = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="reminder")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
