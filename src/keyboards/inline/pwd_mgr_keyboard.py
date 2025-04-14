from __future__ import annotations

from typing import TYPE_CHECKING
from aiogram.types import InlineKeyboardMarkup

from keyboards.buttons import gen_enter_services_button, gen_import_from_file_button, gen_export_to_file_button, \
    gen_return_to_start_menu_button, gen_return_to_pwd_mgr_button, gen_create_service_button, \
    gen_next_page_services_button, gen_search_button, gen_service_buttons, gen_delete_services_button, \
    gen_previous_page_services_button, gen_next_page_pwds_button, gen_pwd_buttons, gen_change_service_button, \
    gen_delete_service_button, gen_return_to_services_button, gen_create_pwd_button, gen_previous_page_pwds_button, \
    gen_return_to_passwords_button, gen_delete_pwd_button, gen_inline_query_service_button, \
    gen_return_to_password_button

if TYPE_CHECKING:
    from helpers.pwd_mgr_helper import DecryptedRecord


def pwd_mgr_menu() -> InlineKeyboardMarkup:
    enter_services_button = gen_enter_services_button()
    import_from_file_button = gen_import_from_file_button()
    export_to_file_button = gen_export_to_file_button()
    return_to_start_menu_button = gen_return_to_start_menu_button()

    return InlineKeyboardMarkup(inline_keyboard=[
        [enter_services_button],
        [import_from_file_button, export_to_file_button],
        [return_to_start_menu_button]
    ])


def pwd_mgr_no_services() -> InlineKeyboardMarkup:
    return_to_pwd_mgr_button = gen_return_to_pwd_mgr_button()
    create_new_service_button = gen_create_service_button(services_offset=0)

    return InlineKeyboardMarkup(
        inline_keyboard=
        [
            [create_new_service_button],
            [return_to_pwd_mgr_button]
        ]
    )


def pwd_mgr_services(services: list[str], services_offset: int) -> InlineKeyboardMarkup:
    next_page_button = gen_next_page_services_button(services, services_offset)
    search_button = gen_search_button()
    service_buttons_rows = gen_service_buttons(services, services_offset)
    return_to_pwd_mgr_button = gen_return_to_pwd_mgr_button()
    create_new_service_button = gen_create_service_button(services_offset)
    delete_services_button = gen_delete_services_button(services_offset)
    previous_page_button = gen_previous_page_services_button(services_offset)

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


def pwd_mgr_passwords(
        decrypted_records: list[DecryptedRecord],
        service: str,
        pwd_offset: int,
        services_offset: int
) -> InlineKeyboardMarkup:
    next_page_button = gen_next_page_pwds_button(decrypted_records, service, services_offset, pwd_offset)
    password_buttons_rows = gen_pwd_buttons(decrypted_records)
    change_service_name_button = gen_change_service_button(service, services_offset, pwd_offset)
    delete_service_button = gen_delete_service_button(service, services_offset, pwd_offset)
    return_to_services_button = gen_return_to_services_button(services_offset)
    create_new_password_button = gen_create_pwd_button(service, services_offset, pwd_offset)
    previous_page_button = gen_previous_page_pwds_button(services_offset, pwd_offset, service)

    navigation_buttons_row = [
        button for button in [previous_page_button, return_to_services_button, next_page_button] if button
    ]

    return InlineKeyboardMarkup(inline_keyboard=[
        *password_buttons_rows,
        [change_service_name_button],
        [create_new_password_button, delete_service_button],
        navigation_buttons_row,
    ])


def return_to_services(services_offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[gen_return_to_services_button(services_offset)]])


def return_to_pwd_mgr() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[gen_return_to_pwd_mgr_button()]])


def pwd_mgr_password(service: str, login: str, password: str, pwds_offset: int, services_offset: int) -> InlineKeyboardMarkup:
    return_to_passwords_button = gen_return_to_passwords_button(service, services_offset, pwds_offset)
    delete_password_button = gen_delete_pwd_button(login, password)

    return InlineKeyboardMarkup(inline_keyboard=[
        [delete_password_button],
        [return_to_passwords_button]
    ])


def pwd_mgr_inline_search(service: str) -> InlineKeyboardMarkup:
    inline_query_service_button = gen_inline_query_service_button(service)
    return InlineKeyboardMarkup(inline_keyboard=[[inline_query_service_button]])


def return_to_passwords(service: str, services_offset: int, pwds_offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[gen_return_to_passwords_button(service, services_offset, pwds_offset)]])


def return_to_password(login: str, password: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[gen_return_to_password_button(login, password)]])
