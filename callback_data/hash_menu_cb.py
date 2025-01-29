from enum import Enum

from aiogram.filters.callback_data import CallbackData


class HashMenu(CallbackData, prefix="hash_menu"):
    action: str

    class hash_types(str, Enum):
        MD5 = "MD5"
        SHA1 = "SHA-1"
        SHA256 = "SHA-256"

    class ACTIONS(str, Enum):
        ENTER = "enter"
        MD5 = "MD5"
        SHA1 = "SHA-1"
        SHA256 = "SHA-256"
