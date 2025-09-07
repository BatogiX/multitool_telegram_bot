from aiogram.filters.callback_data import CallbackData

from config import BOT_CFG


class StartMenuCallbackData:
    class Enter(CallbackData, prefix="start_menu_enter", sep=BOT_CFG.sep): ...
