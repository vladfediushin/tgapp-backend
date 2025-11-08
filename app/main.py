# backend/app/main.py
import logging
import os
import time
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from aiogram.types import MenuButtonWebApp, Update, WebAppInfo

from bot.wiring import get_bot_and_dispatcher
from app.routers import users_router, questions_router, user_progress_router, topics_router
from app.api.health import router as health_router
from .tg_security import check_init_data, extract_user

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


@app.on_event("startup")
async def init_bot():
    """Initialize Telegram bot and dispatcher on application startup."""
    bot, dp = get_bot_and_dispatcher()
    app.state.bot = bot
    app.state.dp = dp
    logger.info("🤖 Telegram bot initialized")


def _get_bot_state():
    bot = getattr(app.state, "bot", None)
    dp = getattr(app.state, "dp", None)
    if not bot or not dp:
        raise HTTPException(status_code=500, detail="Bot is not initialized")
    return bot, dp


@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    """Handle Telegram webhook updates with shared secret validation."""
    secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret:
        raise HTTPException(status_code=401, detail="Invalid secret token")

    data = await request.json()
    update = Update.model_validate(data)

    bot, dp = _get_bot_state()
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/tg/set_webhook")
async def set_webhook():
    """Convenience endpoint to register webhook with Telegram."""
    base = os.environ["BACKEND_BASE_URL"]
    secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]
    url = f"{base.rstrip('/')}/tg/webhook"
    bot, _ = _get_bot_state()
    ok = await bot.set_webhook(url=url, secret_token=secret)
    return {"ok": ok, "url": url}


@app.get("/tg/delete_webhook")
async def delete_webhook():
    """Remove webhook and drop pending updates."""
    bot, _ = _get_bot_state()
    ok = await bot.delete_webhook(drop_pending_updates=True)
    return {"ok": ok}


@app.post("/tg/menu_button")
async def set_menu_button(admin_token: str):
    """Set a global menu button pointing to the Mini App (admin protected)."""
    if admin_token != os.environ.get("ADMIN_TOKEN", ""):
        raise HTTPException(status_code=403, detail="Forbidden")
    bot, _ = _get_bot_state()
    button = MenuButtonWebApp(
        text="AM Driving Test",
        web_app=WebAppInfo(url="https://www.drivingtest.space/")
    )
    ok = await bot.set_chat_menu_button(menu_button=button)
    return {"ok": ok}


@app.post("/auth/telegram")
async def auth_telegram(payload: dict = Body(...)):
    """Verify initData payload received from Telegram Mini App."""
    init_data = payload.get("initData", "")
    if not init_data:
        raise HTTPException(status_code=400, detail="initData required")
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    if not check_init_data(init_data, bot_token):
        raise HTTPException(status_code=401, detail="Invalid Telegram initData")
    user = extract_user(init_data)
    return {"ok": True, "user": user}
