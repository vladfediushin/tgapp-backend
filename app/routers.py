import logging
logger = logging.getLogger("api")

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import QuestionOut, AnswerSubmit, UserProgressOut, UserCreate, UserOut, TopicsOut, UserStatsOut
from app.crud.question import fetch_questions_for_user, get_distinct_countries, get_distinct_languages, fetch_topics
from app.crud import user_progress as crud_progress
from app.crud import user as crud_user

PREFIX = ""

questions_router = APIRouter(
    prefix=f"{PREFIX}/questions",
    tags=["questions"])

@questions_router.get("/countries", response_model=List[str])
async def list_countries(db: AsyncSession = Depends(get_db)):
    return await get_distinct_countries(db)

@questions_router.get("/languages", response_model=List[str])
async def list_languages(db: AsyncSession = Depends(get_db)):
    return await get_distinct_languages(db)

@questions_router.get("/", response_model=List[QuestionOut])
async def get_questions(
    user_id: UUID = Query(
        ...,
        description="Internal user UUID (внутренний идентификатор пользователя)"
    ),
    mode: str = Query(
        ...,
        description="Mode of questions: interval_all, all, new_only, shown_before"
    ),
    country: str = Query(
        ...,
        description="Exam country code, e.g. 'am', 'ru'"
    ),
    language: str = Query(
        ...,
        description="Exam language code, e.g. 'ru', 'en'"
    ),
    topic: Optional[str] = Query(
        None,
        description="Optional topic filter"
    ),
    batch_size: int = Query(
        30, ge=1, le=50
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает список вопросов для данного пользователя с учётом режима и фильтров.
    Поддерживаемые режимы:
      - interval_all: интервальные вопросы (next_due_at <= now)
      - all: все вопросы
      - new_only: только новые вопросы
      - shown_before: показанные прежде вопросы
    """
    user = await crud_user.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await fetch_questions_for_user(
        db=db,
        user_id=user_id,
        country=user.exam_country,
        language=user.exam_language,
        mode=mode,
        batch_size=batch_size,
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

@users_router.get("/{user_id}/stats", response_model = UserStatsOut)
async def user_stats(user_id: UUID, db: AsyncSession = Depends(get_db)):
    stats = await crud_user.get_user_stats(db, user_id)
    if "detail" in stats:               # пользователь не найден
        raise HTTPException(status_code=404, detail=stats["detail"])
    return stats

@users_router.post("/", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    print(f"[DEBUG] Получен пользователь: {user.telegram_id}, {user.username}")
    return await crud_user.create_or_update_user(db, user)


@users_router.get("/by-telegram-id/{telegram_id}", response_model=UserOut)
async def get_user_by_telegram_id_endpoint(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get_user_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@users_router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
)
async def update_user_profile(
    user_id: UUID,
    fields: dict[str, str],  # или: UserUpdate, если введёте соответствующую Pydantic-схему
    db: AsyncSession = Depends(get_db),
):
    """
    Поля fields могут содержать exam_country и/или exam_language.
    """
    user = await crud_user.update_user(db, user_id, **fields)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


topics_router = APIRouter(tags=["topics"])

@topics_router.get("/topics", response_model=TopicsOut)
async def get_topics(
    country: str = Query(..., description="Country code, e.g. AM"),
    language: str = Query(..., description="Language code, e.g. ru"),
    db: AsyncSession = Depends(get_db),
):
    topics = await fetch_topics(db, country, language)
    return TopicsOut(topics=topics)

