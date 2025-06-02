from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import QuestionOut, AnswerSubmit, UserProgressOut, UserCreate, UserOut, UserStats
from app.crud.question import fetch_questions_for_user
from app.crud import user_progress as crud_progress
from app.crud import user as crud_user

PREFIX = ""

questions_router = APIRouter(
    prefix=f"{PREFIX}/questions",
    tags=["questions"],
)

@questions_router.get("/", response_model=List[QuestionOut])
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



user_progress_router = APIRouter(
    prefix=f"{PREFIX}/user_progress",
    tags=["user_progress"],
)


@user_progress_router.post(
        "/submit_answer", 
        response_model=UserProgressOut,
        status_code=status.HTTP_201_CREATED)
async def save_user_progress(
    progress_data: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
):
    """
    Принимает JSON AnswerSubmit, делает upsert в UserProgress.
    Возвращает готовый UserProgressOut (после сохранения).
    """
    try:
        progress = await crud_progress.create_or_update_progress(db, progress_data)
        return progress
    except Exception as e:
        import traceback, sys
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"[save_user_progress] Unhandled exception:\n{tb}")
        # Возвращаем HTTP 500 с кратким сообщением
        raise HTTPException(status_code=500, detail="Internal server error, see logs for details")

"""
это мы допишем потом
"""
@user_progress_router.get(
        "/get_user_stats", 
        response_model=UserProgressOut)
async def get_user_progress(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    progress = await crud_progress.get_progress_for_user(db, user_id)
    return progress

users_router = APIRouter(
    prefix=f"{PREFIX}/users",
    tags=["users"],
)

@users_router.post("/", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    print(f"[DEBUG] Получен пользователь: {user.telegram_id}, {user.username}")
    return await crud_user.create_or_update_user(db, user)





"""
stats_router = APIRouter(
    prefix=f"{PREFIX}",
    tags=["statistics"],
) # оставить на потом, мб использовать просто user_progress_router?

@stats_router.get("/", response_model=UserStats)
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

    """