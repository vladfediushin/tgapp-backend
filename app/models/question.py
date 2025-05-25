from sqlalchemy import Column, Integer, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON, nullable=False)
    topic = Column(Text, nullable=False)
    country = Column(Text, nullable=False)
    language = Column(Text, nullable=False)

    user_progress = relationship("UserProgress", back_populates="question")