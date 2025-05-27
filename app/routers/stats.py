# backend/app/routers/stats.py

# оставить на потом


from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user_progress import UserProgress
from app.models.user import User
from pydantic import BaseModel


router = APIRouter(tags=["Statistics"])

@router.get("/stats", response_model=UserStats)
def get_user_stats(user_id: int = Query(...)):
    user_answers = [a for a in answers_log if a.user_id == user_id]
    total = len(user_answers)
    correct = sum(1 for a in user_answers if a.is_correct)

    return UserStats(
        user_id=user_id,
        answered=total,
        correct=correct,
        total_questions=total
    )