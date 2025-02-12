from enum import Enum

from aiogram.filters.callback_data import CallbackData


class StartMenuCallbackData(CallbackData, prefix="start_menu"):
    action: str

    class ACTIONS(str, Enum):
        ENTER = "enter"
