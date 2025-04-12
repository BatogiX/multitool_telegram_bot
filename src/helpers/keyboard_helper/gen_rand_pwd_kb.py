from aiogram.types import InlineKeyboardButton

from models.callback_data import GenerateRandomPasswordCallback
from utils.kb_utils import create_button

REGENERATE_RAND_PWD_TEXT = "🎲 Regenerate Password"


def gen_regenerate_rand_pwd_button() -> InlineKeyboardButton:
    return create_button(
        text=REGENERATE_RAND_PWD_TEXT,
        callback_data=GenerateRandomPasswordCallback.Enter()
    )
