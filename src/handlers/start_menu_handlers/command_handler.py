from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import text

from config import db_manager
from keyboards import InlineKeyboards
from helpers import PasswordManagerHelper as PwdMgrHelper

command_router = Router(name=__name__)


@command_router.message(CommandStart())
async def cmd_start(message: Message):
    await db_manager.relational_db.create_user_if_not_exists(
        user_id=message.from_user.id,
        user_name=message.from_user.username,
        full_name=message.from_user.full_name,
        salt=PwdMgrHelper.gen_salt()
    )

    await message.answer(
        text="Hello! I'm your friendly bot. How can I assist you today?",
        reply_markup=InlineKeyboards.start_menu()
    )


@command_router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = text(
        "Here are some commands you can use:",
        "/start - Start the bot",
        "/help - Get help",
        sep="\n"
    )
    await message.answer(help_text)
