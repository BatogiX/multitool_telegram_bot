import re

from aiofiles import os
from aiogram import types
from aiogram.exceptions import TelegramBadRequest


async def download_file(message: types.Message) -> str:
    """
    Downloads a file from Telegram and returns it's path.

    :param message: Message object.
    :return: Path to the downloaded file.
    """
    if message.document:
        file_id = message.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:
        file_id = message.audio.file_id
    else:
        raise Exception("Unsupported file type.")

    temp_file_path = f"temp_{file_id}"
    file = await message.bot.get_file(file_id)
    if not file:
        raise Exception("Only files up to 50MB are supported.")
    file_path = file.file_path
    await message.bot.download_file(file_path=file_path, destination=temp_file_path)
    return temp_file_path


async def delete_file(file_path: str) -> None:
    await os.remove(file_path)


async def delete_fsm_message(message_id: int, message: types.Message) -> None:
    """Deletes message by message_id that stores in FSM-data."""
    try:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    except TelegramBadRequest:
        pass


def escape_markdown_v2(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


def strip_protocol(service: str) -> str:
    return re.sub(r"^(https?://)|(www\.)", "", service)


def add_protocol(service: str) -> str:
    return f"https://{service}"
