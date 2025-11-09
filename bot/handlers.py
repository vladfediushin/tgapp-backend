"""Aiogram message handlers for AM Driving Test bot."""
from __future__ import annotations

from typing import Set

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

router = Router()

ADMIN_USER_ID = 164441065  # Vlad (@quilongo)
feedback_waiting: Set[int] = set()


def _start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Open AM Driving Test",
                    web_app=WebAppInfo(url="https://www.drivingtest.space/")
                )
            ],
            [
                InlineKeyboardButton(
                    text="About the app",
                    callback_data="about_app"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Feedback / report an issue",
                    callback_data="feedback"
                )
            ],
        ]
    )


@router.message(CommandStart())
async def handle_start(message: types.Message) -> None:
    """Send inline buttons for the Mini App, about, and feedback."""
    await message.answer(
        "Choose an option:",
        reply_markup=_start_keyboard()
    )


@router.callback_query(F.data == "about_app")
async def handle_about(callback: types.CallbackQuery) -> None:
    """Provide short description about the Mini App."""
    text = (
        "AM Driving Test helps you prepare for the Armenian driving theory exam. "
        "Track progress, review mistakes, and keep practicing directly inside Telegram."
    )
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "feedback")
async def handle_feedback_request(callback: types.CallbackQuery) -> None:
    """Ask user to type their feedback."""
    user_id = callback.from_user.id
    feedback_waiting.add(user_id)
    await callback.message.answer("Write a feedback message and send it here.")
    await callback.answer()


@router.message(F.text)
async def handle_feedback_message(message: types.Message) -> None:
    """Collect feedback messages when the user is in feedback mode."""
    user_id = message.from_user.id
    if user_id not in feedback_waiting:
        return

    feedback_waiting.discard(user_id)
    user = message.from_user
    profile = f"{user.full_name} (@{user.username})" if user.username else user.full_name
    admin_text = (
        f"📩 Feedback from {profile}\n"
        f"ID: {user.id}\n\n"
        f"{message.text}"
    )
    await message.bot.send_message(ADMIN_USER_ID, admin_text)
    await message.answer("Thanks, your feedback was delivered.")
