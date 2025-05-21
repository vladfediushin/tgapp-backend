# backend/app/routers/questions.py
from fastapi import APIRouter, Query
from app.schemas.question import Question
from app.routers.answers import answers_log
from datetime import datetime, timedelta

router = APIRouter()

MOCK_QUESTIONS = [
    Question(
        id=1,
        text="Можно ли ехать на красный свет?",
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Traffic_light_red.svg/512px-Traffic_light_red.svg.png",
        options=["Да", "Нет", "Только направо"],
        correct_index=1,
        topic="Светофоры"
    ),
    Question(
        id=2,
        text="Что означает этот знак?",
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Znak_DDW.svg/512px-Znak_DDW.svg.png",
        options=["Уступи дорогу", "Главная", "Парковка"],
        correct_index=0,
        topic="Знаки"
    ),
]

FIB_DAYS = [1, 2, 3, 5, 8, 13, 21]

@router.get("/questions", response_model=list[Question])
def get_questions(
    mode: str = Query("all"),
    user_id: int = Query(123),
    topic: str | None = Query(None)
):
    if topic:
        return [q for q in MOCK_QUESTIONS if q.topic == topic]

    if mode != "interval":
        return MOCK_QUESTIONS

    now = datetime.utcnow()
    eligible_ids = set()

    for question in MOCK_QUESTIONS:
        user_answers = [a for a in answers_log if a.user_id == user_id and a.question_id == question.id and a.is_correct]
        if not user_answers:
            eligible_ids.add(question.id)
            continue

        last_answer = sorted(user_answers, key=lambda a: a.timestamp)[-1]
        correct_times = len(user_answers)
        if correct_times >= len(FIB_DAYS):
            continue

        days_needed = FIB_DAYS[correct_times - 1]
        if last_answer.timestamp + timedelta(days=days_needed) <= now:
            eligible_ids.add(question.id)

    return [q for q in MOCK_QUESTIONS if q.id in eligible_ids]