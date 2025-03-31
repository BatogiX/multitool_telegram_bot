from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardMarkup

from utils import InlineKeyboardsUtils as KbUtils

if TYPE_CHECKING:
    from helpers import PasswordManagerHelper
    DecryptedRecord = PasswordManagerHelper.DecryptedRecord


class InlinePasswordManagerKeyboard:
    @classmethod
    def pwd_mgr_menu(cls) -> InlineKeyboardMarkup:
        enter_services_button = KbUtils.gen_enter_services_button()
        import_from_file_button = KbUtils.gen_import_from_file_button()
        export_to_file_button = KbUtils.gen_export_to_file_button()
        return_to_start_menu_button = KbUtils.gen_return_to_start_menu_button()

        return InlineKeyboardMarkup(inline_keyboard=[
            [enter_services_button],
            [import_from_file_button, export_to_file_button],
            [return_to_start_menu_button]
        ])

    @classmethod
    def pwd_mgr_no_services(cls) -> InlineKeyboardMarkup:
        return_to_pwd_mgr_button = KbUtils.gen_return_to_pwd_mgr_button()
        create_new_service_button = KbUtils.gen_create_service_button(services_offset=0)

        return InlineKeyboardMarkup(
            inline_keyboard=
            [
                [create_new_service_button],
                [return_to_pwd_mgr_button]
            ]
        )

    @classmethod
    def pwd_mgr_services(cls, services: list[str], services_offset: int) -> InlineKeyboardMarkup:
        next_page_button = KbUtils.gen_next_page_services_button(services, services_offset)
        search_button = KbUtils.gen_search_button()
        service_buttons_rows = KbUtils.gen_service_buttons(services, services_offset)
        return_to_pwd_mgr_button = KbUtils.gen_return_to_pwd_mgr_button()
        create_new_service_button = KbUtils.gen_create_service_button(services_offset)
        delete_services_button = KbUtils.gen_delete_services_button(services_offset)
        previous_page_button = KbUtils.gen_previous_page_services_button(services_offset)

        action_buttons_row = [
            button for button in [create_new_service_button, delete_services_button] if button
        ]
        navigation_buttons_row = [
            button for button in [previous_page_button, return_to_pwd_mgr_button, next_page_button] if button
        ]

        return InlineKeyboardMarkup(
            inline_keyboard=
            [
                [search_button],
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
        next_page_button = KbUtils.gen_next_page_pwds_button(decrypted_records, service, services_offset, pwd_offset)
        password_buttons_rows = KbUtils.gen_pwd_buttons(decrypted_records)
        change_service_name_button = KbUtils.gen_change_service_button(service, services_offset, pwd_offset)
        delete_service_button = KbUtils.gen_delete_service_button(service, services_offset, pwd_offset)
        return_to_services_button = KbUtils.gen_return_to_services_button(services_offset)
        create_new_password_button = KbUtils.gen_create_pwd_button(service, services_offset, pwd_offset)
        previous_page_button = KbUtils.gen_previous_page_pwds_button(services_offset, pwd_offset, service)

        navigation_buttons_row = [
            button for button in [previous_page_button, return_to_services_button, next_page_button] if button
        ]

        return InlineKeyboardMarkup(inline_keyboard=[
            *password_buttons_rows,
            [change_service_name_button],
            [create_new_password_button, delete_service_button],
            navigation_buttons_row,
        ])

    @classmethod
    def return_to_services(cls, services_offset: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[KbUtils.gen_return_to_services_button(services_offset)]])

    @classmethod
    def return_to_pwd_mgr(cls) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[KbUtils.gen_return_to_pwd_mgr_button()]])

    @classmethod
    def pwd_mgr_password(cls, service: str, login: str, password: str, pwds_offset: int, services_offset: int) -> InlineKeyboardMarkup:
        return_to_passwords_button = KbUtils.gen_return_to_passwords_button(service, services_offset, pwds_offset)
        delete_password_button = KbUtils.gen_delete_pwd_button(login, password)

        return InlineKeyboardMarkup(inline_keyboard=[
            [delete_password_button],
            [return_to_passwords_button]
        ])

    @classmethod
    def pwd_mgr_inline_search(cls, service: str) -> InlineKeyboardMarkup:
        inline_query_service_button = KbUtils.gen_inline_query_service_button(service)
        return InlineKeyboardMarkup(inline_keyboard=[[inline_query_service_button]])

    @classmethod
    def return_to_passwords(cls, service: str, services_offset: int, pwds_offset: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[KbUtils.gen_return_to_passwords_button(service, services_offset, pwds_offset)]])

    @classmethod
    def return_to_password(cls, login: str, password: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[KbUtils.gen_return_to_password_button(login, password)]])