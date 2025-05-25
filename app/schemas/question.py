# app/schemas/question.py
from pydantic import BaseModel
from typing import Any


class QuestionOut(BaseModel):
    id: int
    data: Any
    topic: str
    country: str
    language: str

    class Config:
        orm_mode = True
