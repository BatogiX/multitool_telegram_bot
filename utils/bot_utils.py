from aiofiles import os
from aiogram import types


class BotUtils:
    @staticmethod
    async def download_file(message: types.Message) -> str | None:
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
            await message.answer("File's format not supported.")
            return

        temp_file_path = f"temp_{file_id}"
        file = await message.bot.get_file(file_id)
        if not file:
            await message.answer("File's size not supported.")
            return
        file_path = file.file_path
        await message.bot.download_file(file_path=file_path, destination=temp_file_path)
        return temp_file_path

    @staticmethod
    async def _delete_file(file_path) -> None:
        await os.remove(file_path)

    @staticmethod
    async def delete_fsm_message(state, message: types.Message) -> None:
        message_id_to_delete = await state.get_data()
        message_id_to_delete = message_id_to_delete.get("message_to_delete")
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id_to_delete)

