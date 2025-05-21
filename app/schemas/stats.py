# backend/app/schemas/stats.py
from pydantic import BaseModel

class UserStats(BaseModel):
    user_id: int
    answered: int
    correct: int
    total_questions: int