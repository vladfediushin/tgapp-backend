from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserProgressCreate(BaseModel):
    user_id: UUID
    question_id: int
    is_correct: bool
    country: str
    language: str

    class Config:
        orm_mode = True


class UserProgressOut(BaseModel):
    id: UUID
    user_id: UUID
    question_id: int
    repetition_count: int
    is_correct: Optional[bool]
    last_answered_at: Optional[datetime]
    next_due_at: Optional[datetime]
    country: str
    language: str

    class Config:
        orm_mode = True
