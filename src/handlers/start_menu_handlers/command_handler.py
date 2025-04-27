import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import text

from database import db
import keyboards.inline

command_router = Router(name=__name__)


@command_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> Message:
    asyncio.create_task(db.relational.create_user_if_not_exists(
        user_id=message.from_user.id,
        user_name=message.from_user.username,
        full_name=message.from_user.full_name,
        state=state
    ))
    return await message.answer(
        text="Hello! I'm your friendly bot. How can I assist you today?",
        reply_markup=keyboards.inline.start_menu_ikm
    )


@command_router.message(Command("help"))
async def cmd_help(message: Message) -> Message:
    help_text = text(
        "Here are some commands you can use:",
        "/start - Start the bot",
        "/help - Get help",
        sep="\n"
    )
    return await message.answer(help_text)
