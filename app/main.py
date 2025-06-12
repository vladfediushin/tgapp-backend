# backend/app/main.py
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.routers import users_router, questions_router, user_progress_router, topics_router

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(docs_url="/docs", redoc_url="/redoc")

# CORS
origins = [
    "https://tgapp-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Логируем метод и URL
    logger.info(f">>> {request.method} {request.url}")

    # Логируем тело запроса (если есть)
    body = await request.body()
    if body:
        try:
            logger.info(f"    Body: {body.decode('utf-8')}")
        except Exception:
            logger.info(f"    Body (binary): {body}")

    # Прокидываем запрос дальше
    response: Response = await call_next(request)

    # Логируем статус ответа
    logger.info(f"<<< Response {response.status_code} for {request.method} {request.url.path}")
    return response

@app.get("/")
async def root():
    return {"message": "Backend is alive. Go to /docs for API info."}

# Подключение роутеров
app.include_router(users_router)
app.include_router(questions_router)
app.include_router(user_progress_router)
app.include_router(topics_router)