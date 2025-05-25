from sqlalchemy import Column, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base

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
