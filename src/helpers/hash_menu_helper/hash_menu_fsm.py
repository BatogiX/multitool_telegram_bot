import hashlib
from typing import Callable

import aiofiles
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from database import db_manager
from models.callback_data import HashMenuCallbackData
from models.states import HashMenuStates
from utils import download_file, delete_file

DEFAULT_CHUNK_SIZE = 65536


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


def get_state_by_hash_type(hash_type: str) -> State:
    return _HASH_TO_STATE_MAPPING[hash_type]


async def _get_file_path_and_hash(message: types.Message) -> tuple[str, str]:
    """
    Extract the file path and expected hash based on message content.
    :return: Tuple of (file_path, expected_hash).
    """
    temp_file_path = await download_file(message)
    expected_hash = (message.caption or "").casefold()
    return temp_file_path, expected_hash


async def _calculate_file_hash(file_path: str, hash_type: str) -> str:
    """Calculate the file's hash based on the specified hash type."""
    hash_func = _HASH_TO_FUNC_MAPPING.get(hash_type)
    return await _compute_file_hash(file_path, hash_func)


async def _compute_file_hash(file_path: str, hash_func: Callable) -> str | None:
    """Asynchronously compute the file's hash."""
    hash_obj = hash_func()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(DEFAULT_CHUNK_SIZE):
            hash_obj.update(chunk)

    await delete_file(file_path)
    return hash_obj.hexdigest()


async def check_hash(state: FSMContext, message: types.Message) -> tuple[bool, str, str, str]:
    hash_type = await db_manager.key_value_db.get_hash_type(state)
    file_path, expected_hash = await _get_file_path_and_hash(message)

    computed_hash = await _calculate_file_hash(file_path, hash_type)
    is_match = computed_hash == expected_hash

    return is_match, expected_hash, hash_type, computed_hash
