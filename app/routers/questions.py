# app/routers/questions.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.database import get_db
from app.models.question import Question
from app.schemas.question import QuestionOut
from app.models.user_progress import UserProgress

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[QuestionOut])
async def get_questions(
# здесь надо добавить механизм получения user_id:
#    user_id:  UUID  = Depends(get_current_user),
    country: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Question) \
        .join(UserProgress, Question.id == UserProgress.question_id) \
        .where(
            #заглушка
            UserProgress.user_id == 'ddf6c239-6c30-4b58-9be8-bc209cc89a9b',
            UserProgress.next_due_at <= datetime.utcnow(),
        )

    if country:
        stmt = stmt.where(Question.country == country)
    if language:
        stmt = stmt.where(Question.language == language)
    if topic:
        stmt = stmt.where(Question.topic == topic)

    result = await db.execute(stmt)
    return result.scalars().all()