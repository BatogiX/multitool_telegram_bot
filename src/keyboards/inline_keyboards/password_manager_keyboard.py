from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.passwords_record import DecryptedRecord
from utils.keyboards_utils import KeyboardsUtils as kbUtil


class InlinePasswordManagerKeyboard:
    @classmethod
    def passwd_man_services(cls, services: list[str] = ()) -> InlineKeyboardMarkup:
        service_buttons: list[InlineKeyboardButton] = kbUtil.gen_service_buttons(services)
        return_to_start_menu_button = kbUtil.gen_return_to_start_menu_button()
        create_new_service_button = kbUtil.gen_create_service_button()
        delete_services_button = kbUtil.gen_delete_services_button(services)

        return InlineKeyboardMarkup(inline_keyboard=[
            service_buttons,
            delete_services_button,
            [return_to_start_menu_button, create_new_service_button]
        ])

    @classmethod
    def passwd_man_passwords(cls, decrypted_records: list[DecryptedRecord], service: str) -> InlineKeyboardMarkup:
        password_buttons: list[InlineKeyboardButton] = kbUtil.gen_password_buttons(decrypted_records)
        change_service_name_button = kbUtil.gen_change_service_button(service)
        delete_service_button = kbUtil.gen_delete_service_button(service)
        return_to_passwd_man_services_button = kbUtil.gen_return_to_passwd_man_button()
        create_new_password_button = kbUtil.gen_create_password_button(service)

        return InlineKeyboardMarkup(inline_keyboard=[
            password_buttons,
            [change_service_name_button],
            [delete_service_button],
            [return_to_passwd_man_services_button, create_new_password_button],
        ])

    @classmethod
    def return_to_passwd_man(cls) -> InlineKeyboardMarkup:
        return_to_passwd_man_button = kbUtil.gen_return_to_passwd_man_button()

        return InlineKeyboardMarkup(inline_keyboard=[[return_to_passwd_man_button]])

    @classmethod
    def passwd_man_password(cls) -> InlineKeyboardMarkup:
        return_to_passwd_man_button = kbUtil.gen_return_to_passwd_man_button()
        delete_password_button = kbUtil.gen_delete_password_button()

        return InlineKeyboardMarkup(inline_keyboard=[
            [delete_password_button],
            [return_to_passwd_man_button]
        ])
