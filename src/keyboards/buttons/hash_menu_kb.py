from aiogram.types import InlineKeyboardButton

from models.callback_data import HashMenuCallbackData
from utils.kb_utils import create_button, RETURN_CHAR

RETURN_TO_HASH_MENU_TEXT = "Back to Hash Menu"
RETRY_SAME_HASH_TEXT = "🔄️"


def gen_return_to_hash_menu_button() -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {RETURN_TO_HASH_MENU_TEXT}",
        callback_data=HashMenuCallbackData.Enter()
    )


def gen_retry_same_hash_button(hash_type: str) -> InlineKeyboardButton:
    return create_button(
        text=RETRY_SAME_HASH_TEXT,
        callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type)
    )


def gen_hash_buttons() -> list[InlineKeyboardButton]:
    return [
        create_button(
            text=hash_type, callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type)
        )
        for hash_type in HashMenuCallbackData.hash_types
    ]