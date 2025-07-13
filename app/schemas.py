# app/schemas.py - Fixed version
from pydantic import BaseModel, Field, constr
from typing import Any, Optional
from uuid import UUID
from datetime import datetime, date

class AnswerSubmit(BaseModel):
    user_id: UUID
    question_id: int
    is_correct: bool

    class Config:
        schema_extra = {
            "example": {
                "user_id": "e759a0f2-e50c-407b-a263-a0d5f7ed5a6f",
                "question_id": 123,
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
        from_attributes = True

class UserStatsOut(BaseModel):
    total_questions: int
    answered: int
    correct: int

class UserProgressOut(BaseModel):
    id: UUID
    user_id: UUID
    question_id: int
    repetition_count: int
    is_correct: bool
    last_answered_at: datetime
    next_due_at: datetime

    class Config:
        from_attributes = True

# Fixed UserCreate schema - made exam_date and daily_goal optional
class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    exam_country: constr(min_length=2, max_length=2)
    exam_language: constr(min_length=2, max_length=2)
    ui_language: constr(min_length=2, max_length=2)  # Fixed typo from ui_langugage
    exam_date: Optional[date] = None  # Made optional
    daily_goal: Optional[int] = None  # Made optional

# Fixed UserSettingsUpdate - made exam_date and daily_goal optional
class UserSettingsUpdate(BaseModel):
    exam_country: Optional[constr(min_length=2, max_length=2)] = None
    exam_language: Optional[constr(min_length=2, max_length=2)] = None
    ui_language: Optional[constr(min_length=2, max_length=2)] = None
    exam_date: Optional[date] = None  
    daily_goal: Optional[int] = None 

class UserOut(BaseModel):
    id: UUID
    created_at: datetime
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    exam_country: Optional[str] = None  # Made optional for backward compatibility
    exam_language: Optional[str] = None  # Made optional for backward compatibility
    ui_language: Optional[str] = None  # Made optional for backward compatibility
    exam_date: Optional[date] = None
    daily_goal: Optional[int] = None

    class Config:
        from_attributes = True

class TopicsOut(BaseModel):
    topics: list[str]

# New schemas for exam settings management
class ExamSettingsUpdate(BaseModel):
    exam_date: date = Field(..., description="Target exam date")
    daily_goal: int = Field(..., ge=1, le=100, description="Daily questions goal (1-100)")

class ExamSettingsResponse(BaseModel):
    exam_date: Optional[date] = None
    daily_goal: Optional[int] = None
    days_until_exam: Optional[int] = None
    recommended_daily_goal: Optional[int] = None

class DailyProgressOut(BaseModel):
    questions_mastered_today: int
    date: date

    class Config:
        schema_extra = {
            "example": {
                "questions_mastered_today": 5,
                "date": "2025-07-09"
            }
        }