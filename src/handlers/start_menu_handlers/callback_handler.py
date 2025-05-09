from aiogram import Router
from aiogram.types import CallbackQuery, Message

import keyboards.inline
from models.callback_data import StartMenuCallbackData

callback_router = Router(name=__name__)


@callback_router.callback_query(StartMenuCallbackData.Enter.filter())
async def return_to_start_menu_from_another_menu(callback_query: CallbackQuery) -> Message:
    return await callback_query.message.edit_text(
        text="Hello! I'm your friendly bot. How can I assist you today?",
        reply_markup=keyboards.inline.start_menu_ikm
    )
