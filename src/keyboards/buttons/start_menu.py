from __future__ import annotations

from typing import TYPE_CHECKING, Final

from models.callback_data import (
    GenerateRandomPasswordCallback,
    HashMenuCallbackData,
    StartMenuCallbackData,
)
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb

from .util import RETURN_CHAR, create_button

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardButton

return_to_start_menu_text = "Back to Main Menu"
hash_menu_text = "🔍 Verify File's Checksum"
passw_manager_text = "🔐 Password manager"
generate_random_passw_text = "🎲 Generate Password"


def _btn_hash_menu() -> InlineKeyboardButton:
    return create_button(
        text=hash_menu_text,
        callback_data=HashMenuCallbackData.Enter(),
    )


def _btn_password_manager_menu() -> InlineKeyboardButton:
    return create_button(
        text=passw_manager_text,
        callback_data=PwdMgrCb.Enter(),
    )


def _btn_return_to_start_menu() -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {return_to_start_menu_text}",
        callback_data=StartMenuCallbackData.Enter(),
    )


def _btn_generate_random_password() -> InlineKeyboardButton:
    return create_button(
        text=generate_random_passw_text,
        callback_data=GenerateRandomPasswordCallback.Enter(),
    )


BTN_HASH_MENU: Final[InlineKeyboardButton] = _btn_hash_menu()
BTN_PASSWORD_MANAGER_MENU: Final[InlineKeyboardButton] = _btn_password_manager_menu()
BTN_RETURN_TO_START_MENU: Final[InlineKeyboardButton] = _btn_return_to_start_menu()
BTN_GENERATE_RANDOM_PASSWORD: Final[InlineKeyboardButton] = _btn_generate_random_password()
