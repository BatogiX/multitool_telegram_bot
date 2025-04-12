from aiogram.types import InlineKeyboardMarkup

from helpers.keyboard_helper import gen_return_to_start_menu_button, gen_regenerate_rand_pwd_button


def gen_rand_pwd() -> InlineKeyboardMarkup:
    return_to_start_menu_button = gen_return_to_start_menu_button()
    regenerate_rand_pwd_button = gen_regenerate_rand_pwd_button()

    return InlineKeyboardMarkup(inline_keyboard=[
        [return_to_start_menu_button, regenerate_rand_pwd_button]
    ])
