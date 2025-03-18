from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import db_manager
from .callback_handler import SERVICES_TEXT, ENTER_TEXT, NO_SERVICES_TEXT, CONFIRMATION_TEXT, SERVICE_TEXT
from keyboards import Keyboards
from models.states import PasswordManagerStates
from utils import StorageUtils
from helpers import PasswordManagerHelper as PwdMgrHelper

DecryptedRecord = PwdMgrHelper.DecryptedRecord

MAX_CHAR_LIMIT = 64
MSG_ERROR_INVALID_FORMAT = "Wrong format"
MSG_ERROR_LONG_INPUT = "Login or password is too long"
MSG_ERROR_MASTER_PASS = "Wrong Master Password"
MSG_ERROR_NOT_CONFIRMED = "You didn't confirm the action"
IMPORT_FROM_FILE_TEXT = "Passwords were successfully imported from file\n\n"
EXPORT_TO_FILE_TEXT = "Passwords were successfully exported to file\n\n"
PASSWORD_DELETED_TEXT = "Password was deleted successfully\n\n"
CHOOSE_LOGIN_TEXT = "\nChoose your login to see password"
ALL_SERVICES_DELETED_TEXT = "All services deleted successfully"
SERVICE_DELETED_TEXT = "Service was deleted successfully\n\n"

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(PasswordManagerStates.CreateService), F.text)
async def create_service(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    try:
        master_password, service, login, password = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=4)
        PwdMgrHelper.has_valid_input_length(login, password)
        await PwdMgrHelper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)

    await StorageUtils.set_service(state, service)
    decrypted_record = DecryptedRecord(service=service, login=login, password=password)
    await PwdMgrHelper.create_password_record(decrypted_record, message.from_user.id, master_password)
    return await message.answer(
        text=SERVICE_TEXT + service + CHOOSE_LOGIN_TEXT,
        parse_mode="Markdown",
        reply_markup=Keyboards.inline.pwd_mgr_passwords(
            decrypted_records=[decrypted_record],
            service=service,
            pwd_offset=0,
            services_offset=await StorageUtils.get_pm_services_offset(state)
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.CreatePassword), F.text)
async def create_password(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    try:
        master_password, login, password = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=3)
        PwdMgrHelper.has_valid_input_length(login, password)
        await PwdMgrHelper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)

    service = await StorageUtils.get_service(state)
    await PwdMgrHelper.create_password_record(DecryptedRecord(service=service, login=login, password=password), message.from_user.id, master_password)
    decrypted_records, pwd_offset, services_offset, text = await PwdMgrHelper.show_service_logins(message, state, master_password, service)
    return await message.answer(
        text=text,
        reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, pwd_offset, services_offset),
        parse_mode="Markdown"
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeletePassword), F.text)
async def delete_password(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    try:
        master_password, login, password = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=3)
        await PwdMgrHelper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)

    service = await StorageUtils.get_service(state)
    encrypted_records = await db_manager.relational_db.get_passwords(
        user_id=message.from_user.id,
        service=service,
        offset=0
    )

    decrypted_records = []
    for encrypted_record in encrypted_records:
        decrypted_record = DecryptedRecord.decrypt(encrypted_record=encrypted_record, master_password=master_password)
        if decrypted_record.login == login and decrypted_record.password == password:
            await db_manager.relational_db.delete_password(message.from_user.id, service, encrypted_record.ciphertext)
            continue
        decrypted_records.append(decrypted_record)

    if decrypted_records:
        offset = await StorageUtils.get_pm_pwd_offset(state)
        services_offset = await StorageUtils.get_pm_services_offset(state)
        return await message.answer(
            text=PASSWORD_DELETED_TEXT + SERVICE_TEXT + service + CHOOSE_LOGIN_TEXT,
            reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, offset, services_offset),
            parse_mode="Markdown"
        )
    else:
        services = await db_manager.relational_db.get_services(message.from_user.id, offset=0)
        if services:
            return await message.answer(
                text=PASSWORD_DELETED_TEXT + SERVICES_TEXT,
                reply_markup=Keyboards.inline.pwd_mgr_services(services=services)
            )
        else:
            return await message.answer(
                text=PASSWORD_DELETED_TEXT + NO_SERVICES_TEXT,
                reply_markup=Keyboards.inline.pwd_mgr_no_services()
            )


@fsm_router.message(StateFilter(PasswordManagerStates.EnterService), F.text)
async def service_enter(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)
    try:
        master_password = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=1)
        await PwdMgrHelper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)

    service = await StorageUtils.get_service(state)
    decrypted_records, pwd_offset, services_offset, text = await PwdMgrHelper.show_service_logins(message, state, master_password, service)
    return await message.answer(
        text=text,
        reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, pwd_offset, services_offset),
        parse_mode="Markdown"
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ChangeService), F.text)
async def change_service(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    try:
        new_service = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=1)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)

    new_service = new_service[0]
    old_service = await StorageUtils.get_service(state)

    await db_manager.relational_db.change_service(
        new_service=new_service,
        user_id=message.from_user.id,
        old_service=old_service
    )

    services = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
    return await message.answer(
        text=SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_services(services=services)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteServices), F.text)
async def delete_services(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    try:
        master_password = await PwdMgrHelper.split_user_input(user_input=message.text, maxsplit=1)
        await PwdMgrHelper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)

    await db_manager.relational_db.delete_services(message.from_user.id)
    return await message.answer(
        text=ALL_SERVICES_DELETED_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_no_services()
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteService), F.text)
async def delete_service(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    match message.text.upper():
        case CONFIRMATION_TEXT.upper():
            service = await StorageUtils.get_service(state)
            await db_manager.relational_db.delete_service(message.from_user.id, service)

            services = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
            if services:
                return await message.answer(
                    text=SERVICE_DELETED_TEXT + SERVICES_TEXT,
                    reply_markup=Keyboards.inline.pwd_mgr_services(services)
                )
            else:
                return await message.answer(
                    text=SERVICE_DELETED_TEXT + NO_SERVICES_TEXT,
                    reply_markup=Keyboards.inline.pwd_mgr_no_services()
                )
        case _:
            return await PwdMgrHelper.resend_user_input_request(state, message, MSG_ERROR_NOT_CONFIRMED, current_state)


@fsm_router.message(StateFilter(PasswordManagerStates.ImportFromFile), F.document)
async def import_from_file(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)

    try:
        master_password = await PwdMgrHelper.split_user_input(user_input=message.caption, maxsplit=1)
        await PwdMgrHelper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)

    try:
        await PwdMgrHelper.process_importing_from_file(message=message, master_password=master_password)
    except Exception as e:
        return await message.answer(
            text=f"{str(e)}\n\n{ENTER_TEXT}",
            reply_markup=Keyboards.inline.pwd_mgr_menu()
        )
    services = await db_manager.relational_db.get_services(message.from_user.id, offset=0)
    return await message.answer(
        text=IMPORT_FROM_FILE_TEXT + SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_services(services=services)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ExportToFile), F.text)
async def export_to_file(message: Message, state: FSMContext) -> Message:
    current_state = await PwdMgrHelper.handle_message_deletion(state, message)
    
    try:
        master_password = await PwdMgrHelper.split_user_input(user_input=message.caption, maxsplit=1)
        await PwdMgrHelper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await PwdMgrHelper.resend_user_input_request(state, message, str(e), current_state)
    
    document = await PwdMgrHelper.process_exporting_to_file(master_password=master_password, user_id=message.from_user.id)
    return await message.answer_document(
        document=document,
        caption=EXPORT_TO_FILE_TEXT + ENTER_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_menu()
    )
