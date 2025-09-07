from aiogram import Router
from aiogram.types import CallbackQuery, Message

import keyboards.inline
from helpers.gen_rand_pwd import generate_password
from models.callback_data import GenerateRandomPasswordCallback

callback_router = Router(name=__name__)


@callback_router.callback_query(GenerateRandomPasswordCallback.Enter.filter())
async def generate_random_password(callback_query: CallbackQuery) -> Message:
    rand_pwd = generate_password()

    return await callback_query.message.edit_text(
        text=f"`{rand_pwd}`",
        reply_markup=keyboards.inline.RAND_PWD_IKM,
        parse_mode="MarkdownV2",
    )
