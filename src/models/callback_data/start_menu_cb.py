from enum import Enum

from aiogram.filters.callback_data import CallbackData

from config import bot_config as c


class StartMenuCallbackData(CallbackData, prefix="start_menu", sep=c.sep):
    action: str

    class ACTIONS(str, Enum):
        ENTER = "enter"
