from aiogram.types import InlineKeyboardButton

from models.callback_data import HashMenuCallbackData
from .kb_utils import KeyboardsUtils

class HashMenuKeyboardsUtils(KeyboardsUtils):
    return_to_hash_menu_text = "Back to Hash Menu"
    retry_same_hash_char = "🔄️"

    @classmethod
    def gen_return_to_hash_menu_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {cls.return_to_hash_menu_text}",
            callback_data=HashMenuCallbackData.Enter()
        )

    @classmethod
    def gen_retry_same_hash_button(cls, hash_type: str) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.retry_same_hash_char,
            callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type)
        )

    @classmethod
    def gen_hash_buttons(cls) -> list[InlineKeyboardButton]:
        return [
            cls._create_button(
                text=hash_type, callback_data=HashMenuCallbackData.Hashes(hash_type=hash_type)
            )
            for hash_type in HashMenuCallbackData.hash_types
        ]