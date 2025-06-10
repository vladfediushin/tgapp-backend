from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, Boolean, DateTime, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid



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

    repetition_count = Column(Integer, default=0, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    last_answered_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    next_due_at = Column(DateTime(timezone=True), nullable=True)

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
    user_progress = relationship(
        "UserProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )