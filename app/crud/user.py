# app/crud/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.exc import NoResultFound
from datetime import datetime


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()


async def create_or_update_user(db: AsyncSession, user_data: UserCreate):
    user = await get_user_by_telegram_id(db, user_data.telegram_id)

    if user:
        # Обновим, если нужно
        user.username = user_data.username
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
    else:
        # Создадим нового
        user = User(**user_data.dict(), created_at=datetime.utcnow())
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user
