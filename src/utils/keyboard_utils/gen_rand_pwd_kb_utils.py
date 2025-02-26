from aiogram.types import InlineKeyboardButton

from models.callback_data import GenerateRandomPasswordCallback
from .kb_utils import KeyboardsUtils


class GenerateRandomPasswordKeyboardsUtils(KeyboardsUtils):
    regenerate_rand_pwd = "🎲 Regenerate Password"

    @classmethod
    def gen_regenerate_rand_pwd_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.regenerate_rand_pwd,
            callback_data=GenerateRandomPasswordCallback.Enter()
        )
