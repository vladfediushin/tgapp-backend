from pydantic import BaseModel, Field
from typing import Any, Optional
from uuid import UUID
from datetime import datetime

class AnswerSubmit(BaseModel):
    user_id: UUID
    question_id: int
    is_correct: bool

    class Config:
        schema_extra = {
            "example": {
                "user_id": "e759a0f2-e50c-407b-a263-a0d5f7ed5a6f",
                "question_id": "3f58c6ea-29d4-4c9c-8bd7-0c8fa472d0b2",
                "is_correct": True
            }
        }


class QuestionOut(BaseModel):
    id: int
    data: Any
    topic: str
    country: str
    language: str

    class Config:
        orm_mode = True



class UserStats(BaseModel):
    user_id: int
    answered: int
    correct: int
    total_questions: int
   
    class Config:
        orm_mode = True


class UserProgressOut(BaseModel):
    id: UUID
    user_id: UUID
    question_id: int
    repetition_count: int
    is_correct: bool
    last_answered_at: datetime
    next_due_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserOut(UserCreate):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True