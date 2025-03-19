from aiogram.types import InlineKeyboardMarkup

from utils import InlineKeyboardsUtils as KbUtils


class InlineGenerateRandomPasswordKeyboard:
    @staticmethod
    def gen_rand_pwd() -> InlineKeyboardMarkup:
        return_to_start_menu_button = KbUtils.gen_return_to_start_menu_button()
        regenerate_rand_pwd_button = KbUtils.gen_regenerate_rand_pwd_button()

        return InlineKeyboardMarkup(inline_keyboard=[
            [return_to_start_menu_button, regenerate_rand_pwd_button]
        ])
