from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.database import get_db
from app.schemas.answer import AnswerSubmit
from app.schemas.user_progress import UserProgressOut
from app.crud import user_progress as crud_progress

router = APIRouter(
    prefix="/user_progress",
    tags=["user_progress"],
)


@router.post("/submit_answer", 
             response_model=UserProgressOut,
             status_code=status.HTTP_201_CREATED)
async def save_user_progress(
    progress_data: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
):
    """
    Принимает JSON AnswerSubmit, делает upsert в UserProgress.
    Возвращает готовый UserProgressOut (после сохранения).
    """
    try:
        progress = await crud_progress.create_or_update_progress(db, progress_data)
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
это мы допишем потом
"""
@router.get("/get_for_user", 
            response_model=UserProgressOut)
async def get_user_progress(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    list = await crud_progress.get_progress_for_user(db, user_id)
    return progress
