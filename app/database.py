# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, 
                             echo=True, 
                             pool_size=5,
                             max_overflow=5,
                             pool_timeout=30,
                             pool_pre_ping=True,
                             connect_args={"statement_cache_size": 0},
                            )
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

# dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session