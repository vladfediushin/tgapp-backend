from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Boolean, DateTime, Text, ForeignKey, JSON, BigInteger, Date, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid


class AnswerHistory(Base):
    __tablename__ = "answer_history"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # FIXED: Added ForeignKey
    question_id = Column(Integer, nullable=False)  # Note: No FK to questions since you removed it
    is_correct  = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="answer_history")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON, nullable=False)
    topic = Column(Text, nullable=False)
    country = Column(Text, nullable=False)
    language = Column(Text, nullable=False)

    user_progress = relationship("UserProgress", back_populates="question")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    # Answer tracking
    is_correct = Column(Boolean, nullable=False)
    last_answered_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # FSRS fields
    stability = Column(Float, nullable=True)        # S - stability (interval when R=90%)
    difficulty = Column(Float, nullable=True)       # D - difficulty [1-10]
    retrievability = Column(Float, nullable=True)   # R - probability of recall
    elapsed_days = Column(Integer, default=0)       # Days since last review
    scheduled_days = Column(Integer, default=0)     # Scheduled interval
    reps = Column(Integer, default=0)               # Number of repetitions
    lapses = Column(Integer, default=0)             # Number of lapses (forgetting)
    state = Column(Integer, default=0)              # 0=New, 1=Learning, 2=Review, 3=Relearning
    last_review = Column(DateTime(timezone=True), nullable=True)  # FSRS last review time
    due = Column(DateTime(timezone=True), nullable=True)          # FSRS due time

    user = relationship("User", back_populates="user_progress")
    question = relationship("Question", back_populates="user_progress")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    exam_country = Column(Text)
    exam_language = Column(Text)
    ui_language = Column(Text)
    exam_date = Column(Date, nullable=True)  # FIXED: Made nullable for optional feature
    daily_goal = Column(Integer, nullable=True)  # FIXED: Made nullable for optional feature
    
    user_progress = relationship(
        "UserProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    answer_history = relationship(
        "AnswerHistory", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )