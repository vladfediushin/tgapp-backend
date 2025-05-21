# backend/app/routers/stats.py
from fastapi import APIRouter, Query
from app.schemas.stats import UserStats
from app.routers.answers import answers_log

router = APIRouter()

@router.get("/stats", response_model=UserStats)
def get_user_stats(user_id: int = Query(...)):
    user_answers = [a for a in answers_log if a.user_id == user_id]
    total = len(user_answers)
    correct = sum(1 for a in user_answers if a.is_correct)

    return UserStats(
        user_id=user_id,
        answered=total,
        correct=correct,
        total_questions=50  # пока просто заглушка
    )