from enum import StrEnum

from aiogram.filters.callback_data import CallbackData

from config import BOT_CFG


class HashMenuCallbackData:
    class Enter(CallbackData, prefix="hash_menu_enter", sep=BOT_CFG.sep): ...

    class Hashes(CallbackData, prefix="hash_menu_hashes", sep=BOT_CFG.sep):
        hash_type: str

    class HashTypes(StrEnum):
        MD5 = "MD5"
        SHA1 = "SHA-1"
        SHA256 = "SHA-256"
