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

# Добавляем параметры для отключения prepared statements в URL
if "?" in DATABASE_URL:
    DATABASE_URL += "&statement_cache_size=0"
else:
    DATABASE_URL += "?statement_cache_size=0"

# Оптимальная настройка для Supabase с connection pooling
engine = create_async_engine(
    DATABASE_URL,  # URL уже содержит statement_cache_size=0
    # Используем стандартный QueuePool вместо NullPool
    pool_size=5,              # Размер основного пула соединений
    max_overflow=10,          # Максимум дополнительных соединений
    pool_pre_ping=True,       # Проверка соединений перед использованием
    pool_recycle=3600,        # Пересоздание соединений каждый час
    pool_timeout=30,          # Таймаут получения соединения из пула
    echo=False,
    connect_args={
        "statement_cache_size": 0,  # Отключаем prepared statements для Supabase
        "command_timeout": 30.0,    # Таймаут команд
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

# Функция для мониторинга состояния connection pool
def get_pool_status():
    """Возвращает статистику пула соединений для мониторинга"""
    pool = engine.pool
    try:
        stats = {
            "pool_class": pool.__class__.__name__,
        }
        
        # Безопасно получаем доступные методы
        safe_methods = ['size', 'checkedin', 'checkedout', 'overflow']
        for method in safe_methods:
            try:
                if hasattr(pool, method):
                    stats[method] = getattr(pool, method)()
                else:
                    stats[method] = "not_available"
            except Exception as e:
                stats[method] = f"error: {str(e)}"
        
        # Проверяем invalid отдельно, так как его часто нет в async пулах
        try:
            if hasattr(pool, 'invalid'):
                stats["invalid"] = pool.invalid()
            else:
                stats["invalid"] = "not_supported_by_async_pool"
        except Exception as e:
            stats["invalid"] = f"error: {str(e)}"
            
        # Добавляем информацию о настройках пула
        if hasattr(pool, '_pool'):
            stats["internal_pool_size"] = len(pool._pool._pool) if hasattr(pool._pool, '_pool') else "unknown"
        
        return stats
    except Exception as e:
        # Если вообще ничего не получается, возвращаем минимальную информацию
        return {
            "pool_class": pool.__class__.__name__ if hasattr(pool, '__class__') else "unknown",
            "status": "error",
            "error": str(e),
            "message": "Failed to retrieve detailed pool statistics"
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