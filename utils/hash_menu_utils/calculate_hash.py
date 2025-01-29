import hashlib
from enum import Enum

import aiofiles
from aiogram import types
from aiogram.fsm.context import FSMContext

from callback_data import HashMenu
from fsm import HashMenuStates
from utils import BotUtils


class CalculateHash(BotUtils):
    _DEFAULT_CHUNK_SIZE = 4096
    _STATE_TO_HASH_MAPPING = {
        HashMenuStates.MD5: HashMenu.hash_types.MD5,
        HashMenuStates.SHA1: HashMenu.hash_types.SHA1,
        HashMenuStates.SHA256: HashMenu.hash_types.SHA256,
    }
    _HASH_TO_FUNC_MAPPING = {
        HashMenu.hash_types.MD5: hashlib.md5,
        HashMenu.hash_types.SHA1: hashlib.sha1,
        HashMenu.hash_types.SHA256: hashlib.sha256,
    }


    @classmethod
    async def _compute_file_hash(cls, file_path: str, hash_obj, delete_file_after_processing: bool) -> str:
        """Asynchronously compute the file's hash."""
        try:
            async with aiofiles.open(file_path, "rb") as f:
                while chunk := await f.read(cls._DEFAULT_CHUNK_SIZE):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            raise RuntimeError(f"Failed to compute file hash: {e}")
        finally:
            if delete_file_after_processing:
                await cls._delete_file(file_path)

    @classmethod
    async def _calculate_file_hash(cls, file_path: str, hash_type: Enum, is_file_has_to_be_deleted: bool) -> str:
        """Calculate the file's hash based on the specified hash type."""
        hash_func = cls._HASH_TO_FUNC_MAPPING.get(hash_type) # noqa
        return await cls._compute_file_hash(file_path, hash_func(), is_file_has_to_be_deleted)

    @classmethod
    async def _get_file_path_and_hash(cls, message: types.Message) -> tuple[str, str, bool]:
        """
        Extract the file path and expected hash based on message content.
        :return: Tuple of (file_path, expected_hash, delete_file_after_processing).
        """
        temp_file_path = await cls.download_file(message)
        if not temp_file_path:
            raise RuntimeError("Failed to download the file.")
        expected_hash = (message.caption or "").casefold()
        return temp_file_path, expected_hash, True

    @classmethod
    async def _get_hash_type(cls, state: FSMContext) -> Enum:
        current_state = await state.get_state()
        return cls._STATE_TO_HASH_MAPPING.get(current_state)


    @classmethod
    async def check_hash(cls, state: FSMContext, message: types.Message) -> tuple[bool, str, str, str]:
        hash_type = await cls._get_hash_type(state)
        file_path, expected_hash, delete_file_after_processing = await cls._get_file_path_and_hash(message)
        await state.set_state(None)

        computed_hash = await cls._calculate_file_hash(file_path, hash_type, delete_file_after_processing)
        is_match = computed_hash == expected_hash

        return is_match, expected_hash, hash_type.value, computed_hash
