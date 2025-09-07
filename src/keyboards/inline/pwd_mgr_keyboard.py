from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.types import InlineKeyboardMarkup

from keyboards.buttons import pwd_mgr, start_menu

if TYPE_CHECKING:
    from models.sql import DecryptedPassword, Password


def pwd_mgr_menu_ikm(record: Password) -> InlineKeyboardMarkup:
    btn_enter_services = pwd_mgr.BTN_ENTER_SERVICES
    btn_return_to_start_menu = start_menu.BTN_RETURN_TO_START_MENU
    btn_import_from_file = pwd_mgr.BTN_IMPORT_FROM_FILE
    btn_export_to_file = pwd_mgr.BTN_EXPORT_TO_FILE
    btn_change_master_password = [pwd_mgr.BTN_CHANGE_MASTER_PASSWORD] if record else []

    btns_import_export_to_file = [btn_import_from_file]
    if record:
        btns_import_export_to_file.append(btn_export_to_file)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_enter_services],
            btns_import_export_to_file,
            btn_change_master_password,
            [btn_return_to_start_menu],
        ],
    )


def _pwd_mgr_no_services_ikm() -> InlineKeyboardMarkup:
    return_to_pwd_mgr_button = pwd_mgr.BTN_RETURN_TO_PWD_MGR
    create_new_service_button = pwd_mgr.btn_create_service(services_offset=0)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [create_new_service_button],
            [return_to_pwd_mgr_button],
        ],
    )


def pwd_mgr_services_ikm(services: list[str], services_offset: int) -> InlineKeyboardMarkup:
    next_page = pwd_mgr.btn_next_page_services(services, services_offset)
    search_button = pwd_mgr.BTN_SEARCH_SERVICE
    service_buttons_rows = pwd_mgr.btns_service(services, services_offset)
    return_to_pwd_mgr = pwd_mgr.BTN_RETURN_TO_PWD_MGR
    create_new_service_button = pwd_mgr.btn_create_service(services_offset)
    delete_services_button = pwd_mgr.btn_delete_services(services_offset)
    previous_page = pwd_mgr.btn_previous_page_services(services_offset)

    action_buttons_row = [button for button in [create_new_service_button, delete_services_button] if button]
    navigation_buttons_row = [button for button in [previous_page, return_to_pwd_mgr, next_page] if button]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [search_button],
            *service_buttons_rows,
            action_buttons_row,
            navigation_buttons_row,
        ],
    )


def pwd_mgr_passwords_ikm(
    decrypted_records: list[DecryptedPassword],
    service: str,
    pwd_offset: int,
    services_offset: int,
) -> InlineKeyboardMarkup:
    next_page = pwd_mgr.btn_next_page_pwds(decrypted_records, service, services_offset, pwd_offset)
    passwords = pwd_mgr.btns_pwd(decrypted_records)
    change_service_name = pwd_mgr.btn_change_service(service, services_offset, pwd_offset)
    delete_service = pwd_mgr.btn_delete_service(service, services_offset, pwd_offset)
    return_to_services = pwd_mgr.btn_return_to_services(services_offset)
    create_new_password = pwd_mgr.btn_create_pwd(service, services_offset, pwd_offset)
    previous_page = pwd_mgr.btn_previous_page_pwds(services_offset, pwd_offset, service)

    navigation_buttons_row = [button for button in [previous_page, return_to_services, next_page] if button]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *passwords,
            [change_service_name],
            [create_new_password, delete_service],
            navigation_buttons_row,
        ],
    )


def return_to_services_ikm(services_offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[pwd_mgr.btn_return_to_services(services_offset)]],
    )


def _return_to_pwd_mgr_ikm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[pwd_mgr.BTN_RETURN_TO_PWD_MGR]])


def pwd_mgr_password_ikm(
    service: str,
    login: str,
    password: str,
    pwds_offset: int,
    services_offset: int,
) -> InlineKeyboardMarkup:
    btn_return_to_pwds = pwd_mgr.btn_return_to_pwds(service, services_offset, pwds_offset)
    btn_delete_pwd = pwd_mgr.btn_delete_pwd(login, password)
    btn_update_credentials = pwd_mgr.btn_update_credentials(login, password)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn_delete_pwd],
            [btn_update_credentials],
            [btn_return_to_pwds],
        ],
    )


def pwd_mgr_inline_search_ikm(service: str) -> InlineKeyboardMarkup:
    inline_query_service_button = pwd_mgr.btn_inline_query_service(service)

    return InlineKeyboardMarkup(inline_keyboard=[[inline_query_service_button]])


def return_to_passwords_ikm(
    service: str,
    services_offset: int,
    pwds_offset: int,
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [pwd_mgr.btn_return_to_pwds(service, services_offset, pwds_offset)],
        ],
    )


def return_to_password_ikm(login: str, password: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[pwd_mgr.btn_return_to_password(login, password)]],
    )


PWD_MGR_NO_SERVICES_IKM = _pwd_mgr_no_services_ikm()
RETURN_TO_PWD_MGR_IKM = _return_to_pwd_mgr_ikm()
