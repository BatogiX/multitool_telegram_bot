from __future__ import annotations

import contextlib
import re
from typing import TYPE_CHECKING

from aiofiles import os
from aiogram.exceptions import TelegramBadRequest

if TYPE_CHECKING:
    from aiogram.types import Message


async def download_file(message: Message) -> str:
    """
    Downloads a file from Telegram and returns it's path.

    :param message: Message object.
    :return: Path to the downloaded file.
    """
    if not message.bot:
        msg = "There is no bot instance"
        raise Exception(msg)

    if message.document:
        file_id = message.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id
    else:
        msg = "Unsupported file type."
        raise Exception(msg)

    temp_file_path = f"temp_{file_id}"
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    if not file_path:
        msg = "Only files up to 50MB are supported."
        raise Exception(msg)

    await message.bot.download_file(file_path=file_path, destination=temp_file_path)
    return temp_file_path


async def delete_file(file_path: str) -> None:
    await os.remove(file_path)


async def delete_fsm_message(message_id: int, message: Message) -> None:
    """Deletes message by message_id that stores in FSM-data."""
    if not message.bot:
        msg = "There is no bot instance"
        raise Exception(msg)

    with contextlib.suppress(TelegramBadRequest):
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)


def escape_markdown_v2(text: str) -> str:
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", text)


def strip_protocol(service: str) -> str:
    return re.sub(r"^(https?://)|(www\.)", "", service)


def add_protocol(service: str) -> str:
    return f"https://{service}"
