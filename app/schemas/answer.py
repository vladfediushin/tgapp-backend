# backend/app/schemas/answer.py
from pydantic import BaseModel
from datetime import datetime

class AnswerSubmit(BaseModel):
    user_id: int
    question_id: int
    selected_index: int
    is_correct: bool
    timestamp: datetime = datetime.utcnow()