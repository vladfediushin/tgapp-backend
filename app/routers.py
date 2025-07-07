# app/routers.py - Fixed version with exam settings
import logging
from datetime import date, datetime
logger = logging.getLogger("api")

from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    QuestionOut, AnswerSubmit, UserProgressOut, UserCreate, UserOut, 
    TopicsOut, UserStatsOut, UserSettingsUpdate, ExamSettingsUpdate, ExamSettingsResponse
)
from app.crud.question import fetch_questions_for_user, get_distinct_countries, get_distinct_languages, fetch_topics
from app.crud import user_progress as crud_progress
from app.crud import user as crud_user

PREFIX = ""

questions_router = APIRouter(
    prefix=f"{PREFIX}/questions",
    tags=["questions"])

@questions_router.get("/countries", response_model=List[str])
async def list_countries(db: AsyncSession = Depends(get_db)):
    return await get_distinct_countries(db)

@questions_router.get("/languages", response_model=List[str])
async def list_languages(db: AsyncSession = Depends(get_db)):
    return await get_distinct_languages(db)

@questions_router.get("/", response_model=List[QuestionOut])
async def get_questions(
    user_id: UUID = Query(..., description="Internal user UUID"),
    mode: str = Query(..., description="Mode: interval_all, new_only, shown_before, topics"),
    country: str = Query(..., description="Exam country code"),
    language: str = Query(..., description="Exam language code"),
    topics: Optional[List[str]] = Query(None, alias="topic", description="Optional topic filter"),
    batch_size: int = Query(30, ge=1, le=50, description="Number of questions to fetch"),
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return await fetch_questions_for_user(
        db=db,
        user_id=user_id,
        country=user.exam_country or country,
        language=user.exam_language or language,
        mode=mode,
        batch_size=batch_size,
        topics=topics,
    )

user_progress_router = APIRouter(
    prefix=f"{PREFIX}/user_progress",
    tags=["user_progress"],
)

@user_progress_router.post("/submit_answer", response_model=UserProgressOut, status_code=status.HTTP_201_CREATED)
async def save_user_progress(
    progress_data: AnswerSubmit,
    db: AsyncSession = Depends(get_db),
):
    try:
        progress = await crud_progress.create_or_update_progress(db, progress_data)
        return progress
    except Exception as e:
        import traceback
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"[save_user_progress] Unhandled exception:\n{tb}")
        raise HTTPException(status_code=500, detail="Internal server error, see logs for details")

users_router = APIRouter(
    prefix=f"{PREFIX}/users",
    tags=["users"],
)

@users_router.get("/{user_id}/stats", response_model=UserStatsOut, status_code=status.HTTP_200_OK)
async def user_stats_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        stats = await crud_user.get_user_stats(db, user_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=404, detail="User not found or error getting stats")

@users_router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def upsert_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating/updating user: {user.telegram_id}, {user.username}")
    try:
        return await crud_user.create_or_update_user(db, user)
    except Exception as e:
        logger.error(f"Error creating/updating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")

@users_router.get("/by-telegram-id/{telegram_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user_by_telegram_id_endpoint(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await crud_user.get_user_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@users_router.patch("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def patch_user_settings_endpoint(
    user_id: UUID,
    payload: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        updated = await crud_user.update_user_settings(db, user_id, payload)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(status_code=500, detail="Error updating user settings")

# NEW: Exam settings endpoints
@users_router.post("/{user_id}/exam-settings", response_model=ExamSettingsResponse)
async def set_exam_settings(
    user_id: UUID,
    settings: ExamSettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Set user's exam date and daily goal"""
    try:
        # Validate exam date is in the future
        if settings.exam_date <= date.today():
            raise HTTPException(status_code=400, detail="Exam date must be in the future")
        
        # Update user with exam settings
        update_data = UserSettingsUpdate(
            exam_date=settings.exam_date,
            daily_goal=settings.daily_goal
        )
        
        updated_user = await crud_user.update_user_settings(db, user_id, update_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate days until exam and recommendations
        days_until_exam = (settings.exam_date - date.today()).days
        total_questions = 100  # Adjust based on your question database
        recommended_daily_goal = max(1, total_questions // max(1, days_until_exam))
        
        return ExamSettingsResponse(
            exam_date=settings.exam_date,
            daily_goal=settings.daily_goal,
            days_until_exam=days_until_exam,
            recommended_daily_goal=recommended_daily_goal
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting exam settings: {e}")
        raise HTTPException(status_code=500, detail="Error setting exam settings")

@users_router.get("/{user_id}/exam-settings", response_model=ExamSettingsResponse)
async def get_exam_settings(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get user's exam settings"""
    try:
        user = await crud_user.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        days_until_exam = None
        recommended_daily_goal = None
        
        if user.exam_date:
            days_until_exam = (user.exam_date - date.today()).days
            total_questions = 100
            recommended_daily_goal = max(1, total_questions // max(1, days_until_exam))
        
        return ExamSettingsResponse(
            exam_date=user.exam_date,
            daily_goal=user.daily_goal,
            days_until_exam=days_until_exam,
            recommended_daily_goal=recommended_daily_goal
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exam settings: {e}")
        raise HTTPException(status_code=500, detail="Error getting exam settings")

topics_router = APIRouter(tags=["topics"])

@topics_router.get("/topics", response_model=TopicsOut)
async def get_topics(
    country: str = Query(..., description="Country code, e.g. AM"),
    language: str = Query(..., description="Language code, e.g. ru"),
    db: AsyncSession = Depends(get_db),
):
    topics = await fetch_topics(db, country, language)
    return TopicsOut(topics=topics)