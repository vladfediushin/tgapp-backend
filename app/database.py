# app/database.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

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

# Оптимизированная конфигурация для Supabase Transaction Pooler
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,          # Постоянных соединений - 5 (согласно договоренности)
    max_overflow=2,       # Временных добавочных соединений - 2
    pool_timeout=5,       # БЫСТРЫЙ таймаут - 5 секунд
    pool_recycle=300,     # 5 минут переиспользования (оптимально для веб-приложения)
    pool_pre_ping=True,   # Проверяем соединения
    echo=False,
    # Отключаем prepared statements для Supabase Transaction Pooler
    connect_args={
        "server_settings": {
            "statement_cache_size": "0"
        }
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