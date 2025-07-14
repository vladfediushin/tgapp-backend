# app/api/health.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint для проверки состояния API и БД
    """
    try:
        # Простой запрос для проверки соединения с БД
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy" if result.scalar() == 1 else "unhealthy"
        
        return {
            "status": "healthy",
            "database": db_status,
            "message": "API is running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "unhealthy",
                "database": "error",
                "message": f"Database connection failed: {str(e)}"
            }
        )

@router.get("/health/simple")
async def simple_health_check():
    """
    Простой health check без проверки БД
    """
    return {"status": "healthy", "message": "API is running"}
