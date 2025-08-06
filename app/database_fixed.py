# app/database.py
import os
import logging
import uuid
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import InterfaceError, OperationalError, DisconnectionError

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

# Добавляем URL параметры для ПОЛНОГО отключения prepared statements
# КРИТИЧНО: server_side_cursors НЕ поддерживается asyncpg!
url_params = [
    "statement_cache_size=0",
    "prepared_statement_cache_size=0"
]

if "?" in DATABASE_URL:
    DATABASE_URL += "&" + "&".join(url_params)
else:
    DATABASE_URL += "?" + "&".join(url_params)

# Оптимальная настройка для Neon PostgreSQL с connection recovery
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,           # КРИТИЧНО: проверяет соединение перед использованием
    pool_recycle=3600,            # Пересоздает соединения каждый час
    pool_timeout=7,               # Таймаут ожидания соединения из пула
    connect_args={
        "command_timeout": 7.0,
        "server_settings": {
            "application_name": "tgapp_backend",
        }
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False
)
Base = declarative_base()

def get_pool_status():
    """Возвращает статистику пула соединений для мониторинга."""
    pool = engine.pool
    try:
        url_str = str(engine.url) if hasattr(engine, 'url') else ""
        if ":5432" in url_str:
            supabase_mode = "session_mode"
        elif ":6543" in url_str:
            supabase_mode = "transaction_mode"
        else:
            supabase_mode = "unknown"
            
        stats = {
            "pool_class": pool.__class__.__name__,
            "supabase_mode": supabase_mode,
            "note": f"Using Supabase Supavisor in {supabase_mode}."
        }
        
        client_stats = {}
        safe_methods = ['size', 'checkedin', 'checkedout']
        
        for method in safe_methods:
            try:
                if hasattr(pool, method):
                    client_stats[method] = getattr(pool, method)()
            except Exception:
                client_stats[method] = "not_available"
        
        if client_stats:
            stats["client_side_pool"] = client_stats
        
        stats["engine_echo"] = engine.echo
        
        return stats
        
    except Exception as e:
        return {
            "pool_class": "unknown",
            "status": "error", 
            "error": str(e),
            "note": "Error getting pool status"
        }

# Dependency для получения сессии БД с улучшенной обработкой ошибок
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise

# Декоратор для автоматического retry при connection errors
def db_retry(max_retries=3, delay=0.5):
    """
    Декоратор для повторных попыток при ошибках соединения с БД.
    Решает проблему connection timeout после простоя.
    
    Args:
        max_retries: Максимальное количество попыток (по умолчанию 3)
        delay: Базовая задержка между попытками в секундах (по умолчанию 0.5)
    
    Returns:
        Декоратор функции с автоматическим retry при connection errors
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (InterfaceError, OperationalError, DisconnectionError) as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Проверяем, что это именно connection error
                    if any(keyword in error_msg for keyword in [
                        'connection is closed', 
                        'connection was closed', 
                        'connection lost',
                        'server closed the connection',
                        'connection timeout',
                        'connection has been closed',
                        'asyncpg.exceptions.ConnectionDoesNotExistError'
                    ]):
                        logger.warning(f"Database connection error on attempt {attempt + 1}/{max_retries}: {e}")
                        
                        if attempt < max_retries - 1:
                            # Exponential backoff: 0.5s, 1s, 1.5s
                            await asyncio.sleep(delay * (attempt + 1))
                            continue
                    
                    # Если это не connection error или последняя попытка, пробрасываем исключение
                    raise
            
            # Если все попытки исчерпаны
            logger.error(f"All {max_retries} retry attempts failed for function {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator
