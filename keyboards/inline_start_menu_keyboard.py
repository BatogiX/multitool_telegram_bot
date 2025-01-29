from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callback_data import HashMenu


class InlineStartMenuKeyboard:
    @staticmethod
    def start_menu_inline_keyboard() -> InlineKeyboardMarkup:
        hash_menu_button = InlineKeyboardButton(text="Check file's hash", callback_data=HashMenu(action=HashMenu.ACTIONS.ENTER).pack())

        return InlineKeyboardMarkup(inline_keyboard=[
            [hash_menu_button]
        ])