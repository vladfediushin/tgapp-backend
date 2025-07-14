# app/database.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

# Отключаем prepared statements для стабильности Transaction Pooler
if "?" in DATABASE_URL:
    DATABASE_URL += "&statement_cache_size=0&prepared_statement_cache_size=0"
else:
    DATABASE_URL += "?statement_cache_size=0&prepared_statement_cache_size=0"

logger.info(f"Database URL configured for Transaction Pooler compatibility")

# Окончательная конфигурация для Supabase Transaction Pooler
engine = create_async_engine(
    DATABASE_URL,
    # Используем NullPool для Transaction Pooler
    poolclass=NullPool,
    
    # Полностью отключаем все виды кеширования
    connect_args={
        "prepared_statement_cache_size": 0,  # Полностью отключаем prepared statements
        "statement_cache_size": 0,           # Отключаем statement cache
        "command_timeout": 10,               # 10 секунд таймаут
    },
    
    # Дополнительные настройки
    echo=False,  # Отключаем SQL логирование
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    autoflush=False,  # Отключаем автофлуш для оптимизации
    autocommit=False
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