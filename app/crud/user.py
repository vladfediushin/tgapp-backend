# app/crud/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import User, Question, UserProgress
from app.schemas import UserCreate
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from uuid import UUID
from typing import Optional


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
    """
    Если пользователь с таким telegram_id есть — обновляем все поля,
    иначе создаём нового и сразу сохраняем все поля из Pydantic-схемы.
    """
    user = await get_user_by_telegram_id(db, user_data.telegram_id)

    if user:
        # Обновляем только те поля, что действительно пришли в запросе
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
    else:
        # Создаём нового пользователя — все требуемые поля уже в user_data
        user = User(
            **user_data.dict(),
            created_at=datetime.utcnow()
        )
        db.add(user)

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


from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models import Question, UserProgress

async def get_user_stats(db: AsyncSession, user_id: UUID) -> dict:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # total вопросов
    total_q_stmt = (
        select(func.count())
        .select_from(Question)
        .where(Question.country == user.exam_country)
        .where(Question.language == user.exam_language)
    )
    total_questions = (await db.execute(total_q_stmt)).scalar_one()

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
