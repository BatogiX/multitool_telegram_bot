from aiogram.filters.callback_data import CallbackData

from config import BOT_CFG


class GenerateRandomPasswordCallback:
    class Enter(CallbackData, prefix="generate_random_password", sep=BOT_CFG.sep): ...
