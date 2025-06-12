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
      - 'interval'   : интервальные вопросы (next_due_at <= now)
      - 'all'        : все вопросы
      - 'new_only'   : только новые (без прогресса)
      - 'errors_only': только ошибочные (is_correct=False)
    """
    # Выбор логики по режиму
    if mode == 'interval':
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
        
    elif mode == 'all':
        # TODO: вернуть все вопросы, без учета due date и прогресса
        # stmt = select(Question)
        # .where(Question.country == country, Question.language == language)
        raise NotImplementedError("Mode 'all' not implemented yet")
    elif mode == 'new_only':
        # TODO: вернуть только новые вопросы, у которых нет записи в UserProgress для user_id
        # stmt = select(Question)
        # .outerjoin(UserProgress)
        # .where(UserProgress.user_id == user_id, UserProgress.id == None)
        raise NotImplementedError("Mode 'new_only' not implemented yet")
    elif mode == 'errors_only':
        # TODO: вернуть только вопросы с неверным ответом (is_correct=False)
        # stmt = select(Question)
        # .join(UserProgress)
        # .where(UserProgress.user_id == user_id, UserProgress.is_correct == False)
        raise NotImplementedError("Mode 'errors_only' not implemented yet")
    else:
        # Неизвестный режим: по умолчанию интервальные
        stmt = (
            select(Question)
            .join(UserProgress, Question.id == UserProgress.question_id)
            .where(UserProgress.user_id == user_id)
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

    result = await db.execute(random_stmt)
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