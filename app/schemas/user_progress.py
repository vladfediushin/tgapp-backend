from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional



class UserProgressOut(BaseModel):
    id: UUID
    user_id: UUID
    question_id: UUID
    repetition_count: int
    is_correct: bool
    last_answered_at: datetime
    next_due_at: datetime

    class Config:
        orm_mode = True
