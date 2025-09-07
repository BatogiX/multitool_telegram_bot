from __future__ import annotations

from typing import TYPE_CHECKING, Final

from models.callback_data import HashMenuCallbackData

from .util import RETURN_CHAR, create_button

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardButton

RETURN_TO_HASH_MENU_TEXT = "Back to Hash Menu"
RETRY_SAME_HASH_TEXT = "🔄️"


def btn_retry_same_hash(hash_type: str) -> InlineKeyboardButton:
    return create_button(
        text=RETRY_SAME_HASH_TEXT,
        callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type),
    )


def _btn_return_to_hash_menu() -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {RETURN_TO_HASH_MENU_TEXT}",
        callback_data=HashMenuCallbackData.Enter(),
    )


def _btns_hash() -> list[InlineKeyboardButton]:
    return [
        create_button(
            text=hash_type,
            callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type),
        )
        for hash_type in HashMenuCallbackData.HashTypes
    ]


BTN_RETURN_TO_HASH_MENU: Final[InlineKeyboardButton] = _btn_return_to_hash_menu()
BTNS_HASH: Final[list[InlineKeyboardButton]] = _btns_hash()
