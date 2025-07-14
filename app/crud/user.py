# app/crud/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
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

    return {
        "total_questions": total_questions,
        "answered": answered,
        "correct": correct,
    }


async def get_daily_progress(
    db: AsyncSession, 
    user_id: UUID, 
    target_date: date = None
) -> dict:
    """
    Оптимизированный подсчет вопросов, изученных за день.
    Использует один запрос вместо N+1.
    """
    
    if target_date is None:
        target_date = date.today()
    
    # Границы дня
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = day_start + timedelta(days=1)
    
    user = await get_user_by_id(db, user_id)
    if not user:
        return {"questions_mastered_today": 0, "date": target_date}
    
    # Оптимизированный запрос с использованием window functions
    # Получаем все ответы пользователя, упорядоченные по времени
    query = """
    WITH question_progress AS (
        SELECT 
            question_id,
            is_correct,
            answered_at,
            ROW_NUMBER() OVER (
                PARTITION BY question_id 
                ORDER BY answered_at DESC
            ) as rn_overall,
            ROW_NUMBER() OVER (
                PARTITION BY question_id 
                ORDER BY answered_at DESC
            ) FILTER (WHERE answered_at < :day_start) as rn_before_today,
            CASE 
                WHEN answered_at >= :day_start AND answered_at < :day_end 
                THEN ROW_NUMBER() OVER (
                    PARTITION BY question_id 
                    ORDER BY answered_at ASC
                ) FILTER (WHERE answered_at >= :day_start AND answered_at < :day_end AND is_correct = true)
                ELSE NULL
            END as first_correct_today
        FROM answer_history 
        WHERE user_id = :user_id
    ),
    mastered_today AS (
        SELECT DISTINCT question_id
        FROM question_progress
        WHERE first_correct_today = 1  -- Первый правильный ответ сегодня
        AND (
            rn_before_today IS NULL  -- Никогда не отвечал раньше
            OR EXISTS (  -- Или последний ответ до сегодня был неправильным
                SELECT 1 FROM question_progress qp2 
                WHERE qp2.question_id = question_progress.question_id 
                AND qp2.rn_before_today = 1 
                AND qp2.is_correct = false
            )
        )
    )
    SELECT COUNT(*) as mastered_count FROM mastered_today
    """
    
    result = await db.execute(
        text(query),
        {
            "user_id": user_id,
            "day_start": day_start,
            "day_end": day_end
        }
    )
    
    mastered_count = result.scalar() or 0
    
    return {
        "questions_mastered_today": mastered_count,
        "date": target_date
    }