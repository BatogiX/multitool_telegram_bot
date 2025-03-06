from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from config import db_manager, bot_cfg
from .callback_handler import SERVICES_TEXT, ENTER_TEXT, NO_SERVICES_TEXT, CONFIRMATION_TEXT, SERVICE_TEXT
from keyboards import Keyboards
from models.states import PasswordManagerStates
from models.db_record.password_record import DecryptedRecord, EncryptedRecord
from utils import StorageUtils
from helpers import PasswordManagerHelper as PwdMgrHelper

MAX_CHAR_LIMIT: int = 64
MSG_ERROR_INVALID_FORMAT: str = "Wrong format"
MSG_ERROR_LONG_INPUT: str = "Login or password is too long"
MSG_ERROR_MASTER_PASS: str = "Wrong Master Password"
MSG_ERROR_NOT_CONFIRMED: str = "You didn't confirm the action"
IMPORT_FROM_FILE_TEXT: str = "Passwords were successfully imported from file\n\n"
EXPORT_TO_FILE_TEXT: str = "Passwords were successfully exported to file\n\n"
PASSWORD_DELETED_TEXT: str = "Password was deleted successfully\n\n"
CHOOSE_LOGIN_TEXT: str = "\nChoose your login to see password"
ALL_SERVICES_DELETED_TEXT: str = "All services deleted successfully"
SERVICE_DELETED_TEXT: str = "Service was deleted successfully\n\n"

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(PasswordManagerStates.CreateService), F.text)
async def create_service(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=4)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, service, login, password = user_input
    if not PwdMgrHelper.has_valid_input_length(login, password):
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    error = PwdMgrHelper.is_master_password_weak(master_password)
    if error:
        return await PwdMgrHelper.resend_user_input_request(state, message, error, current_state)

    key: bytes | str = await PwdMgrHelper.derive_key_from_master_password(master_password, message)
    if not key:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state)

    await PwdMgrHelper.create_password_record(login, password, service, message, key)
    await StorageUtils.set_service(state, service)
    services_offset = await StorageUtils.get_pm_services_offset(state)
    await message.answer(
        text=SERVICE_TEXT + service + CHOOSE_LOGIN_TEXT,
        parse_mode="Markdown",
        reply_markup=Keyboards.inline.pwd_mgr_passwords(
            decrypted_records=[DecryptedRecord(service=service, login=login, password=password)],
            service=service,
            pwd_offset=0,
            services_offset=services_offset
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.CreatePassword), F.text)
async def create_password(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=3)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, login, password = user_input
    if not PwdMgrHelper.has_valid_input_length(login, password):
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    error = PwdMgrHelper.is_master_password_weak(master_password)
    if error:
        return await PwdMgrHelper.resend_user_input_request(state, message, error, current_state)

    key: bytes | str = await PwdMgrHelper.derive_key_from_master_password(master_password, message)
    if not key:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state)

    service: str = await StorageUtils.get_service(state)
    await PwdMgrHelper.create_password_record(login, password, service, message, key)
    await PwdMgrHelper.show_service_logins(message, state, key, service)


@fsm_router.message(StateFilter(PasswordManagerStates.DeletePassword), F.text)
async def delete_password(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=3)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, login, password = user_input
    error = PwdMgrHelper.is_master_password_weak(master_password)
    if error:
        return await PwdMgrHelper.resend_user_input_request(state, message, error, current_state)

    key: bytes | str = await PwdMgrHelper.derive_key_from_master_password(master_password, message)
    if not key:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state)

    service: str = await StorageUtils.get_service(state)
    encrypted_records: list[EncryptedRecord] = await db_manager.relational_db.get_passwords(
        user_id=message.from_user.id,
        service=service,
        offset=0,
        limit=bot_cfg.dynamic_buttons_limit
    )

    decrypted_records: list[DecryptedRecord] = []
    for encrypted_record in encrypted_records:
        decrypted_record: DecryptedRecord = PwdMgrHelper.decrypt_record(encrypted_record=encrypted_record, key=key)
        if decrypted_record.login == login and decrypted_record.password == password:
            await db_manager.relational_db.delete_password(message.from_user.id, service, encrypted_record.ciphertext)
            continue
        decrypted_records.append(decrypted_record)

    if decrypted_records:
        offset: int = await StorageUtils.get_pm_pwd_offset(state)
        services_offset = await StorageUtils.get_pm_services_offset(state)
        await message.answer(
            text=PASSWORD_DELETED_TEXT + SERVICE_TEXT + service + CHOOSE_LOGIN_TEXT,
            reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, offset, services_offset),
            parse_mode="Markdown"
        )
    else:
        services: list[str] = await db_manager.relational_db.get_services(
            message.from_user.id, offset=0, limit=bot_cfg.dynamic_buttons_limit)
        if services:
            await message.answer(
                text=PASSWORD_DELETED_TEXT + SERVICES_TEXT,
                reply_markup=Keyboards.inline.pwd_mgr_services(services=services)
            )
        else:
            await message.answer(
                text=PASSWORD_DELETED_TEXT + NO_SERVICES_TEXT,
                reply_markup=Keyboards.inline.pwd_mgr_no_services()
            )


