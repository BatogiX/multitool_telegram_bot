from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from helpers import GenerateRandomPasswordHelper
from models.callback_data import GeneratePasswordCallback
from utils import InlineKeyboardsUtils

callback_router = Router(name=__name__)


@callback_router.callback_query(GeneratePasswordCallback.Enter.filter())
async def generate_random_password(callback_query: CallbackQuery):
    rand_pwd = GenerateRandomPasswordHelper.generate_password()

    await callback_query.message.edit_text(
        text=f"`{rand_pwd}`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardsUtils.gen_return_to_start_menu_button()]]),
        parse_mode="MarkdownV2"
    )
