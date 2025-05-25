# app/routers/questions.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.database import get_db
from app.models.question import Question
from app.schemas.question import QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[QuestionOut])
async def get_questions(
    country: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Question)

    if country:
        stmt = stmt.where(Question.country == country)
    if language:
        stmt = stmt.where(Question.language == language)
    if topic:
        stmt = stmt.where(Question.topic == topic)

    result = await db.execute(stmt)
    return result.scalars().all()