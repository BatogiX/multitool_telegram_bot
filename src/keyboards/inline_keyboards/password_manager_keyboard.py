from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.passwords_record import DecryptedRecord
from utils.keyboards_utils import PasswordManagerKeyboardsUtils as PmUtil
from utils.keyboards_utils import StartMenuKeyboardsUtils as SmUtil


class InlinePasswordManagerKeyboard:
    @classmethod
    def passwd_man_services(cls, services: list[str] | None, offset: int) -> InlineKeyboardMarkup:
        next_page_button: InlineKeyboardButton | None = PmUtil.gen_next_page_services_button(services, offset)
        service_buttons_rows: list[list[InlineKeyboardButton]] | None = PmUtil.gen_service_buttons(services)
        return_to_start_menu_button: InlineKeyboardButton = SmUtil.gen_return_to_start_menu_button()
        create_new_service_button: InlineKeyboardButton = PmUtil.gen_create_service_button(offset)
        delete_services_button: InlineKeyboardButton | None = PmUtil.gen_delete_services_button(services, offset)
        previous_page_button: InlineKeyboardButton | None = PmUtil.gen_previous_page_services_button(offset)

        action_buttons_row: list[InlineKeyboardButton] = [
            button for button in [create_new_service_button, delete_services_button] if button
        ]
        navigation_buttons_row: list[InlineKeyboardButton] = [
            button for button in [previous_page_button, return_to_start_menu_button, next_page_button] if button
        ]

        return InlineKeyboardMarkup(
            inline_keyboard=
            [
                *service_buttons_rows,
                action_buttons_row,
                navigation_buttons_row
            ]
        )

    @classmethod
    def passwd_man_passwords(
            cls,
            decrypted_records: list[DecryptedRecord],
            service: str,
            pwd_offset: int,
            services_offset: int
    ) -> InlineKeyboardMarkup:
        next_page_button: InlineKeyboardButton | None = PmUtil.gen_next_page_passwords_button(decrypted_records, pwd_offset, service)
        password_buttons_rows: list[list[InlineKeyboardButton]] = PmUtil.gen_password_buttons(decrypted_records)
        change_service_name_button: InlineKeyboardButton = PmUtil.gen_change_service_button(service)
        delete_service_button: InlineKeyboardButton = PmUtil.gen_delete_service_button(service)
        return_to_passwd_man_button: InlineKeyboardButton = PmUtil.gen_return_to_passwd_man_button(services_offset)
        create_new_password_button: InlineKeyboardButton = PmUtil.gen_create_password_button(service)
        previous_page_button: InlineKeyboardButton | None = PmUtil.gen_previous_page_passwords_button(pwd_offset, service)

        navigation_buttons_row: list[InlineKeyboardButton] = [
            button for button in [previous_page_button, return_to_passwd_man_button, next_page_button] if button
        ]

        return InlineKeyboardMarkup(inline_keyboard=[
            *password_buttons_rows,
            [change_service_name_button],
            [create_new_password_button, delete_service_button],
            navigation_buttons_row,
        ])

    @classmethod
    def return_to_passwd_man(cls, offset) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[PmUtil.gen_return_to_passwd_man_button(offset)]])

    @classmethod
    def passwd_man_password(cls, offset: int, service: str) -> InlineKeyboardMarkup:
        return_to_passwd_man_button = PmUtil.gen_return_to_passwd_man_button(offset)
        delete_password_button = PmUtil.gen_delete_password_button(service)

        return InlineKeyboardMarkup(inline_keyboard=[
            [delete_password_button],
            [return_to_passwd_man_button]
        ])
