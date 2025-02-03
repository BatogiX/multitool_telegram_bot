from enum import Enum

from aiogram.filters.callback_data import CallbackData


class PasswordManagerCallbackData(CallbackData, prefix="password_manager"):
    action: str

    class ACTIONS(str, Enum):
        ENTER = "enter"
