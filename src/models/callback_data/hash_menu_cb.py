from enum import Enum

from aiogram.filters.callback_data import CallbackData

from config import bot_cfg


class HashMenuCallbackData:
    class Enter(CallbackData, prefix="hash_menu_enter", sep=bot_cfg.sep): ...

    class Hashes(CallbackData, prefix="hash_menu_hashes", sep=bot_cfg.sep):
        hash_type: str

    class hash_types(str, Enum):
        MD5 = "MD5"
        SHA1 = "SHA-1"
        SHA256 = "SHA-256"
