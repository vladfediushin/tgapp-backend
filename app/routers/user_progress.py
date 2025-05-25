from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.schemas.user_progress import UserProgressCreate, UserProgressOut
from app.crud import user_progress as crud_progress

router = APIRouter(
    prefix="/user_progress",
    tags=["user_progress"],
)


@router.post("/", response_model=UserProgressOut)
async def save_user_progress(
    progress_data: UserProgressCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        progress = await crud_progress.create_or_update_progress(db, progress_data)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[UserProgressOut])
async def get_user_progress(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    progress = await crud_progress.get_progress_for_user(db, user_id)
    return progress
