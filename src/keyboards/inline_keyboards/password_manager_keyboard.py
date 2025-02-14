from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.passwords_record import DecryptedRecord
from utils.keyboards_utils import KeyboardsUtils as kbUtil


class InlinePasswordManagerKeyboard:
    @classmethod
    def passwd_man_services(cls, services: list[str] | None, offset: int) -> InlineKeyboardMarkup:
        next_page_button: InlineKeyboardButton | None = kbUtil.gen_next_page_services_button(services, offset)
        service_buttons_rows: list[list[InlineKeyboardButton]] | None = kbUtil.gen_service_buttons(services)
        return_to_start_menu_button: InlineKeyboardButton = kbUtil.gen_return_to_start_menu_button()
        create_new_service_button: InlineKeyboardButton = kbUtil.gen_create_service_button(offset)
        delete_services_button: InlineKeyboardButton | None = kbUtil.gen_delete_services_button(services, offset)
        previous_page_button: InlineKeyboardButton | None = kbUtil.gen_previous_page_services_button(offset)

        action_buttons_row: list[InlineKeyboardButton] = [button for button in
                                                          [create_new_service_button, delete_services_button] if
                                                          button is not None]
        navigation_buttons_row: list[InlineKeyboardButton] = [button for button in
                                                              [previous_page_button, return_to_start_menu_button,
                                                               next_page_button] if button is not None]

        return InlineKeyboardMarkup(
            inline_keyboard=
            [
                *service_buttons_rows,
                action_buttons_row,
                navigation_buttons_row
            ]
        )

    @classmethod
    def passwd_man_passwords(cls, decrypted_records: list[DecryptedRecord], service: str,
                             offset: int) -> InlineKeyboardMarkup:
        next_page_button: InlineKeyboardButton | None = kbUtil.gen_next_page_passwords_button(decrypted_records, offset,
                                                                                              service)
        password_buttons_rows: list[list[InlineKeyboardButton]] = kbUtil.gen_password_buttons(decrypted_records)
        change_service_name_button: InlineKeyboardButton = kbUtil.gen_change_service_button(service)
        delete_service_button: InlineKeyboardButton = kbUtil.gen_delete_service_button(service)
        return_to_passwd_man_services_button: InlineKeyboardButton = kbUtil.gen_return_to_passwd_man_button(offset)
        create_new_password_button: InlineKeyboardButton = kbUtil.gen_create_password_button(service)
        previous_page_button: InlineKeyboardButton | None = kbUtil.gen_previous_page_passwords_button(offset, service)

        navigation_buttons_row: list[InlineKeyboardButton] = [button for button in [previous_page_button,
                                                                                    return_to_passwd_man_services_button,
                                                                                    next_page_button] if
                                                              button is not None]

        return InlineKeyboardMarkup(inline_keyboard=[
            *password_buttons_rows,
            [change_service_name_button],
            [create_new_password_button, delete_service_button],
            navigation_buttons_row,
        ])

    @classmethod
    def return_to_passwd_man(cls, offset) -> InlineKeyboardMarkup:
        return_to_passwd_man_button = kbUtil.gen_return_to_passwd_man_button(offset)

        return InlineKeyboardMarkup(inline_keyboard=[[return_to_passwd_man_button]])

    @classmethod
    def passwd_man_password(cls, offset: int) -> InlineKeyboardMarkup:
        return_to_passwd_man_button = kbUtil.gen_return_to_passwd_man_button(offset)
        delete_password_button = kbUtil.gen_delete_password_button(offset)

        return InlineKeyboardMarkup(inline_keyboard=[
            [delete_password_button],
            [return_to_passwd_man_button]
        ])
