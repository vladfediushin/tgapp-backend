from sqlalchemy import Column, String, BigInteger, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship


from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_progress = relationship(
        "UserProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
