from aiogram.types import InlineKeyboardMarkup

from helpers.keyboard_helper import (
    gen_hash_menu_button,
    gen_password_manager_button,
    gen_generate_random_password_button
)


def start_menu() -> InlineKeyboardMarkup:
    hash_menu_button = gen_hash_menu_button()
    password_manager_button = gen_password_manager_button()
    generate_password_button = gen_generate_random_password_button()

    return InlineKeyboardMarkup(inline_keyboard=[
        [hash_menu_button, password_manager_button],
        [generate_password_button]
    ])
