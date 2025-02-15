from aiogram.types import InlineKeyboardMarkup

from utils.keyboards_utils import StartMenuKeyboardsUtils as SmUtil


class InlineStartMenuKeyboard:
    @staticmethod
    def start_menu_inline_keyboard() -> InlineKeyboardMarkup:
        hash_menu_button = SmUtil.gen_hash_menu_button()
        password_manager_button = SmUtil.gen_password_manager_button()

        return InlineKeyboardMarkup(inline_keyboard=[
            [hash_menu_button, password_manager_button],
        ])
