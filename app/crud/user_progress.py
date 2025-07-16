# Файл: app/crud/user_progress.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy.orm import joinedload
from app.models import UserProgress, Question, AnswerHistory
from app.schemas import AnswerSubmit

# Предвычисленная последовательность Фибоначчи на 20 уровней (до ~18 лет)
FIB_SEQUENCE = [
    0, 1, 1, 2, 3, 5, 8, 13, 21, 34,
    55, 89, 144, 233, 377, 610, 987,
    1597, 2584, 4181, 6765
]


def calculate_next_due_date(repetition_count: int) -> datetime:
    """
    Возвращает следующую дату повторения: текущее время + интервал по Фибоначчи.
    """
    idx = min(repetition_count, len(FIB_SEQUENCE) - 1)
    days = FIB_SEQUENCE[idx]
    return datetime.utcnow() + timedelta(days=days)


async def create_or_update_progress(
    db: AsyncSession,
    data: AnswerSubmit
) -> UserProgress:
    """
    Создаёт или обновляет запись UserProgress при ответе пользователя.
    Логирует каждый ответ в AnswerHistory.
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

    # 2. Получаем текущий прогресс (если есть)
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

    # 3. Обновляем или создаём прогресс
    if prog:
        if data.is_correct:
            prog.repetition_count += 1
        else:
            prog.repetition_count = 0
        prog.is_correct = data.is_correct
        prog.last_answered_at = now
        prog.next_due_at = calculate_next_due_date(prog.repetition_count)
    else:
        reps = 1 if data.is_correct else 0
        next_due = calculate_next_due_date(reps)
        prog = UserProgress(
            user_id=data.user_id,
            question_id=data.question_id,
            is_correct=data.is_correct,
            repetition_count=reps,
            last_answered_at=now,
            next_due_at=next_due,
        )
        db.add(prog)

    await db.commit()
    await db.refresh(prog)
    return prog


async def create_or_update_progress_batch(
    db: AsyncSession,
    data: AnswerSubmit
) -> UserProgress:
    """
    Создаёт или обновляет запись UserProgress при ответе пользователя.
    Логирует каждый ответ в AnswerHistory.
    ВНИМАНИЕ: НЕ делает commit - используется для batch операций.
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

    # 2. Получаем текущий прогресс (если есть)
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

    # 3. Обновляем или создаём прогресс
    if prog:
        if data.is_correct:
            prog.repetition_count += 1
        else:
            prog.repetition_count = 0
        prog.is_correct = data.is_correct
        prog.last_answered_at = now
        prog.next_due_at = calculate_next_due_date(prog.repetition_count)
    else:
        reps = 1 if data.is_correct else 0
        next_due = calculate_next_due_date(reps)
        prog = UserProgress(
            user_id=data.user_id,
            question_id=data.question_id,
            is_correct=data.is_correct,
            repetition_count=reps,
            last_answered_at=now,
            next_due_at=next_due,
        )
        db.add(prog)

    # НЕ делаем commit здесь - это ответственность вызывающего кода
    return prog


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


async def check_answer_exists(
    db: AsyncSession, 
    user_id: UUID, 
    question_id: int, 
    timestamp: int
) -> bool:
    """Проверяет, существует ли уже ответ с данным timestamp"""
    try:
        # Конвертируем timestamp из миллисекунд в datetime
        if timestamp:
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
            return existing is not None
        else:
            # Если timestamp не передан, используем старую логику (проверка за последние 5 минут)
            result = await db.execute(
                select(AnswerHistory)
                .where(
                    AnswerHistory.user_id == user_id,
                    AnswerHistory.question_id == question_id,
                    AnswerHistory.answered_at >= datetime.utcnow() - timedelta(minutes=5)
                )
            )
            existing = result.scalar_one_or_none()
            return existing is not None
            
    except Exception as e:
        # При ошибке не блокируем сохранение
        print(f"Warning: Could not check for duplicate answer: {e}")
        return False
