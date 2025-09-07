from __future__ import annotations

from typing import TYPE_CHECKING, Final

from models.callback_data import GenerateRandomPasswordCallback

from .util import create_button

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardButton

REGENERATE_RAND_PASSW_TEXT = "🎲 Regenerate Password"


def _btn_regenerate_rand_pwd() -> InlineKeyboardButton:
    return create_button(
        text=REGENERATE_RAND_PASSW_TEXT,
        callback_data=GenerateRandomPasswordCallback.Enter(),
    )


BTN_REGENERATE_RAND_PWD: Final[InlineKeyboardButton] = _btn_regenerate_rand_pwd()
