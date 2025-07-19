# app/database.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Загружаем .env файл из backend директории
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Обеспечиваем использование asyncpg драйвера
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif not DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL

# Добавляем параметры для отключения prepared statements в URL
if "?" in DATABASE_URL:
    DATABASE_URL += "&statement_cache_size=0"
else:
    DATABASE_URL += "?statement_cache_size=0"

# Радикальное решение для Supabase Transaction Pooler - NullPool без пула соединений
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    DATABASE_URL,  # URL уже содержит statement_cache_size=0
    poolclass=NullPool,       # Отключаем пул соединений полностью
    echo=False,
    # Отключаем prepared statements
    connect_args={
        "statement_cache_size": 0,  # Отключаем prepared statements
        "command_timeout": 5.0      # Таймаут команд 5 секунд (float)
    }
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