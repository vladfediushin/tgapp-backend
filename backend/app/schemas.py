# app/schemas.py - Fixed version
from pydantic import BaseModel, Field, constr
from typing import Any, Optional, List
from uuid import UUID
from datetime import datetime, date

class AnswerSubmit(BaseModel):
    """Схема для отдельного ответа с user_id (для внутреннего использования)"""
    user_id: UUID
    question_id: int
    is_correct: bool
    timestamp: Optional[int] = None
    response_time: Optional[int] = None  # Время ответа в миллисекундах для FSRS
    difficulty_rating: Optional[int] = Field(None, ge=1, le=4, description="FSRS rating: 1=Again, 2=Hard, 3=Good, 4=Easy")

class BatchAnswerItem(BaseModel):
    """Ответ в batch запросе без user_id (user_id берется из URL)"""
    question_id: int
    is_correct: bool
    timestamp: Optional[int] = None
    response_time: Optional[int] = None  # Время ответа в миллисекундах для FSRS
    difficulty_rating: Optional[int] = Field(None, ge=1, le=4, description="FSRS rating: 1=Again, 2=Hard, 3=Good, 4=Easy")

class BatchAnswersSubmit(BaseModel):
    """Batch запрос ответов - user_id берется из URL параметра"""
    answers: List[BatchAnswerItem]
    
    class Config:
        json_schema_extra = {
            "example": {
                "answers": [
                    {
                        "question_id": 123,
                        "is_correct": True,
                        "timestamp": 1640995200000
                    }
                ]
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
    # FSRS дополнения
    fsrs_enabled: Optional[bool] = False
    avg_retention: Optional[float] = None
    cards_due_today: Optional[int] = None
    cards_learning: Optional[int] = None
    cards_review: Optional[int] = None

class UserProgressOut(BaseModel):
    id: UUID
    user_id: UUID
    question_id: int
    is_correct: bool
    last_answered_at: datetime
    # FSRS fields
    stability: float
    difficulty: float
    retrievability: float
    state: int
    reps: int
    lapses: int
    due: datetime

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
        json_schema_extra = {
            "example": {
                "questions_mastered_today": 5,
                "date": "2025-07-09"
            }
        }

# FSRS-specific schemas
class FSRSCardStats(BaseModel):
    """FSRS статистика для конкретной карточки"""
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    retrievability: Optional[float] = None
    state: Optional[int] = None  # 0=New, 1=Learning, 2=Review, 3=Relearning
    reps: Optional[int] = None
    lapses: Optional[int] = None
    due: Optional[datetime] = None

class UserProgressWithFSRS(BaseModel):
    """Расширенный прогресс с FSRS данными"""
    id: UUID
    user_id: UUID
    question_id: int
    is_correct: bool
    last_answered_at: datetime
    # FSRS fields
    stability: float
    difficulty: float
    retrievability: float
    state: int
    reps: int
    lapses: int
    due: datetime

    class Config:
        from_attributes = True

class BatchAnswersSubmitWithFSRS(BaseModel):
    """Batch запрос с опциональной FSRS поддержкой"""
    answers: List[BatchAnswerItem]
    use_fsrs: Optional[bool] = False  # Feature flag
    
    class Config:
        json_schema_extra = {
            "example": {
                "answers": [
                    {
                        "question_id": 123,
                        "is_correct": True,
                        "timestamp": 1640995200000,
                        "response_time": 3500,
                        "difficulty_rating": 3
                    }
                ],
                "use_fsrs": True
            }
        }