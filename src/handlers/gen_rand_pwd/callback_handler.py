from aiogram import Router
from aiogram.types import CallbackQuery

from helpers import GenerateRandomPasswordHelper
from keyboards import Keyboards
from models.callback_data import GenerateRandomPasswordCallback

callback_router = Router(name=__name__)


@callback_router.callback_query(GenerateRandomPasswordCallback.Enter.filter())
async def generate_random_password(callback_query: CallbackQuery):
    rand_pwd = GenerateRandomPasswordHelper.generate_password()

    await callback_query.message.edit_text(
        text=f"`{rand_pwd}`",
        reply_markup=Keyboards.inline.gen_rand_pwd(),
        parse_mode="MarkdownV2"
    )
