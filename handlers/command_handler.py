from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import text

from keyboards import InlineKeyboards

command_router = Router(name=__name__)


@command_router.message(CommandStart())
async def cmd_start(message: Message):
    inline_keyboard = InlineKeyboards.start_menu_inline_keyboard()
    await message.answer(text="Hello! I'm your friendly bot. How can I assist you today?", reply_markup=inline_keyboard)


@command_router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = text(
        "Here are some commands you can use:",
        "/start - Start the bot",
        "/help - Get help",
        sep="\n"
    )
    await message.answer(help_text)
