from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from models.db_record.password_record import DecryptedRecord
from utils.keyboard_utils import PasswordManagerKeyboardsUtils as PmUtil
from utils.keyboard_utils import StartMenuKeyboardsUtils as SmUtil


class InlinePasswordManagerKeyboard:
    @classmethod
    def pwd_mgr_menu(cls):
        enter_services_button: InlineKeyboardButton = PmUtil.gen_enter_services_button()
        import_from_file_button: InlineKeyboardButton = PmUtil.gen_import_from_file_button()
        export_to_file_button: InlineKeyboardButton = PmUtil.gen_export_to_file_button()
        return_to_start_menu_button: InlineKeyboardButton = SmUtil.gen_return_to_start_menu_button()

        return InlineKeyboardMarkup(inline_keyboard=[
            [enter_services_button],
            [import_from_file_button, export_to_file_button],
            [return_to_start_menu_button]
        ])


    @classmethod
    def pwd_mgr_services(cls, services: list[str] | None, offset: int) -> InlineKeyboardMarkup:
        search_button = PmUtil.gen_search_button(services)
        next_page_button: InlineKeyboardButton | None = PmUtil.gen_next_page_services_button(services, offset)
        service_buttons_rows: list[list[InlineKeyboardButton]] | None = PmUtil.gen_service_buttons(services)
        return_to_pwd_mgr_button: InlineKeyboardButton = PmUtil.gen_return_to_pwd_mgr_button()
        create_new_service_button: InlineKeyboardButton = PmUtil.gen_create_service_button(offset)
        delete_services_button: InlineKeyboardButton | None = PmUtil.gen_delete_services_button(services, offset)
        previous_page_button: InlineKeyboardButton | None = PmUtil.gen_previous_page_services_button(offset)

        action_buttons_row: list[InlineKeyboardButton] = [
            button for button in [create_new_service_button, delete_services_button] if button
        ]
        navigation_buttons_row: list[InlineKeyboardButton] = [
            button for button in [previous_page_button, return_to_pwd_mgr_button, next_page_button] if button
        ]

        return InlineKeyboardMarkup(
            inline_keyboard=
            [
                search_button,
                *service_buttons_rows,
                action_buttons_row,
                navigation_buttons_row
            ]
        )

    @classmethod
    def pwd_mgr_passwords(
            cls,
            decrypted_records: list[DecryptedRecord],
            service: str,
            pwd_offset: int,
            services_offset: int
    ) -> InlineKeyboardMarkup:
        next_page_button: InlineKeyboardButton | None = PmUtil.gen_next_page_pwds_button(decrypted_records, pwd_offset, service)
        password_buttons_rows: list[list[InlineKeyboardButton]] = PmUtil.gen_pwd_buttons(decrypted_records)
        change_service_name_button: InlineKeyboardButton = PmUtil.gen_change_service_button(service)
        delete_service_button: InlineKeyboardButton = PmUtil.gen_delete_service_button(service)
        return_to_services_button: InlineKeyboardButton = PmUtil.gen_return_to_services_button(services_offset)
        create_new_password_button: InlineKeyboardButton = PmUtil.gen_create_pwd_button(service)
        previous_page_button: InlineKeyboardButton | None = PmUtil.gen_previous_page_pwds_button(pwd_offset, service)

        navigation_buttons_row: list[InlineKeyboardButton] = [
            button for button in [previous_page_button, return_to_services_button, next_page_button] if button
        ]

        return InlineKeyboardMarkup(inline_keyboard=[
            *password_buttons_rows,
            [change_service_name_button],
            [create_new_password_button, delete_service_button],
            navigation_buttons_row,
        ])

    @classmethod
    def return_to_services(cls, offset) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[PmUtil.gen_return_to_services_button(offset)]])

    @classmethod
    def return_to_pwd_mgr(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[PmUtil.gen_return_to_pwd_mgr_button()]])

    @classmethod
    def pwd_mgr_password(cls, offset: int, service: str) -> InlineKeyboardMarkup:
        return_to_services_button = PmUtil.gen_return_to_services_button(offset)
        delete_password_button = PmUtil.gen_delete_pwd_button(service)

        return InlineKeyboardMarkup(inline_keyboard=[
            [delete_password_button],
            [return_to_services_button]
        ])

    @classmethod
    def pwd_mgr_inline_search(cls, service: str) -> InlineKeyboardMarkup:
        inline_query_service_button: InlineKeyboardButton = PmUtil.gen_inline_query_service_button(service)
        return InlineKeyboardMarkup(inline_keyboard=[[inline_query_service_button]])