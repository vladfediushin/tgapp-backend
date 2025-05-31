# app/schemas/answer.py
from pydantic import BaseModel
from typing import Any
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