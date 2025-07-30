# backend/app/main.py
import logging
from fastapi import FastAPI, Request
import time
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.routers import users_router, questions_router, user_progress_router, topics_router
from app.api.health import router as health_router

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
    allow_origins=[
        "https://www.drivingtest.space",
        "tgapp-frontend.vercel.app",
        "tgapp-frontend-vladfediushins-projects.vercel.app",
        "https://tgapp-frontend-git-main-vladfediushins-projects.vercel.app/",
        "https://tgapp-frontend-dick4advs-vladfediushins-projects.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f">>> {request.method} {request.url}")
    body = await request.body()
    if body:
        try:
            logger.info(f"    Body: {body.decode('utf-8')}")
        except Exception:
            logger.info(f"    Body (binary): {body}")
    response: Response = await call_next(request)
    logger.info(f"<<< Response {response.status_code} for {request.method} {request.url.path}")
    return response

# Middleware для отслеживания времени обработки запроса
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(f"{request.method} {request.url.path} took {process_time:.3f}s")
    return response

@app.get("/")
async def root():
    return {"message": "Backend is alive. Go to /docs for API info."}

# Подключение роутеров
app.include_router(health_router)
app.include_router(users_router)
app.include_router(questions_router)
app.include_router(user_progress_router)
app.include_router(topics_router)