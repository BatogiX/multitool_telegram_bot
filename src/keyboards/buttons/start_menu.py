from aiogram.types import InlineKeyboardButton

from models.callback_data import HashMenuCallbackData, StartMenuCallbackData, \
    PasswordManagerCallbackData as PwdMgrCb, \
    GenerateRandomPasswordCallback
from utils.kb_utils import create_button, RETURN_CHAR

return_to_start_menu_text = "Back to Main Menu"
hash_menu_text = "🔍 Verify File's Checksum"
password_manager_text = "🔐 Password manager"
generate_random_password_text = "🎲 Generate Password"


def _btn_hash_menu() -> InlineKeyboardButton:
    return create_button(
        text=hash_menu_text,
        callback_data=HashMenuCallbackData.Enter()
    )


def _btn_password_manager_menu() -> InlineKeyboardButton:
    return create_button(
        text=password_manager_text,
        callback_data=PwdMgrCb.Enter()
    )


def _btn_return_to_start_menu() -> InlineKeyboardButton:
    return create_button(
        text=f"{RETURN_CHAR} {return_to_start_menu_text}",
        callback_data=StartMenuCallbackData.Enter()
    )


def _btn_generate_random_password() -> InlineKeyboardButton:
    return create_button(
        text=generate_random_password_text,
        callback_data=GenerateRandomPasswordCallback.Enter()
    )


btn_hash_menu: InlineKeyboardButton = _btn_hash_menu()
btn_password_manager_menu: InlineKeyboardButton = _btn_password_manager_menu()
btn_return_to_start_menu: InlineKeyboardButton = _btn_return_to_start_menu()
btn_generate_random_password: InlineKeyboardButton = _btn_generate_random_password()
