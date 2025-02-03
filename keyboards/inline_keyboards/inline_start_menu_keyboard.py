from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callback_data import HashMenuCallbackData, PasswordManagerCallbackData


class InlineStartMenuKeyboard:
    @staticmethod
    def start_menu_inline_keyboard() -> InlineKeyboardMarkup:
        hash_menu_button = InlineKeyboardButton(text="Check file's hash", callback_data=HashMenuCallbackData(action=HashMenuCallbackData.ACTIONS.ENTER).pack())
        password_manager_button = InlineKeyboardButton(text="Password manager", callback_data=PasswordManagerCallbackData(action=PasswordManagerCallbackData.ACTIONS.ENTER).pack())

        return InlineKeyboardMarkup(inline_keyboard=[
            [hash_menu_button, password_manager_button],
        ])