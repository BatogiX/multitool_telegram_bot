from aiogram.filters.callback_data import CallbackData

from config import bot_cfg


class GenerateRandomPasswordCallback:
    class Enter(CallbackData, prefix="generate_random_password", sep=bot_cfg.sep): ...
