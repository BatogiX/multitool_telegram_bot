from aiogram.types import InlineKeyboardMarkup

from keyboards.buttons import hash_menu, start_menu


def _hash_menu_ikm() -> InlineKeyboardMarkup:
    btns_hash = hash_menu.btns_hash
    btn_return_to_start_menu = start_menu.btn_return_to_start_menu

    return InlineKeyboardMarkup(
        inline_keyboard=[
            btns_hash,
            [btn_return_to_start_menu]
        ]
    )


def _return_to_hash_menu_ikm() -> InlineKeyboardMarkup:
    btn_return_to_hash_menu = hash_menu.btn_return_to_hash_menu

    return InlineKeyboardMarkup(inline_keyboard=[[btn_return_to_hash_menu]])


def return_to_hash_menu_or_retry_ikm(hash_type: str) -> InlineKeyboardMarkup:
    btn_return_to_hash_menu = hash_menu.btn_return_to_hash_menu
    btn_retry_same_hash = hash_menu.btn_retry_same_hash(hash_type)

    return InlineKeyboardMarkup(inline_keyboard=[
        [btn_return_to_hash_menu, btn_retry_same_hash]
    ])


hash_menu_ikm: InlineKeyboardMarkup = _hash_menu_ikm()
return_to_hash_menu_ikm: InlineKeyboardMarkup = _return_to_hash_menu_ikm()