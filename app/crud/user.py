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
    Использует один SQL запрос для максимальной производительности.
    """
    
    if target_date is None:
        target_date = date.today()
    
    # Границы дня
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = day_start + timedelta(days=1)
    
    # Оптимизированный запрос - один SQL вместо множественных запросов
    query = text("""
        SELECT
            COALESCE(u.daily_goal, 30) AS daily_goal,
            COUNT(*) AS questions_mastered_today,
            :target_date AS date
        FROM (
            SELECT DISTINCT ah1.question_id
            FROM answer_history ah1
            WHERE ah1.user_id = :user_id
              AND ah1.is_correct = TRUE
              AND ah1.answered_at >= :start_time
              AND ah1.answered_at < :end_time
              AND NOT EXISTS (
                  SELECT 1
                  FROM answer_history ah2
                  WHERE ah2.user_id = ah1.user_id
                    AND ah2.question_id = ah1.question_id
                    AND ah2.is_correct = TRUE
                    AND ah2.answered_at < :start_time
              )
        ) newly_mastered
        CROSS JOIN users u 
        WHERE u.id = :user_id
    """)

    result = await db.execute(query, {
        "user_id": user_id,
        "target_date": target_date.isoformat(),
        "start_time": day_start,
        "end_time": day_end
    })
    
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "questions_mastered_today": row.questions_mastered_today,
        "date": target_date,
        "daily_goal": row.daily_goal
    }