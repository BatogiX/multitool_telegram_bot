from aiogram.types import InlineKeyboardButton

from models.callback_data import HashMenuCallbackData
from utils.kb_utils import create_button, RETURN_CHAR

RETURN_TO_HASH_MENU_TEXT = "Back to Hash Menu"
RETRY_SAME_HASH_TEXT = "🔄️"


def btn_retry_same_hash(hash_type: str) -> InlineKeyboardButton:
    return create_button(
        text=RETRY_SAME_HASH_TEXT,
        callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type)
    )


def _btn_return_to_hash_menu() -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {RETURN_TO_HASH_MENU_TEXT}",
        callback_data=HashMenuCallbackData.Enter()
    )


def _btns_hash() -> list[InlineKeyboardButton]:
    return [
        create_button(
            text=hash_type, callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type)
        )
        for hash_type in HashMenuCallbackData.hash_types
    ]


btn_return_to_hash_menu: InlineKeyboardButton = _btn_return_to_hash_menu()
btns_hash: list[InlineKeyboardButton] = _btns_hash()
