# app/crud/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.schemas import UserCreate
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from uuid import UUID
from typing import Optional


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
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
