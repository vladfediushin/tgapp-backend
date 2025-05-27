from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserOut
from app.crud import user as crud_user

router = APIRouter()

@router.post("/users/", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    print(f"[DEBUG] Получен пользователь: {user.telegram_id}, {user.username}")
    return await crud_user.create_or_update_user(db, user)
