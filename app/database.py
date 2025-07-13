# app/database.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

# РАДИКАЛЬНОЕ решение: добавляем параметры прямо в URL
if "?" in DATABASE_URL:
    DATABASE_URL += "&statement_cache_size=0&prepared_statement_cache_size=0"
else:
    DATABASE_URL += "?statement_cache_size=0&prepared_statement_cache_size=0"

logger.info(f"Database URL with disabled prepared statements: {DATABASE_URL.split('@')[0]}@[MASKED]")

engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,
    # Отключаем все возможные кэши SQLAlchemy
    execution_options={
        "compiled_cache": {},
        "autocommit": False,
    },
    # Дополнительно в connect_args тоже
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "command_timeout": 30,  # Таймаут 30 сек
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)
Base = declarative_base()

# dependency
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