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

# Оптимальная настройка для Supabase Connection Pooler
# Порт 5432 = Session Mode (persistent connections)
# Порт 6543 = Transaction Mode (serverless/transient connections)
# Supabase управляет server-side pooling в обоих режимах
engine = create_async_engine(
    DATABASE_URL,  # URL уже содержит statement_cache_size=0
    # Для Supabase Pooler можно использовать минимальные настройки client-side
    echo=False,
    connect_args={
        "statement_cache_size": 0,  # Обязательно для Supabase (любой режим)
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

# Функция для мониторинга состояния connection pool (адаптирована для Supabase)
def get_pool_status():
    """
    Возвращает статистику пула соединений для мониторинга.
    Для Supabase Pooler показывает доступную информацию.
    """
    pool = engine.pool
    try:
        # Определяем режим Supabase по URL
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
            "note": f"Using Supabase Supavisor in {supabase_mode}. Server-side pooling is managed by Supabase."
        }
        
        # Пытаемся получить client-side статистику, если доступна
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
        
        # Добавляем информацию о engine
        stats["engine_echo"] = engine.echo
        
        return stats
        
    except Exception as e:
        return {
            "pool_class": "unknown",
            "status": "error", 
            "error": str(e),
            "note": "Error getting pool status - this is normal for some Supabase configurations"
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