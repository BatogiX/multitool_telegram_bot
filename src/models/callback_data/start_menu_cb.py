from aiogram.filters.callback_data import CallbackData

from config import bot_cfg


class StartMenuCallbackData:
    class Enter(CallbackData, prefix="start_menu_enter", sep=bot_cfg.sep): ...
