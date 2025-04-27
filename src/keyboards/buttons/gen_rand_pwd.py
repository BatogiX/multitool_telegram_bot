from aiogram.types import InlineKeyboardButton

from models.callback_data import GenerateRandomPasswordCallback
from utils.kb_utils import create_button

REGENERATE_RAND_PWD_TEXT = "🎲 Regenerate Password"


def _btn_regenerate_rand_pwd() -> InlineKeyboardButton:
    return create_button(
        text=REGENERATE_RAND_PWD_TEXT,
        callback_data=GenerateRandomPasswordCallback.Enter()
    )


btn_regenerate_rand_pwd: InlineKeyboardButton = _btn_regenerate_rand_pwd()
