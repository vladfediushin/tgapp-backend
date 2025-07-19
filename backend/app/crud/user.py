# app/crud/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text, distinct
from app.models import User, Question, UserProgress, AnswerHistory
from app.schemas import UserCreate, UserSettingsUpdate
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from datetime import date, datetime, timedelta
from uuid import UUID
from typing import Optional
from fastapi import HTTPException


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    q = select(User).where(User.id == user_id)
    result = await db.execute(q)
    return result.scalars().first()

async def create_or_update_user(
    db: AsyncSession,
    user_data: UserCreate
) -> User:
    user = await db.execute(select(User).where(User.telegram_id == user_data.telegram_id))
    user = user.scalar_one_or_none()

    if user:
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
    else:
        user = User(**user_data.dict(), created_at=datetime.utcnow())
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user

async def update_user_settings(
    db: AsyncSession,
    user_id: UUID,
    settings: UserSettingsUpdate
) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    # Обновляем только те поля, которые реально пришли (не None)
    for field, value in settings.dict(exclude_unset=True, exclude_none=True).items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: UUID, **fields) -> Optional[User]:
    # Разрешенные поля для обновления
    ALLOWED_FIELDS = {"first_name", "last_name", "exam_country", 
                      "exam_language", "ui_language"}
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    # Обновляем только разрешенные поля
    for field, value in fields.items():
        if field in ALLOWED_FIELDS:
            setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user


async def get_total_questions(db: AsyncSession, country: str, language: str) -> int:
    stmt = (
        select(func.count())
        .select_from(Question)
        .where(Question.country == country)
        .where(Question.language == language)
    )
    return (await db.execute(stmt)).scalar_one()

async def get_user_stats(db: AsyncSession, user_id: UUID) -> dict:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_questions = await get_total_questions(db, user.exam_country, user.exam_language)

    # answered — с JOIN на Question
    answered_stmt = (
        select(func.count())
        .select_from(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(UserProgress.user_id == user_id)
        .where(Question.country == user.exam_country)
        .where(Question.language == user.exam_language)
    )
    answered = (await db.execute(answered_stmt)).scalar_one()

    # correct — то же самое, плюс is_correct=True
    correct_stmt = (
        select(func.count())
        .select_from(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(UserProgress.user_id == user_id)
        .where(UserProgress.is_correct.is_(True))
        .where(Question.country == user.exam_country)
        .where(Question.language == user.exam_language)
    )
    correct = (await db.execute(correct_stmt)).scalar_one()
    
    # FSRS статистика (если есть FSRS данные)
    fsrs_stats = await get_fsrs_stats_for_user(db, user_id, user.exam_country, user.exam_language)

    return {
        "total_questions": total_questions,
        "answered": answered,
        "correct": correct,
        # FSRS дополнения
        "fsrs_enabled": fsrs_stats["has_fsrs_data"],
        "avg_retention": fsrs_stats["avg_retention"],
        "cards_due_today": fsrs_stats["due_today"],
        "cards_learning": fsrs_stats["learning"],
        "cards_review": fsrs_stats["review"],
    }


async def get_fsrs_stats_for_user(db: AsyncSession, user_id: UUID, country: str, language: str) -> dict:
    """Получает FSRS статистику для пользователя"""
    
    now = datetime.now()
    
    # Проверяем есть ли FSRS данные у пользователя
    fsrs_check_stmt = (
        select(func.count())
        .select_from(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(
            UserProgress.user_id == user_id,
            Question.country == country,
            Question.language == language,
            UserProgress.stability.isnot(None)  # Есть FSRS данные
        )
    )
    fsrs_count = (await db.execute(fsrs_check_stmt)).scalar_one()
    
    if fsrs_count == 0:
        return {
            "has_fsrs_data": False,
            "avg_retention": None,
            "due_today": None,
            "learning": None,
            "review": None
        }
    
    # Получаем FSRS статистику одним запросом
    fsrs_stats_stmt = (
        select(
            func.avg(UserProgress.stability).label('avg_stability'),
            func.count().filter(
                and_(
                    UserProgress.due <= now,
                    UserProgress.state.in_([1, 2, 3])  # Learning, Review, Relearning
                )
            ).label('due_today'),
            func.count().filter(UserProgress.state == 1).label('learning'),
            func.count().filter(UserProgress.state == 2).label('review'),
        )
        .select_from(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(
            UserProgress.user_id == user_id,
            Question.country == country,
            Question.language == language,
            UserProgress.stability.isnot(None)
        )
    )
    
    result = (await db.execute(fsrs_stats_stmt)).first()
    
    # Конвертируем stability в retention (приблизительно)
    avg_retention = None
    if result.avg_stability:
        # Простая формула: retention = stability / (stability + 1)
        avg_retention = result.avg_stability / (result.avg_stability + 1)
    
    return {
        "has_fsrs_data": True,
        "avg_retention": avg_retention,
        "due_today": result.due_today or 0,
        "learning": result.learning or 0,
        "review": result.review or 0
    }


async def get_daily_progress(
    db: AsyncSession, 
    user_id: UUID, 
    target_date: date = None
) -> dict:
    """
    Простой и быстрый подсчет дневного прогресса.
    """
    
    if target_date is None:
        target_date = date.today()
    
    # Границы дня
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = day_start + timedelta(days=1)
    
    # Получаем пользователя с дневной целью
    user_result = await db.execute(
        select(User.daily_goal).where(User.id == user_id)
    )
    user_data = user_result.first()
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    daily_goal = user_data.daily_goal or 30
    
    # Простой подсчет новых правильных ответов за день
    progress_result = await db.execute(
        select(func.count(distinct(UserProgress.question_id)))
        .where(
            UserProgress.user_id == user_id,
            UserProgress.is_correct == True,
            UserProgress.last_answered_at >= day_start,
            UserProgress.last_answered_at < day_end
        )
    )
    
    questions_mastered_today = progress_result.scalar() or 0

    return {
        "questions_mastered_today": questions_mastered_today,
        "date": target_date,
        "daily_goal": daily_goal
    }