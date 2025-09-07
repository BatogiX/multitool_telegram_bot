from __future__ import annotations

from aiogram import Router
from aiogram.types import CallbackQuery, Message

from keyboards.inline import START_MENU_IKM
from models.callback_data import StartMenuCallbackData

callback_router = Router(name=__name__)


@callback_router.callback_query(StartMenuCallbackData.Enter.filter())
async def return_to_start_menu_from_another_menu(callback_query: CallbackQuery) -> None:
    if isinstance(callback_query.message, Message):
        await callback_query.message.edit_text(
            text="Hello! I'm your friendly bot. How can I assist you today?",
            reply_markup=START_MENU_IKM,
        )
