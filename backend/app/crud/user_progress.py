# Файл: app/crud/user_progress.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import joinedload
from app.models import UserProgress, Question, AnswerHistory
from app.schemas import AnswerSubmit
from app.services.fsrs_service import fsrs_service


async def create_or_update_progress(
    db: AsyncSession,
    data: AnswerSubmit,
    rating: int  # FSRS rating (1-4)
) -> UserProgress:
    """
    FSRS-only version: Создаёт или обновляет прогресс с использованием FSRS алгоритма
    """
    return await create_or_update_progress_internal(db, data, rating)


async def create_or_update_progress_batch(
    db: AsyncSession,
    data: AnswerSubmit,
    rating: int  # FSRS rating (1-4)
) -> UserProgress:
    """
    FSRS-only batch version: НЕ делает commit - используется для batch операций.
    """
    return await create_or_update_progress_batch_internal(db, data, rating)


async def get_progress_for_user(
    db: AsyncSession,
    user_id: UUID
) -> list[UserProgress]:
    """
    Возвращает все записи прогресса пользователя, с предзагрузкой связанных вопросов.
    """
    stmt = (
        select(UserProgress)
        .options(joinedload(UserProgress.question))
        .where(UserProgress.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_progress_for_user_and_question(
    db: AsyncSession,
    user_id: UUID,
    question_id: int,
    country: str,
    language: str
) -> UserProgress | None:
    """
    Возвращает запись UserProgress для заданного user_id, question_id,
    country и language, учитывая данные из таблицы Question,
    с предзагрузкой связанных вопросов.
    """
    stmt = (
        select(UserProgress)
        .options(joinedload(UserProgress.question))
        .join(Question, UserProgress.question_id == Question.id)
        .where(
            UserProgress.user_id == user_id,
            UserProgress.question_id == question_id,
            Question.country == country,
            Question.language == language,
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_progress_for_question(
    db: AsyncSession,
    user_id: UUID,
    question_id: int
) -> UserProgress | None:
    """
    Получает прогресс пользователя для конкретного вопроса

    Args:
        db: Database session
        user_id: User ID
        question_id: Question ID

    Returns:
        UserProgress record or None if not found
    """
    stmt = (
        select(UserProgress)
        .where(
            UserProgress.user_id == user_id,
            UserProgress.question_id == question_id
        )
    )

    result = await db.execute(stmt)
    return result.scalars().first()


async def check_answer_exists(
    db: AsyncSession, 
    user_id: UUID, 
    question_id: int, 
    timestamp: int
) -> bool:
    """Проверяет, существует ли уже ответ с данным timestamp"""
    try:
        # Конвертируем timestamp из миллисекунд в datetime
        target_time = datetime.fromtimestamp(timestamp / 1000)  # timestamp приходит в миллисекундах
        
        # Проверяем точное совпадение в пределах 1 секунды (для учета погрешности)
        time_window = timedelta(seconds=1)
        result = await db.execute(
            select(AnswerHistory)
            .where(
                AnswerHistory.user_id == user_id,
                AnswerHistory.question_id == question_id,
                AnswerHistory.answered_at >= target_time - time_window,
                AnswerHistory.answered_at <= target_time + time_window
            )
        )
        existing = result.scalar_one_or_none()
        existing = result.scalar_one_or_none()
        return existing is not None
            
    except Exception as e:
        # При ошибке не блокируем сохранение
        print(f"Warning: Could not check for duplicate answer: {e}")
        return False


# ============================================================================
# INTERNAL FSRS FUNCTIONS
# ============================================================================


async def create_or_update_progress_internal(
    db: AsyncSession,
    data: AnswerSubmit,
    rating: int  # 1=Again, 2=Hard, 3=Good, 4=Easy
) -> UserProgress:
    """
    FSRS-enabled version: Создаёт или обновляет прогресс с использованием FSRS алгоритма
    
    Args:
        db: Database session
        data: Answer submission data
        rating: FSRS rating (1-4) based on user performance
    
    Returns:
        Updated UserProgress record
    """
    now = datetime.utcnow()

    # 1. Логируем ответ в историю
    history_entry = AnswerHistory(
        user_id=data.user_id,
        question_id=data.question_id,
        is_correct=data.is_correct,
        answered_at=now
    )
    db.add(history_entry)

    # 2. Получаем текущий прогресс
    stmt = (
        select(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(
            UserProgress.user_id == data.user_id,
            UserProgress.question_id == data.question_id,
        )
    )
    result = await db.execute(stmt)
    prog = result.scalars().first()

    # 3. Обновляем или создаём прогресс с FSRS
    if prog:
        # Используем FSRS для расчёта следующего интервала
        fsrs_data = fsrs_service.schedule_review(prog, rating, now)
        
        # Обновляем базовые поля
        if data.is_correct:
            prog.reps = (prog.reps or 0) + 1
        else:
            prog.lapses = (prog.lapses or 0) + 1
        prog.is_correct = data.is_correct
        prog.last_answered_at = now
        
        # Обновляем FSRS поля
        for field, value in fsrs_data.items():
            if field in ['reps', 'lapses']:
                # Skip these, we manage them above
                continue
            setattr(prog, field, value)
        
    else:
        # Новая запись - создаём с базовыми FSRS параметрами
        reps = 1 if data.is_correct else 0
        
        prog = UserProgress(
            user_id=data.user_id,
            question_id=data.question_id,
            is_correct=data.is_correct,
            last_answered_at=now,
            # FSRS поля для новой карточки
            stability=0.0,
            difficulty=0.0,
            retrievability=None,
            elapsed_days=0,
            scheduled_days=0,
            reps=reps,
            lapses=0 if data.is_correct else 1,
            state=0,  # New state
            last_review=now,
            due=now,  # Will be updated by FSRS
        )
        db.add(prog)
        
        # Применяем FSRS расчёт для новой карточки
        fsrs_data = fsrs_service.schedule_review(prog, rating, now)
        for field, value in fsrs_data.items():
            if field in ['reps', 'lapses']:
                # Skip these, we set them above
                continue
            setattr(prog, field, value)

    await db.commit()
    await db.refresh(prog)
    return prog


async def create_or_update_progress_batch_internal(
    db: AsyncSession,
    data: AnswerSubmit,
    rating: int
) -> UserProgress:
    """
    FSRS-enabled batch version: Без commit для использования в batch операциях
    
    Args:
        db: Database session
        data: Answer submission data  
        rating: FSRS rating (1-4)
    
    Returns:
        Updated UserProgress record (not committed)
    """
    now = datetime.utcnow()

    # 1. Логируем ответ в историю
    history_entry = AnswerHistory(
        user_id=data.user_id,
        question_id=data.question_id,
        is_correct=data.is_correct,
        answered_at=now
    )
    db.add(history_entry)

    # 2. Получаем текущий прогресс
    stmt = (
        select(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(
            UserProgress.user_id == data.user_id,
            UserProgress.question_id == data.question_id,
        )
    )
    result = await db.execute(stmt)
    prog = result.scalars().first()

    # 3. Обновляем или создаём прогресс с FSRS (без commit)
    if prog:
        fsrs_data = fsrs_service.schedule_review(prog, rating, now)
        
        if data.is_correct:
            prog.reps = (prog.reps or 0) + 1
        else:
            prog.lapses = (prog.lapses or 0) + 1
        prog.is_correct = data.is_correct
        prog.last_answered_at = now
        
        for field, value in fsrs_data.items():
            if field in ['reps', 'lapses']:
                continue
            setattr(prog, field, value)
        
    else:
        reps = 1 if data.is_correct else 0
        
        prog = UserProgress(
            user_id=data.user_id,
            question_id=data.question_id,
            is_correct=data.is_correct,
            last_answered_at=now,
            stability=0.0,
            difficulty=0.0,
            retrievability=None,
            elapsed_days=0,
            scheduled_days=0,
            reps=reps,
            lapses=0 if data.is_correct else 1,
            state=0,
            last_review=now,
            due=now,
        )
        db.add(prog)
        
        fsrs_data = fsrs_service.schedule_review(prog, rating, now)
        for field, value in fsrs_data.items():
            if field in ['reps', 'lapses']:
                continue
            setattr(prog, field, value)

    return prog


async def get_due_questions(
    db: AsyncSession,
    user_id: UUID,
    country: str,
    language: str,
    limit: int = 20
) -> list[UserProgress]:
    """
    FSRS-only: Получает вопросы готовые к повторению на основе FSRS расписания
    
    Args:
        db: Database session
        user_id: User ID
        country: Question country filter
        language: Question language filter
        limit: Maximum number of questions to return
    
    Returns:
        List of UserProgress records due for review
    """
    now = datetime.utcnow()
    
    # Получаем вопросы с истекшим сроком (due <= now)
    stmt = (
        select(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(
            UserProgress.user_id == user_id,
            Question.country == country,
            Question.language == language,
            UserProgress.due <= now  # FSRS due field
        )
        .order_by(UserProgress.due.asc())  # Сначала самые просроченные
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_stats(db: AsyncSession, user_id: UUID) -> dict:
    """
    Получает статистику FSRS для пользователя
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Dict with FSRS statistics
    """
    now = datetime.utcnow()
    
    # Получаем все записи прогресса пользователя с FSRS данными
    stmt = (
        select(UserProgress)
        .where(
            UserProgress.user_id == user_id,
            UserProgress.state.isnot(None)  # Only FSRS-enabled records
        )
    )
    
    result = await db.execute(stmt)
    all_progress = result.scalars().all()
    
    if not all_progress:
        return {
            'total_cards': 0,
            'due_count': 0,
            'avg_stability': 0.0,
            'avg_difficulty': 0.0,
            'state_distribution': {}
        }
    
    # Подсчитываем статистики
    due_count = sum(1 for p in all_progress if p.due and p.due <= now)
    total_cards = len(all_progress)
    
    stabilities = [p.stability for p in all_progress if p.stability is not None]
    difficulties = [p.difficulty for p in all_progress if p.difficulty is not None]
    
    avg_stability = sum(stabilities) / len(stabilities) if stabilities else 0.0
    avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 0.0
    
    # Распределение по состояниям
    state_counts = {}
    for progress in all_progress:
        state = progress.state if progress.state is not None else 0
        state_counts[state] = state_counts.get(state, 0) + 1
    
    return {
        'total_cards': total_cards,
        'due_count': due_count,
        'avg_stability': round(avg_stability, 2),
        'avg_difficulty': round(avg_difficulty, 2),
        'state_distribution': state_counts
    }
