"""Aiogram message handlers for AM Driving Test bot."""
from __future__ import annotations

import logging
from typing import Dict

from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import User
from bot.locales import get_message, supported_languages

router = Router()

ADMIN_USER_ID = 164441065  # Vlad (@quilongo)
feedback_waiting: Dict[int, str] = {}
SUPPORTED_LANGS = supported_languages()
DEFAULT_LANG = 'en'


async def resolve_locale(user: types.User | None) -> str:
    lang: str | None = None
    if user:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.telegram_id == user.id))
                db_user = result.scalars().first()
                if db_user:
                    lang = db_user.ui_language or db_user.exam_language
        except Exception as exc:
            logging.getLogger(__name__).warning("Failed to load user locale: %s", exc)

        if not lang and user.language_code:
            raw = user.language_code.split('-')[0]
            if raw in SUPPORTED_LANGS:
                lang = raw

    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def _start_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_message(lang, "button_open_app"),
                    web_app=WebAppInfo(url="https://www.drivingtest.space/")
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_message(lang, "button_about"),
                    callback_data="about_app"
                )
            ],
            [
                InlineKeyboardButton(
                    text=get_message(lang, "button_feedback"),
                    callback_data="feedback"
                )
            ],
        ]
    )


@router.message(CommandStart())
async def handle_start(message: types.Message) -> None:
    """Send inline buttons for the Mini App, about, and feedback."""
    lang = await resolve_locale(message.from_user)
    await message.answer(
        get_message(lang, "start_prompt"),
        reply_markup=_start_keyboard(lang)
    )


@router.callback_query(F.data == "about_app")
async def handle_about(callback: types.CallbackQuery) -> None:
    """Provide short description about the Mini App."""
    lang = await resolve_locale(callback.from_user)
    await callback.message.answer(get_message(lang, "about_text"))
    await callback.answer()


@router.callback_query(F.data == "feedback")
async def handle_feedback_request(callback: types.CallbackQuery) -> None:
    """Ask user to type their feedback."""
    user_id = callback.from_user.id
    lang = await resolve_locale(callback.from_user)
    feedback_waiting[user_id] = lang
    await callback.message.answer(get_message(lang, "feedback_prompt"))
    await callback.answer()


@router.message(F.text)
async def handle_feedback_message(message: types.Message) -> None:
    """Collect feedback messages when the user is in feedback mode."""
    user_id = message.from_user.id
    lang = feedback_waiting.get(user_id)
    if not lang:
        return
    feedback_waiting.pop(user_id, None)
    user = message.from_user
    profile = f"{user.full_name} (@{user.username})" if user.username else user.full_name
    admin_text = get_message(
        lang,
        "admin_feedback",
        profile=profile,
        user_id=user.id,
        message=message.text
    )
    await message.bot.send_message(ADMIN_USER_ID, admin_text)
    await message.answer(get_message(lang, "feedback_thanks"))


@router.message(Command("about"))
async def command_about(message: types.Message) -> None:
    lang = await resolve_locale(message.from_user)
    await message.answer(get_message(lang, "about_text"))


@router.message(Command("feedback"))
async def command_feedback(message: types.Message) -> None:
    user_id = message.from_user.id
    lang = await resolve_locale(message.from_user)
    feedback_waiting[user_id] = lang
    await message.answer(get_message(lang, "feedback_prompt"))
