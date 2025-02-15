from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import db_manager
from keyboards import InlineKeyboards
from models.fsm_states import PasswordManagerStates
from models.passwords_record import DecryptedRecord, EncryptedRecord
from utils.fsm_data_utils import FSMDataUtils
from utils.password_manager_utils import PasswordManagerUtils as PwManUtils, PasswordManagerFsmHandlerUtils as PwManFsmHandlerUtils

fsm_router = Router(name=__name__)

MAX_CHAR_LIMIT: int = 64
MSG_ERROR_INVALID_FORMAT: str = "Wrong format"
MSG_ERROR_LONG_INPUT: str = "Login or password is too long"
MSG_ERROR_MASTER_PASS: str = "Wrong Master Password"
MSG_ERROR_NOT_CONFIRMED: str = "You didn't confirm the action"


@fsm_router.message(StateFilter(PasswordManagerStates.CreateService), F.text)
async def create_service(message: Message, state: FSMContext):
    """Handler for creating a new password record with service."""
    current_state = await PwManFsmHandlerUtils.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwManFsmHandlerUtils.split_user_input(message=message, maxsplit=4)
    if not user_input:
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, service, login, password = user_input
    if not PwManFsmHandlerUtils.has_valid_input_length(login, password):
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    key: bytes | str = await PwManFsmHandlerUtils.derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, custom_error, current_state)

    await PwManFsmHandlerUtils.create_password_record(login, password, service, message, key)
    await FSMDataUtils.set_service(state, service)
    services_offset = await FSMDataUtils.get_pm_services_offset(state)
    await message.answer(
        text=f"*Service:* {service}\nChoose your login to see password",
        parse_mode="Markdown",
        reply_markup=InlineKeyboards.passwd_man_passwords(
            decrypted_records=[DecryptedRecord(login=login, password=password)],
            service=service,
            pwd_offset=0,
            services_offset=services_offset
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.CreatePassword), F.text)
async def create_password(message: Message, state: FSMContext):
    """Handler for creating a new password for an existing service."""
    current_state = await PwManFsmHandlerUtils.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwManFsmHandlerUtils.split_user_input(message=message, maxsplit=3)
    if not user_input:
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, login, password = user_input
    if not PwManFsmHandlerUtils.has_valid_input_length(login, password):
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    key: bytes | str = await PwManFsmHandlerUtils.derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, custom_error, current_state)

    service: str = await FSMDataUtils.get_service(state)
    await PwManFsmHandlerUtils.create_password_record(login, password, service, message, key)
    await PwManFsmHandlerUtils.show_service_logins(message, state, key, service)


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingPassword), F.text)
async def delete_password(message: Message, state: FSMContext):
    """Handler for deleting password"""
    current_state = await PwManFsmHandlerUtils.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwManFsmHandlerUtils.split_user_input(message=message, maxsplit=3)
    if not user_input:
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, login, password = user_input
    if not PwManFsmHandlerUtils.has_valid_input_length(login, password):
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    key: bytes | str = await PwManFsmHandlerUtils.derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, custom_error, current_state)

    service: str = await FSMDataUtils.get_service(state)
    encrypted_records: list[EncryptedRecord] = await db_manager.relational_db.get_passwords_records(
        message.from_user.id,
        service,
        offset=0
    )

    decrypted_records: list[DecryptedRecord] = []
    for encrypted_record in encrypted_records:
        decrypted_record: DecryptedRecord = PwManUtils.decrypt_record(encrypted_record=encrypted_record, key=key)
        if decrypted_record.login == login and decrypted_record.password == password:
            await db_manager.relational_db.delete_passwords_record(message.from_user.id, service, encrypted_record.ciphertext)
            continue
        decrypted_records.append(decrypted_record)

    if decrypted_records:
        text: str = (
            "Password was deleted successfully\n\n"
            f"*Service:* {service}\n"
            "Choose your login to see password"
        )
        offset: int = await FSMDataUtils.get_pm_pwd_offset(state)
        services_offset = await FSMDataUtils.get_pm_services_offset(state)
        await message.answer(
            text=text,
            reply_markup=InlineKeyboards.passwd_man_passwords(decrypted_records, service, offset, services_offset),
            parse_mode="Markdown"
        )
    else:
        text: str = "Password was deleted successfully\n\n"
        services: list[str] = await db_manager.relational_db.get_services(message.from_user.id, offset=0)
        if services:
            await message.answer(
                text=text + "Choose service",
                reply_markup=InlineKeyboards.passwd_man_services(services=services, offset=0)
            )
        else:
            await message.answer(
                text=text + "You don't have any services yet. Create one now?",
                reply_markup=InlineKeyboards.passwd_man_services(services=[], offset=0)
            )


@fsm_router.message(StateFilter(PasswordManagerStates.EnteringService), F.text)
async def service_enter(message: Message, state: FSMContext):
    current_state = await PwManFsmHandlerUtils.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwManFsmHandlerUtils.split_user_input(message=message, maxsplit=1)
    if not user_input:
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password: str = user_input[0]
    key: bytes = await PwManFsmHandlerUtils.derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, custom_error, current_state)

    service = await FSMDataUtils.get_service(state)
    await PwManFsmHandlerUtils.show_service_logins(message, state, key, service)


@fsm_router.message(StateFilter(PasswordManagerStates.ChangeService), F.text)
async def change_service(message: Message, state: FSMContext):
    current_state = await PwManFsmHandlerUtils.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwManFsmHandlerUtils.split_user_input(message=message, maxsplit=1)
    if not user_input:
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    new_service: str = user_input[0]
    old_service: str = await FSMDataUtils.get_service(state)

    await db_manager.relational_db.change_service(
        new_service=new_service,
        user_id=message.from_user.id,
        old_service=old_service
    )

    services: list[str] = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
    await message.answer(
        text="Choose service",
        reply_markup=InlineKeyboards.passwd_man_services(services=services, offset=0)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingServices), F.text)
async def delete_services(message: Message, state: FSMContext):
    current_state = await PwManFsmHandlerUtils.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwManFsmHandlerUtils.split_user_input(message=message, maxsplit=1)
    if not user_input:
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password: str = user_input[0]
    key: bytes = await PwManFsmHandlerUtils.derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, custom_error, current_state)

    await db_manager.relational_db.delete_services(message.from_user.id)
    await message.answer(
        text="All services deleted successfully",
        reply_markup=InlineKeyboards.passwd_man_services(services=[], offset=0)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingService), F.text)
async def delete_service(message: Message, state: FSMContext):
    current_state = await PwManFsmHandlerUtils.handle_message_deletion(state, message)

    answer: str = message.text.upper()
    if answer == "I CONFIRM":
        service: str = await FSMDataUtils.get_service(state)
        await db_manager.relational_db.delete_service(message.from_user.id, service)

        services: list[str] = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
        text: str = "Service was deleted successfully\n\n"
        if services:
            await message.answer(
                text=text + "Choose service",
                reply_markup=InlineKeyboards.passwd_man_services(services, offset=0)
            )
        else:
            await message.answer(
                text=text + "You don't have any services yet. Create one now?",
                reply_markup=InlineKeyboards.passwd_man_services(services=[], offset=0)
            )
    else:
        return await PwManFsmHandlerUtils.resend_user_input_request(state, message, MSG_ERROR_NOT_CONFIRMED, current_state)