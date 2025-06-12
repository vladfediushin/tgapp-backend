from sqlalchemy.future import select
from sqlalchemy import distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.models import Question
from app.models import UserProgress

async def fetch_questions_for_user(
    db: AsyncSession,
    user_id: UUID,
    country: str,
    language: str,
    mode: str,
    batch_size: int,
    topic: Optional[str] = None,
) -> List[Question]:
    """
    Возвращает список вопросов для пользователя по заданным параметрам.
    mode может быть:
      - 'interval_all'   : интервальные вопросы (next_due_at <= now)
      - 'all'        : все вопросы
      - 'new_only'   : только новые (без прогресса)
      - 'shown_before': только ошибочные (is_correct=False)
    """
    if mode == 'interval_all':
        stmt = (
            select(Question)
            .outerjoin(UserProgress,
                (Question.id == UserProgress.question_id)
                &(UserProgress.user_id == user_id))
            .where(
                ((UserProgress.next_due_at <= datetime.utcnow())
                 | (UserProgress.user_id == None))
            )
            )
        
    elif mode == 'new_only':
        stmt = (
            select(Question)
            .outerjoin(
                UserProgress,
                (Question.id == UserProgress.question_id)
                & (UserProgress.user_id == user_id)
            )
            .where(UserProgress.question_id == None)
        )
    
    elif mode == 'shown_before':
        stmt = (
            select(Question)
            .join(
                UserProgress,
                (Question.id == UserProgress.question_id)
                & (UserProgress.user_id == user_id)
            )
            .where(
                (UserProgress.next_due_at <= datetime.utcnow())
                | (UserProgress.next_due_at == None)
            )
        )

    # Применяем общие фильтры: страна и язык
    stmt = stmt.where(Question.country == country)
    stmt = stmt.where(Question.language == language)

    # Опциональный фильтр по теме
    if topic:
        stmt = stmt.where(Question.topic == topic)

    stmt = (
        stmt
        .order_by(func.random())
        .limit(batch_size)
    )

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