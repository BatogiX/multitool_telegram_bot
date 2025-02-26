from aiogram import Router
from aiogram.types import CallbackQuery

from keyboards import Keyboards
from models.callback_data import StartMenuCallbackData

callback_router = Router(name=__name__)


@callback_router.callback_query(StartMenuCallbackData.Enter.filter())
async def return_to_start_menu_from_another_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        text="Hello! I'm your friendly bot. How can I assist you today?",
        reply_markup=Keyboards.inline.start_menu()
    )
