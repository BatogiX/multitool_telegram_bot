from aiogram.types import InlineKeyboardMarkup

from keyboards.buttons import start_menu


def _start_menu_ikm() -> InlineKeyboardMarkup:
    btn_hash_menu = start_menu.btn_hash_menu
    btn_password_manager_menu = start_menu.btn_password_manager_menu
    btn_generate_random_password = start_menu.btn_generate_random_password

    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_hash_menu, btn_password_manager_menu],
        [btn_generate_random_password]
    ])


start_menu_ikm: InlineKeyboardMarkup = _start_menu_ikm()
