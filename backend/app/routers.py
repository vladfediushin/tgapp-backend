import logging
from datetime import date, datetime, timedelta
from sqlalchemy import text
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    QuestionOut, AnswerSubmit, BatchAnswersSubmit, BatchAnswerItem, UserProgressOut, UserCreate, UserOut, 
    TopicsOut, UserStatsOut, UserSettingsUpdate, ExamSettingsUpdate, ExamSettingsResponse,
    DailyProgressOut
)
from app.crud.question import fetch_questions_for_user, get_distinct_countries, get_distinct_languages, fetch_topics
from app.crud import user_progress as crud_progress
from app.crud import user as crud_user

logger = logging.getLogger("api")
PREFIX = ""

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@users_router.get("/{user_id}/answers-by-day")
async def get_answers_by_day(
    user_id: UUID,
    days: int = Query(7, ge=1, le=30, description="Сколько дней вернуть"),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает массив по последним N дням: дата, total, correct, incorrect"""
    today = date.today()
    days_list = [(today - timedelta(days=i)) for i in range(1, days+1)]
    days_list.reverse()  # от старых к новым

    # SQL: сгруппировать по дням
    sql = text("""
        SELECT DATE(answered_at) AS answer_date,
               COUNT(*) AS total_answers,
               COUNT(*) FILTER (WHERE is_correct) AS correct_answers,
               COUNT(*) FILTER (WHERE NOT is_correct) AS incorrect_answers
        FROM answer_history
        WHERE user_id = :user_id
          AND answered_at >= :start_date
        GROUP BY answer_date
    """)
    result = await db.execute(sql, {"user_id": str(user_id), "start_date": days_list[0]})
    rows = {str(row.answer_date): {
        "total_answers": row.total_answers,
        "correct_answers": row.correct_answers,
        "incorrect_answers": row.incorrect_answers
    } for row in result}

    # Собираем массив с нулями для пропущенных дней
    out = []
    for d in days_list:
        d_str = d.isoformat()
        day_data = rows.get(d_str, {"total_answers": 0, "correct_answers": 0, "incorrect_answers": 0})
        out.append({
            "date": d_str,
            **day_data
        })
    return out

questions_router = APIRouter(
    prefix=f"{PREFIX}/questions",
    tags=["questions"])

user_progress_router = APIRouter(
    prefix=f"{PREFIX}/user_progress",
    tags=["user_progress"],
)

@questions_router.get("/countries", response_model=List[str])
async def list_countries(db: AsyncSession = Depends(get_db)):
    return await get_distinct_countries(db)

@questions_router.get("/languages", response_model=List[str])
async def list_languages(db: AsyncSession = Depends(get_db)):
    return await get_distinct_languages(db)

@questions_router.get("/remaining-count")
async def get_remaining_questions_count(
    user_id: UUID = Query(..., description="Internal user UUID"),
    country: str = Query(..., description="Exam country code"),
    language: str = Query(..., description="Exam language code"),
    db: AsyncSession = Depends(get_db),
):
    """Get count of questions user still needs to answer correctly"""
    try:
        user = await crud_user.get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        from app.crud.question import get_remaining_questions_count
        remaining_count = await get_remaining_questions_count(
            db=db,
            user_id=user_id,
            country=country,
            language=language
        )
        
        return {"remaining_count": remaining_count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting remaining questions count: {e}")
        raise HTTPException(status_code=500, detail="Error getting remaining questions count")

@questions_router.get("/", response_model=List[QuestionOut])
async def get_questions(
    user_id: UUID = Query(..., description="Internal user UUID"),
    mode: str = Query(..., description="Mode: interval_all, new_only, incorrect, topics"),
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

@user_progress_router.post("/submit_answer", response_model=UserProgressOut, status_code=status.HTTP_201_CREATED)
async def save_user_progress(
    progress_data: AnswerSubmit,
    rating: int = Query(3, ge=1, le=4, description="FSRS difficulty rating (1=Again, 2=Hard, 3=Good, 4=Easy)"),
    db: AsyncSession = Depends(get_db),
):
    try:
        progress = await crud_progress.create_or_update_progress(db, progress_data, rating)
        return progress
    except Exception as e:
        import traceback
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"[save_user_progress] Unhandled exception:\n{tb}")
        raise HTTPException(status_code=500, detail="Internal server error, see logs for details")


@user_progress_router.post("/submit_answers", response_model=UserStatsOut, status_code=status.HTTP_201_CREATED)
async def save_user_answers_batch(
    batch_data: BatchAnswersSubmit,
    db: AsyncSession = Depends(get_db),
):
    try:
        # Обрабатываем все ответы в батче
        processed_count = 0
        for answer_data in batch_data.answers:
            # Создаем полный объект AnswerSubmit 
            full_answer = AnswerSubmit(
                user_id=batch_data.user_id,
                question_id=answer_data.question_id,
                is_correct=answer_data.is_correct,
                timestamp=answer_data.timestamp
            )
            
            # Проверяем дедупликацию по timestamp (если есть)
            if answer_data.timestamp:
                # Можно добавить проверку на дубли в БД, пока пропускаем
                pass
                
            await crud_progress.create_or_update_progress(db, full_answer, 3)  # Default Good rating
            processed_count += 1
            
        # Возвращаем обновленную статистику пользователя
        stats = await crud_user.get_user_stats(db, batch_data.user_id)
        logger.info(f"Processed {processed_count} answers for user {batch_data.user_id}")
        return stats
        
    except Exception as e:
        import traceback
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"[save_user_answers_batch] Unhandled exception:\n{tb}")
        raise HTTPException(status_code=500, detail="Internal server error, see logs for details")


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
    settings: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        # Проверка даты экзамена только если она указана
        if settings.exam_date is not None and settings.exam_date <= date.today():
            raise HTTPException(status_code=400, detail="Exam date must be in the future")
        
        # Обновляем настройки пользователя
        updated_user = await crud_user.update_user_settings(db, user_id, settings)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Рассчитываем дни до экзамена и рекомендуемую цель, если есть дата
        days_until_exam = None
        recommended_daily_goal = None
        if settings.exam_date is not None:
            days_until_exam = (settings.exam_date - date.today()).days

            if updated_user.exam_country and updated_user.exam_language:
                total_questions = await crud_user.get_total_questions(
                    db,
                    updated_user.exam_country,
                    updated_user.exam_language
                )
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
            if user.exam_country and user.exam_language:
                total_questions = await crud_user.get_total_questions(
                    db,
                    user.exam_country,
                    user.exam_language
                )
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
    
@users_router.get("/{user_id}/daily-progress", response_model=DailyProgressOut)
async def get_daily_progress_endpoint(
    user_id: UUID,
    target_date: Optional[date] = Query(None, description="Date to check progress for (default: today)"),
    db: AsyncSession = Depends(get_db),
):
    """Get daily progress for user - questions mastered today"""
    try:
        from app.crud.user import get_daily_progress
        progress = await get_daily_progress(db, user_id, target_date)
        return progress
    except Exception as e:
        logger.error(f"Error getting daily progress for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error getting daily progress")


topics_router = APIRouter(tags=["topics"])

@topics_router.get("/topics", response_model=TopicsOut)
async def get_topics(
    country: str = Query(..., description="Country code, e.g. AM"),
    language: str = Query(..., description="Language code, e.g. ru"),
    db: AsyncSession = Depends(get_db),
):
    topics = await fetch_topics(db, country, language)
    return TopicsOut(topics=topics)

@users_router.post("/{user_id}/submit_answers", response_model=UserStatsOut, status_code=status.HTTP_201_CREATED)
async def submit_answers(
    user_id: UUID,
    answers_data: BatchAnswersSubmit,
    use_fsrs: bool = Query(default=False, description="Enable FSRS algorithm for scheduling"),
    db: AsyncSession = Depends(get_db),
):
    """Submit multiple answers at once with deduplication and optional FSRS support"""
    try:
        processed_answers = 0
        skipped_answers = 0
        
        logger.info(f"🚀 Starting batch submission for user {user_id}, {len(answers_data.answers)} answers received, FSRS: {use_fsrs}")
        
        # Обрабатываем все ответы в одной транзакции
        for i, answer_data in enumerate(answers_data.answers):
            logger.info(f"📝 Processing answer {i+1}/{len(answers_data.answers)}: question_id={answer_data.question_id}, is_correct={answer_data.is_correct}, timestamp={answer_data.timestamp}")
            
            # Обеспечиваем что timestamp не None (если None, используем текущее время)
            timestamp = answer_data.timestamp or int(datetime.now().timestamp() * 1000)
            
            # Проверяем дедупликацию по question_id + timestamp
            if timestamp:
                # Проверяем, не был ли уже записан этот ответ
                existing = await crud_progress.check_answer_exists(
                    db, user_id, answer_data.question_id, timestamp
                )
                if existing:
                    logger.info(f"⏭️ Skipping duplicate answer for question {answer_data.question_id}, timestamp {timestamp}")
                    skipped_answers += 1
                    continue
            
            # Создаем объект AnswerSubmit для совместимости с существующей логикой
            # user_id берем из URL параметра /{user_id}/submit_answers
            answer_submit = AnswerSubmit(
                user_id=user_id,  # user_id из URL параметра
                question_id=answer_data.question_id,
                is_correct=answer_data.is_correct,
                timestamp=timestamp,  # Гарантированно int, не None
                response_time=answer_data.response_time,  # Новое поле
                difficulty_rating=answer_data.difficulty_rating  # Новое поле
            )
            
            # Выбираем алгоритм на основе флага
            if use_fsrs:
                # Вычисляем FSRS rating если не предоставлен
                rating = answer_data.difficulty_rating
                if rating is None:
                    # Автоматически определяем rating на основе корректности и времени ответа
                    if answer_data.is_correct:
                        if answer_data.response_time and answer_data.response_time < 3000:
                            rating = 4  # Easy - быстрый правильный ответ
                        elif answer_data.response_time and answer_data.response_time > 8000:
                            rating = 2  # Hard - медленный правильный ответ  
                        else:
                            rating = 3  # Good - обычный правильный ответ
                    else:
                        rating = 1  # Again - неправильный ответ
                
                logger.info(f"🧠 Using FSRS algorithm with rating {rating} for question {answer_data.question_id}")
                await crud_progress.create_or_update_progress_batch(db, answer_submit, rating)
            else:
                # Default rating if FSRS not requested
                rating = 3  # Good
                logger.info(f"📚 Using traditional FSRS with default rating for question {answer_data.question_id}")
                await crud_progress.create_or_update_progress_batch(db, answer_submit, rating)
            
            processed_answers += 1
        
        # Делаем общий commit для всех ответов
        logger.info(f"🔄 Committing transaction: {processed_answers} processed, {skipped_answers} skipped")
        await db.commit()
        logger.info(f"✅ Successfully committed {processed_answers} answers for user {user_id}")
        
        # Возвращаем обновленную статистику
        stats = await crud_user.get_user_stats(db, user_id)
        logger.info(f"📊 Returning stats: {stats}")
        return stats
        
    except Exception as e:
        # Откатываем транзакцию при ошибке
        await db.rollback()
        import traceback
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"[submit_answers] Unhandled exception, rolling back:\n{tb}")
        raise HTTPException(status_code=500, detail="Internal server error, see logs for details")

# ============================================================================
# FSRS ENDPOINTS
# ============================================================================

fsrs_router = APIRouter(
    prefix="/fsrs",
    tags=["fsrs"],
)

@fsrs_router.post("/submit-answer")
async def submit_answer_fsrs(
    answer_data: AnswerSubmit,
    rating: int = Body(..., ge=1, le=4, description="FSRS rating: 1=Again, 2=Hard, 3=Good, 4=Easy"),
    db: AsyncSession = Depends(get_db)
):
    """
    FSRS-enabled: Submit a single answer with FSRS rating
    
    Args:
        answer_data: Answer submission data
        rating: FSRS rating (1-4)
    
    Returns:
        Updated progress with FSRS scheduling
    """
    try:
        progress = await crud_progress.create_or_update_progress(
            db=db, 
            data=answer_data, 
            rating=rating
        )
        
        return {
            "message": "Answer submitted successfully with FSRS",
            "progress": {
                "question_id": progress.question_id,
                "is_correct": progress.is_correct,
                "fsrs_data": {
                    "stability": progress.stability,
                    "difficulty": progress.difficulty,
                    "retrievability": progress.retrievability,
                    "state": progress.state,
                    "reps": progress.reps,
                    "lapses": progress.lapses,
                    "due": progress.due
                }
            }
        }
    except Exception as e:
        logger.error(f"Error submitting FSRS answer: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@fsrs_router.post("/submit-batch")  
async def submit_batch_answers_fsrs(
    batch_data: BatchAnswersSubmit,
    ratings: List[int] = Body(..., description="FSRS ratings corresponding to each answer (1-4)"),
    db: AsyncSession = Depends(get_db)
):
    """
    FSRS-enabled: Submit multiple answers with FSRS ratings
    
    Args:
        batch_data: Batch of answer submissions
        ratings: List of FSRS ratings (1-4) corresponding to each answer
    
    Returns:
        Batch processing results with FSRS scheduling
    """
    if len(batch_data.answers) != len(ratings):
        raise HTTPException(
            status_code=400, 
            detail="Number of answers must match number of ratings"
        )
    
    try:
        results = []
        
        for answer_item, rating in zip(batch_data.answers, ratings):
            # Validate rating
            if not (1 <= rating <= 4):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid rating {rating}. Must be between 1 and 4"
                )
            
            # Convert BatchAnswerItem to AnswerSubmit
            answer_data = AnswerSubmit(
                user_id=batch_data.user_id,
                question_id=answer_item.question_id,
                is_correct=answer_item.is_correct,
                answered_at=answer_item.answered_at
            )
            
            # Process with FSRS (no commit yet)
            progress = await crud_progress.create_or_update_progress_batch(
                db=db,
                data=answer_data,
                rating=rating
            )
            
            results.append({
                "question_id": progress.question_id,
                "processed": True,
                "fsrs_rating": rating,
                "due": progress.due,
                "stability": progress.stability,
                "difficulty": progress.difficulty
            })
        
        # Commit all changes at once
        await db.commit()
        
        return {
            "message": f"Successfully processed {len(results)} answers with FSRS",
            "results": results
        }
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error in FSRS batch submission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@fsrs_router.get("/due-questions/{user_id}")
async def get_due_questions(
    user_id: UUID,
    country: str = Query(..., description="Question country"),
    language: str = Query(..., description="Question language"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of questions"),
    db: AsyncSession = Depends(get_db)
):
    """
    FSRS-enabled: Get questions due for review based on FSRS scheduling
    
    Args:
        user_id: User ID
        country: Question country filter
        language: Question language filter  
        limit: Maximum questions to return
    
    Returns:
        List of questions due for review with FSRS data
    """
    try:
        due_progress = await crud_progress.get_due_questions(
            db=db,
            user_id=user_id,
            country=country,
            language=language,
            limit=limit
        )
        
        from app.services.fsrs_service import fsrs_service
        
        results = []
        for progress in due_progress:
            # Get FSRS status for this card
            due_status = fsrs_service.get_card_due_status(progress)
            
            # Get predicted intervals for all ratings
            intervals = fsrs_service.get_next_intervals(progress)
            
            results.append({
                "question_id": progress.question_id,
                "due_date": progress.due,
                "days_overdue": abs(due_status['days_until_due']),
                "fsrs_data": {
                    "state": due_status['state'],
                    "stability": due_status['stability'],
                    "difficulty": due_status['difficulty'],
                    "reps": progress.reps,
                    "lapses": progress.lapses
                },
                "predicted_intervals": intervals
            })
        
        return {
            "total_due": len(results),
            "questions": results
        }
        
    except Exception as e:
        logger.error(f"Error getting FSRS due questions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@fsrs_router.get("/stats/{user_id}")
async def get_fsrs_stats(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get FSRS statistics for a user
    
    Args:
        user_id: User ID
    
    Returns:
        FSRS statistics and metrics
    """
    try:
        stats = await crud_progress.get_fsrs_stats(db=db, user_id=user_id)
        
        # Add state name mapping
        state_names = {
            0: "New",
            1: "Learning", 
            2: "Review",
            3: "Relearning"
        }
        
        stats['state_distribution_named'] = {
            state_names.get(state, f"Unknown({state})"): count
            for state, count in stats['state_distribution'].items()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting FSRS stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@fsrs_router.get("/card-info/{user_id}/{question_id}")
async def get_card_info(
    user_id: UUID,
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed FSRS information for a specific card
    
    Args:
        user_id: User ID
        question_id: Question ID
    
    Returns:
        Detailed FSRS card information
    """
    try:
        # Get progress record
        progress = await crud_progress.get_user_progress_for_question(
            db=db,
            user_id=user_id, 
            question_id=question_id
        )
        
        if not progress:
            raise HTTPException(status_code=404, detail="Progress record not found")
        
        from app.services.fsrs_service import fsrs_service
        
        # Get FSRS status
        due_status = fsrs_service.get_card_due_status(progress)
        intervals = fsrs_service.get_next_intervals(progress)
        
        return {
            "question_id": question_id,
            "user_id": user_id,
            "current_status": due_status,
            "predicted_intervals": intervals,
            "history": {
                "total_reps": progress.reps or 0,
                "total_lapses": progress.lapses or 0,
                "last_review": progress.last_review,
                "created_at": progress.last_answered_at
            },
            "fsrs_params": {
                "stability": progress.stability,
                "difficulty": progress.difficulty, 
                "retrievability": progress.retrievability,
                "state": progress.state,
                "elapsed_days": progress.elapsed_days,
                "scheduled_days": progress.scheduled_days
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting card info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")