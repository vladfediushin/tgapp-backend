"""Bot/dispatcher wiring helpers."""
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from .handlers import router as handlers_router


def get_bot_and_dispatcher():
    """Instantiate aiogram Bot and Dispatcher and register handlers."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    bot = Bot(token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(handlers_router)
    return bot, dp
