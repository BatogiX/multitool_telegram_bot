from aiogram.types import InlineKeyboardMarkup

from utils import InlineKeyboardsUtils as KbUtils


class InlineStartMenuKeyboard:
    @staticmethod
    def start_menu() -> InlineKeyboardMarkup:
        hash_menu_button = KbUtils.gen_hash_menu_button()
        password_manager_button = KbUtils.gen_password_manager_button()
        generate_password_button = KbUtils.gen_generate_random_password_button()

        return InlineKeyboardMarkup(inline_keyboard=[
            [hash_menu_button, password_manager_button],
            [generate_password_button]
        ])
