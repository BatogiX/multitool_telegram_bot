import hashlib
from typing import Callable

import aiofiles
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from models.callback_data import HashMenuCallbackData
from models.fsm_states import HashMenuStates
from utils import BotUtils
from utils.fsm_data_utils import FSMDataUtils


class CalculateHash(BotUtils):
    _DEFAULT_CHUNK_SIZE: int = 4096
    _HASH_TO_STATE_MAPPING: dict[str, State] = {
        HashMenuCallbackData.hash_types.MD5: HashMenuStates.MD5,
        HashMenuCallbackData.hash_types.SHA1: HashMenuStates.SHA1,
        HashMenuCallbackData.hash_types.SHA256: HashMenuStates.SHA256,
    }
    _HASH_TO_FUNC_MAPPING: dict[str, Callable] = {
        HashMenuCallbackData.hash_types.MD5: hashlib.md5,
        HashMenuCallbackData.hash_types.SHA1: hashlib.sha1,
        HashMenuCallbackData.hash_types.SHA256: hashlib.sha256,
    }

    @classmethod
    async def _compute_file_hash(cls, file_path: str, hash_func: Callable) -> str | None:
        """Asynchronously compute the file's hash."""
        hash_obj = hash_func()
        try:
            async with aiofiles.open(file_path, "rb") as f:
                while chunk := await f.read(cls._DEFAULT_CHUNK_SIZE):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            raise RuntimeError(f"Failed to compute file hash: {e}")
        finally:
            await cls._delete_file(file_path)

    @classmethod
    async def _calculate_file_hash(cls, file_path: str, hash_type: str) -> str:
        """Calculate the file's hash based on the specified hash type."""
        hash_func = cls._HASH_TO_FUNC_MAPPING.get(hash_type)  # noqa
        return await cls._compute_file_hash(file_path, hash_func)

    @classmethod
    async def _get_file_path_and_hash(cls, message: types.Message) -> tuple[str, str]:
        """
        Extract the file path and expected hash based on message content.
        :return: Tuple of (file_path, expected_hash).
        """
        temp_file_path = await cls.download_file(message)
        if not temp_file_path:
            raise RuntimeError("Failed to download the file.")
        expected_hash = (message.caption or "").casefold()
        return temp_file_path, expected_hash

    @classmethod
    async def check_hash(cls, state: FSMContext, message: types.Message) -> tuple[bool, str, str, str]:
        hash_type: str = await FSMDataUtils.get_hash_type(state)
        file_path, expected_hash = await cls._get_file_path_and_hash(message)

        computed_hash = await cls._calculate_file_hash(file_path, hash_type)
        is_match = computed_hash == expected_hash

        return is_match, expected_hash, hash_type, computed_hash
