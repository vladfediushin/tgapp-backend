# 1. schemas/user.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserOut(UserCreate):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True