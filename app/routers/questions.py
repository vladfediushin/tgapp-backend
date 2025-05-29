# app/routers/questions.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.question import QuestionOut
from app.crud.question import fetch_questions_for_user

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/", response_model=List[QuestionOut])
async def get_questions(
    user_id: str = Query(..., description="User ID from Telegram WebApp"),
    country: str = Query(..., description="Country code, e.g. AM"),
    language: str = Query(..., description="Language code, e.g. ru"),
    mode: str = Query(..., description="Mode of questions: interval, all, new_only, errors_only"),
    topic: Optional[str] = Query(None, description="Optional topic filter"),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает список вопросов для данного пользователя с учётом режима и фильтров.
    Поддерживаемые режимы:
      - interval: интервальные вопросы (next_due_at <= now)
      - all: все вопросы
      - new_only: только новые вопросы
      - errors_only: только неверные ответы
    """
    return await fetch_questions_for_user(
        db=db,
        user_id=user_id,
        country=country,
        language=language,
        mode=mode,
        topic=topic,
    )