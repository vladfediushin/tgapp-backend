# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

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