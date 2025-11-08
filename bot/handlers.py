"""Aiogram message handlers for AM Driving Test bot."""
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

router = Router()

@router.message(F.text == "/start")
async def handle_start(message: types.Message) -> None:
    """Send inline button that opens the Mini App."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Open AM Driving Test",
                    web_app=WebAppInfo(url="https://www.drivingtest.space/")
                )
            ]
        ]
    )
    await message.answer("Tap to launch the Mini App:", reply_markup=keyboard)
