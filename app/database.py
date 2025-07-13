# app/database.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

connect_args = {
    "statement_cache_size": 0,
    "prepared_statement_cache_size": 0,
    "server_settings": {
        "application_name": "fastapi_app",
    }
}

logger.info(f"Creating engine with connect_args: {connect_args}")
logger.info(f"Database URL (masked): {DATABASE_URL.split('@')[0]}@[MASKED]")


engine = create_async_engine(DATABASE_URL, 
                             echo=True, 
                             connect_args={
                            "statement_cache_size": 0,           
                            "prepared_statement_cache_size": 0,  
                            "server_settings": {
                                "application_name": "fastapi_app",  
                            }
                        },
                            )
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

# dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session