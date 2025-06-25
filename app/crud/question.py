from sqlalchemy.future import select
from sqlalchemy import func, distinct, case
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException

from app.models import Question
from app.models import UserProgress

async def fetch_questions_for_user(
    db: AsyncSession,
    user_id: UUID,
    country: str,
    language: str,
    mode: str,
    batch_size: int,
    topics: Optional[List[str]] = None,
) -> List[Question]:
    country = country.lower()
    language = language.lower()
    if mode == 'topics' and not topics:
        mode = 'interval_all'

    if mode == 'interval_all':
        # Интервальные вопросы
        stmt = (
            select(Question)
            .outerjoin(
                UserProgress,
                (Question.id == UserProgress.question_id)
                & (UserProgress.user_id == user_id)
            )
            .where(
                (UserProgress.next_due_at <= datetime.utcnow())
                | (UserProgress.user_id == None)
            )
        )
    elif mode == 'new_only':
        # Только новые
        stmt = (
            select(Question)
            .outerjoin(
                UserProgress,
                (Question.id == UserProgress.question_id)
                & (UserProgress.user_id == user_id)
            )
            .where(UserProgress.user_id == None)
        )
    elif mode == 'shown_before':
        # Только некорректно отвеченные
        stmt = (
            select(Question)
            .join(
                UserProgress,
                (Question.id == UserProgress.question_id)
                & (UserProgress.user_id == user_id)
            )
            .where(UserProgress.is_correct == False)
        )
    elif mode == 'topics':
        # Любые вопросы из указанных тем, но с JOIN, чтобы можно было сортировать по профилю
        stmt = (
            select(Question)
            .outerjoin(
                UserProgress,
                (Question.id == UserProgress.question_id)
                & (UserProgress.user_id == user_id)
            )
        )
    else:
        raise HTTPException(400, f"Unsupported mode '{mode}'")

    # Фильтрация по стране, языку и (опционально) темам
    stmt = stmt.where(Question.country == country)
    stmt = stmt.where(Question.language == language)
    if topics:
        stmt = stmt.where(Question.topic.in_(topics))

    # Сортировка и LIMIT
    if mode in ('interval_all', 'topics'):
        # Сначала вопросы с is_correct=False, потом случайно
        priority = case(
            [(UserProgress.is_correct == False, 0)],
            else_=1
        )
        stmt = stmt.order_by(priority, func.random()).limit(batch_size)
    else:
        stmt = stmt.order_by(func.random()).limit(batch_size)

    result = await db.execute(stmt)
    return result.scalars().all()

# Функции для получения доступных стран и языков в самом начале сессии
async def get_distinct_countries(db: AsyncSession) -> List[str]:
    q = select(distinct(Question.country))
    result = await db.execute(q)
    return [row[0] for row in result.fetchall() if row[0] is not None]

async def get_distinct_languages(db: AsyncSession) -> List[str]:
    q = select(distinct(Question.language))
    result = await db.execute(q)
    return [row[0] for row in result.fetchall() if row[0] is not None]

# Получаем список тем для юзера
async def fetch_topics(db: AsyncSession, country: str, language: str) -> list[str]:
    q = await db.execute(
        select(distinct(Question.topic))
          .where(Question.country == country)
          .where(Question.language == language)
    )
    return [row[0] for row in q.all()]