# app/database.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

# Оптимизированная конфигурация для Supabase
engine = create_async_engine(
    DATABASE_URL,
    pool_size=1,          # Минимальный размер пула для экономии соединений
    max_overflow=2,       # Небольшое количество дополнительных соединений  
    pool_timeout=5,       # БЫСТРЫЙ таймаут - 5 секунд
    pool_recycle=300,     # 5 минут переиспользования (оптимально для веб-приложения)
    pool_pre_ping=True,   # Проверяем соединения
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False
)
Base = declarative_base()

# Dependency для получения сессии БД
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()