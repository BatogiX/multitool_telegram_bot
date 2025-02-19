from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils import InlineKeyboardsUtils as KbUtils


class InlineHashMenuKeyboard:
    @staticmethod
    def hash_menu() -> InlineKeyboardMarkup:
        hash_buttons: list[InlineKeyboardButton] = KbUtils.gen_hash_buttons()
        return_to_start_menu_button: InlineKeyboardButton = KbUtils.gen_return_to_start_menu_button()

        return InlineKeyboardMarkup(inline_keyboard=[
            hash_buttons,
            [return_to_start_menu_button]
        ])

    @staticmethod
    def return_to_hash_menu() -> InlineKeyboardMarkup:
        return_to_hash_menu_button: InlineKeyboardButton = KbUtils.gen_return_to_hash_menu_button()
        
        return InlineKeyboardMarkup(inline_keyboard=[[return_to_hash_menu_button]])

    @staticmethod
    def return_to_hash_menu_or_retry(hash_type: str) -> InlineKeyboardMarkup:
        return_to_hash_menu_button: InlineKeyboardButton = KbUtils.gen_return_to_hash_menu_button()
        retry_button: InlineKeyboardButton = KbUtils.gen_retry_same_hash_button(hash_type)

        return InlineKeyboardMarkup(inline_keyboard=[
            [return_to_hash_menu_button, retry_button]
        ])
