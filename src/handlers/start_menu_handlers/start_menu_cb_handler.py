from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import InlineKeyboards
from utils.filters import CbMagicFilters

callback_router = Router(name=__name__)


@callback_router.callback_query(CbMagicFilters.StartMenu_ENTER(F.data))
async def return_to_start_menu_from_another_menu(callback_query: CallbackQuery):
    inline_kb = InlineKeyboards.start_menu_inline_keyboard()
    await callback_query.message.edit_text(text="Hello! I'm your friendly bot. How can I assist you today?",
                                           reply_markup=inline_kb)