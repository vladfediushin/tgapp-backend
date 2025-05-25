# 1. schemas/user.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserOut(UserCreate):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


# 2. crud/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
import uuid
from datetime import datetime

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def create_or_update_user(db: AsyncSession, user_data: UserCreate):
    user = await get_user_by_telegram_id(db, user_data.telegram_id)
    if user:
        user.username = user_data.username
        user.first_name = user_data.first_name
        user.last_name = user_data.last_name
    else:
        user = User(
            id=uuid.uuid4(),
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            created_at=datetime.utcnow()
        )
        db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# 3. routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_or_update_user

router = APIRouter()

@router.post("/users/", response_model=UserOut)
async def register_or_update_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_or_update_user(db, user)


# 4. app/main.py — подключаем роут
from fastapi import FastAPI
from app.routers import users, questions

app = FastAPI()

app.include_router(questions.router)
