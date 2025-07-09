# app/crud/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.models import User, Question, UserProgress, AnswerHistory
from app.schemas import UserCreate, UserSettingsUpdate
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from datetime import date, datetime, timedelta
from uuid import UUID
from typing import Optional


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    q = select(User).where(User.id == user_id)
    result = await db.execute(q)
    return result.scalars().first()

async def create_or_update_user(
    db: AsyncSession,
    user_data: UserCreate
) -> User:
    user = await db.execute(select(User).where(User.telegram_id == user_data.telegram_id))
    user = user.scalar_one_or_none()

    if user:
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
    else:
        user = User(**user_data.dict(), created_at=datetime.utcnow())
        db.add(user)

    await db.commit()
    await db.refresh(user)
    return user

async def update_user_settings(
    db: AsyncSession,
    user_id: UUID,
    settings: UserSettingsUpdate
) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None

    for field, value in settings.dict().items():
        setattr(user, field, value)
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


from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models import Question, UserProgress

async def get_user_stats(db: AsyncSession, user_id: UUID) -> dict:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # total вопросов
    total_q_stmt = (
        select(func.count())
        .select_from(Question)
        .where(Question.country == user.exam_country)
        .where(Question.language == user.exam_language)
    )
    total_questions = (await db.execute(total_q_stmt)).scalar_one()

    # answered — с JOIN на Question
    answered_stmt = (
        select(func.count())
        .select_from(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(UserProgress.user_id == user_id)
        .where(Question.country == user.exam_country)
        .where(Question.language == user.exam_language)
    )
    answered = (await db.execute(answered_stmt)).scalar_one()

    # correct — то же самое, плюс is_correct=True
    correct_stmt = (
        select(func.count())
        .select_from(UserProgress)
        .join(Question, UserProgress.question_id == Question.id)
        .where(UserProgress.user_id == user_id)
        .where(UserProgress.is_correct.is_(True))
        .where(Question.country == user.exam_country)
        .where(Question.language == user.exam_language)
    )
    correct = (await db.execute(correct_stmt)).scalar_one()

    return {
        "total_questions": total_questions,
        "answered": answered,
        "correct": correct,
    }


async def get_daily_progress(
    db: AsyncSession, 
    user_id: UUID, 
    target_date: date = None
) -> dict:
    """
    Считает количество вопросов, которые были "изучены" за указанный день.
    
    Вопрос считается "изученным" если:
    1. Это первый правильный ответ пользователя на этот вопрос ЗА ДЕНЬ, И
    2. Либо пользователь никогда не отвечал на этот вопрос правильно раньше,
       Либо последний ответ до сегодня был неправильным
    """
    
    if target_date is None:
        target_date = date.today()
    
    # Границы дня
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = day_start + timedelta(days=1)
    
    user = await get_user_by_id(db, user_id)
    if not user:
        return {"questions_mastered_today": 0, "date": target_date}
    
    # Получаем все правильные ответы пользователя за указанный день
    today_correct_answers = await db.execute(
        select(AnswerHistory.question_id)
        .where(
            and_(
                AnswerHistory.user_id == user_id,
                AnswerHistory.is_correct == True,
                AnswerHistory.answered_at >= day_start,
                AnswerHistory.answered_at < day_end
            )
        )
        .distinct()
    )
    today_correct_question_ids = set(row[0] for row in today_correct_answers.fetchall())
    
    if not today_correct_question_ids:
        return {"questions_mastered_today": 0, "date": target_date}
    
    # Для каждого вопроса проверяем, считается ли он "новым изученным"
    mastered_count = 0
    
    for question_id in today_correct_question_ids:
        # Проверяем историю ответов ДО сегодняшнего дня
        previous_answers = await db.execute(
            select(AnswerHistory.is_correct)
            .where(
                and_(
                    AnswerHistory.user_id == user_id,
                    AnswerHistory.question_id == question_id,
                    AnswerHistory.answered_at < day_start
                )
            )
            .order_by(AnswerHistory.answered_at.desc())
        )
        previous_results = previous_answers.fetchall()
        
        # Если никогда не отвечал на этот вопрос раньше - считается изученным
        if not previous_results:
            mastered_count += 1
            continue
            
        # Если последний ответ до сегодня был неправильным - считается изученным
        last_previous_result = previous_results[0][0]  # is_correct
        if not last_previous_result:
            mastered_count += 1
    
    return {
        "questions_mastered_today": mastered_count,
        "date": target_date
    }