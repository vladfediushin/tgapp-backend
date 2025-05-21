# backend/app/schemas/question.py
from pydantic import BaseModel

class Question(BaseModel):
    id: int
    text: str
    image_url: str
    options: list[str]
    correct_index: int
    topic: str