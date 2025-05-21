# backend/app/routers/answers.py
from fastapi import APIRouter
from app.schemas.answer import AnswerSubmit

router = APIRouter()

answers_log: list[AnswerSubmit] = []

@router.post("/submit_answer")
def submit_answer(answer: AnswerSubmit):
    answers_log.append(answer)
    print(f"Ответ получен: {answer}")
    return {"status": "ok"}