from aiogram.types import InlineKeyboardButton

from models.callback_data import HashMenuCallbackData, StartMenuCallbackData, PasswordManagerCallbackData as PwdMgrCb, \
    GenerateRandomPasswordCallback
from utils.kb_utils import create_button

return_to_start_menu_text = "Back to Main Menu"
hash_menu_text = "🔍 Verify File's Checksum"
password_manager_text = "🔐 Password manager"
generate_random_password_text = "🎲 Generate Password"


def gen_hash_menu_button() -> InlineKeyboardButton:
    return create_button(
        text=hash_menu_text,
        callback_data=HashMenuCallbackData.Enter()
    )


def gen_password_manager_button() -> InlineKeyboardButton:
    return create_button(
        text=password_manager_text,
        callback_data=PwdMgrCb.Enter()
    )


def gen_return_to_start_menu_button() -> InlineKeyboardButton:
    return create_button(
        text=f"{return_char} {return_to_start_menu_text}",
        callback_data=StartMenuCallbackData.Enter()
    )


def gen_generate_random_password_button() -> InlineKeyboardButton:
    return create_button(
        text=generate_random_password_text,
        callback_data=GenerateRandomPasswordCallback.Enter()
    )