from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.callback_data import HashMenuCallbackData
from utils.keyboards_utils import KeyboardsUtils as kbUtil


class InlineHashMenuKeyboard:
    @staticmethod
    def hash_menu_keyboard() -> InlineKeyboardMarkup:
        hash_buttons: list[InlineKeyboardButton] = kbUtil.gen_hash_buttons()
        return_to_start_menu_button = kbUtil.gen_return_to_start_menu_button()
        return InlineKeyboardMarkup(inline_keyboard=[
            hash_buttons,
            [return_to_start_menu_button]
        ])

    @staticmethod
    def return_to_hash_menu_keyboard() -> InlineKeyboardMarkup:
        return_to_hash_menu_button = kbUtil.gen_return_to_hash_menu_button()
        return InlineKeyboardMarkup(inline_keyboard=[[return_to_hash_menu_button]])

    @staticmethod
    def return_to_hash_menu_or_retry_keyboard(hash_type: str) -> InlineKeyboardMarkup:
        return_to_hash_menu_button = kbUtil.gen_return_to_hash_menu_button()
        retry_button = kbUtil.gen_retry_same_hash_button(hash_type)

        return InlineKeyboardMarkup(inline_keyboard=[
            [return_to_hash_menu_button, retry_button]
        ])