@fsm_router.message(StateFilter(PasswordManagerStates.EnterService), F.text)
async def service_enter(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=1)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password: str = user_input[0]
    error = PwdMgrHelper.is_master_password_weak(master_password)
    if error:
        return await PwdMgrHelper.resend_user_input_request(state, message, error, current_state)

    key: bytes = await PwdMgrHelper.derive_key_from_master_password(master_password, message)
    if not key:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state)

    service = await StorageUtils.get_service(state)
    await PwdMgrHelper.show_service_logins(message, state, key, service)


@fsm_router.message(StateFilter(PasswordManagerStates.ChangeService), F.text)
async def change_service(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=1)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    new_service: str = user_input[0]
    old_service: str = await StorageUtils.get_service(state)

    await db_manager.relational_db.change_service(
        new_service=new_service,
        user_id=message.from_user.id,
        old_service=old_service
    )

    services: list[str] = await db_manager.relational_db.get_services(
        user_id=message.from_user.id, offset=0, limit=bot_cfg.dynamic_buttons_limit)
    await message.answer(
        text=SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_services(services=services)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteServices), F.text)
async def delete_services(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=1)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password: str = user_input[0]
    error = PwdMgrHelper.is_master_password_weak(master_password)
    if error:
        return await PwdMgrHelper.resend_user_input_request(state, message, error, current_state)

    key: bytes = await PwdMgrHelper.derive_key_from_master_password(master_password, message)
    if not key:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state)

    await db_manager.relational_db.delete_services(message.from_user.id)
    await message.answer(
        text=ALL_SERVICES_DELETED_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_no_services()
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteService), F.text)
async def delete_service(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    match message.text.upper():
        case CONFIRMATION_TEXT.upper():
            service: str = await StorageUtils.get_service(state)
            await db_manager.relational_db.delete_service(message.from_user.id, service)

            services: list[str] = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0, limit=bot_cfg.dynamic_buttons_limit)
            if services:
                await message.answer(
                    text=SERVICE_DELETED_TEXT + SERVICES_TEXT,
                    reply_markup=Keyboards.inline.pwd_mgr_services(services)
                )
            else:
                await message.answer(
                    text=SERVICE_DELETED_TEXT + NO_SERVICES_TEXT,
                    reply_markup=Keyboards.inline.pwd_mgr_no_services()
                )
        case _:
            return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_NOT_CONFIRMED, current_state)


@fsm_router.message(StateFilter(PasswordManagerStates.ImportFromFile), F.document)
async def import_from_file(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.caption, maxsplit=1)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password: str = user_input[0]
    error = PwdMgrHelper.is_master_password_weak(master_password)
    if error:
        return await PwdMgrHelper.resend_user_input_request(state, message, error, current_state)

    key: bytes = await PwdMgrHelper.derive_key_from_master_password(master_password, message)
    if not key:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state)

    try:
        await PwdMgrHelper.process_importing_from_file(message=message, key=key)
    except Exception as e:
        return await message.answer(
            text=f"{str(e)}\n\n{ENTER_TEXT}",
            reply_markup=Keyboards.inline.pwd_mgr_menu()
        )
    services: list[str] = await db_manager.relational_db.get_services(
        message.from_user.id, offset=0, limit=bot_cfg.dynamic_buttons_limit)
    await message.answer(
        text=IMPORT_FROM_FILE_TEXT + SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_services(services=services)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ExportToFile), F.text)
async def export_to_file(message: Message, state: FSMContext):
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)
    
    user_input: tuple[str, ...] = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=1)
    if not user_input:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password: str = user_input[0]
    error = PwdMgrHelper.is_master_password_weak(master_password)
    if error:
        return await PwdMgrHelper.resend_user_input_request(state, message, error, current_state)
    
    key: bytes = await PwdMgrHelper.derive_key_from_master_password(master_password, message)
    if not key:
        return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state)
    
    document: BufferedInputFile = await PwdMgrHelper.process_exporting_to_file(key=key, user_id=message.from_user.id)
    await message.answer_document(
        document=document,
        caption=EXPORT_TO_FILE_TEXT
    )
    await message.answer(
        text=ENTER_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_menu()
    )