from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import text

from database import db
from keyboards.inline import START_MENU_IKM

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

logger = logging.getLogger(__name__)
command_router = Router(name=__name__)


@command_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    if message.from_user and not await db.nosql.execute(db.nosql.get_cache_user_created(), storage_key=state.key):
        user_exists = await db.sql.execute(
            db.sql.create_user_if_not_exists(
                message.from_user.id,
                message.from_user.username,
                message.from_user.full_name,
            )
        )

        if user_exists:
            logger.info("New user created: %s", message.message_id)

        await db.nosql.execute(db.nosql.set_cache_user_created(), storage_key=state.key)

    await message.answer(
        text="Hello! I'm your friendly bot. How can I assist you today?",
        reply_markup=START_MENU_IKM,
    )


@command_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = text(
        "Here are some commands you can use:",
        "/start - Start the bot",
        "/help - Get help",
        sep="\n",
    )
    await message.answer(help_text)
