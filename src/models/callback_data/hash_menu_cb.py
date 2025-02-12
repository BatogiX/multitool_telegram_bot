from enum import Enum

from aiogram.filters.callback_data import CallbackData

from config import sep as sep

class HashMenuCallbackData(CallbackData, prefix="hash_menu", sep=sep):
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
