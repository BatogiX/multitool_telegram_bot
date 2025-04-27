from aiogram.types import InlineKeyboardMarkup

from keyboards.buttons import gen_rand_pwd, start_menu


def _rand_pwd_ikm() -> InlineKeyboardMarkup:
    btn_return_to_start_menu = start_menu.btn_return_to_start_menu
    btn_regenerate_rand_pwd = gen_rand_pwd.btn_regenerate_rand_pwd

    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_return_to_start_menu, btn_regenerate_rand_pwd]
    ])


rand_pwd_ikm: InlineKeyboardMarkup = _rand_pwd_ikm()
