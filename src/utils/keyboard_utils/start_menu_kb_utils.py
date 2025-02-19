from aiogram.types import InlineKeyboardButton

from models.callback_data import HashMenuCallbackData, StartMenuCallbackData, PasswordManagerCallbackData as PwManCb
from .kb_utils import KeyboardsUtils


class StartMenuKeyboardsUtils(KeyboardsUtils):
    return_to_start_menu_text = "Back to Main Menu"
    hash_menu_text = "🔍 Verify file's hash"
    password_manager_text = "🔐 Password manager"

    @classmethod
    def gen_hash_menu_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.hash_menu_text,
            callback_data=HashMenuCallbackData.Enter()
        )

    @classmethod
    def gen_password_manager_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=cls.password_manager_text,
            callback_data=PwManCb.Enter()
        )

    @classmethod
    def gen_return_to_start_menu_button(cls) -> InlineKeyboardButton:
        return cls._create_button(
            text=f"{cls.return_char} {cls.return_to_start_menu_text}",
            callback_data=StartMenuCallbackData.Enter()
        )