from typing import Union

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import db_manager
from helpers.pwd_mgr_helper.texts import *
from models.states import PasswordManagerStates
from helpers.pwd_mgr_helper import *

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(PasswordManagerStates.CreateService), F.text)
async def create_service(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        master_password, service, login, password = split_user_input(user_input=message.text, maxsplit=4)
        has_valid_input_length(login, password)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    pwds_offset = await db_manager.key_value_db.get_pwds_offset(state)
    await db_manager.key_value_db.set_service(service, state)
    decrypted_record = DecryptedRecord(service=service, login=login, password=password)
    await create_password_record(decrypted_record, message.from_user.id, master_password)
    return await message.answer(
        text=gen_passwords_text(service, pwds_offset),
        parse_mode="Markdown",
        reply_markup=Keyboards.inline.pwd_mgr_passwords(
            decrypted_records=[decrypted_record],
            service=service,
            pwd_offset=0,
            services_offset=await db_manager.key_value_db.get_services_offset(state)
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.CreatePassword), F.text)
async def create_password(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        master_password, login, password = split_user_input(user_input=message.text, maxsplit=3)
        has_valid_input_length(login, password)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    service = await db_manager.key_value_db.get_service(state)
    await create_password_record(DecryptedRecord(service=service, login=login, password=password), message.from_user.id, master_password)
    decrypted_records, pwds_offset, services_offset = await show_service_logins(message, state, master_password, service)
    return await message.answer(
        text=gen_passwords_text(service, pwds_offset),
        reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, pwds_offset, services_offset),
        parse_mode="Markdown"
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeletePassword), F.text)
async def delete_password(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        master_password, login, password = split_user_input(user_input=message.text, maxsplit=3)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    service = await db_manager.key_value_db.get_service(state)
    services_offset = await db_manager.key_value_db.get_services_offset(state)
    encrypted_records = await db_manager.relational_db.get_passwords(
        user_id=message.from_user.id,
        service=service,
        offset=0
    )

    decrypted_records = []
    for encrypted_record in encrypted_records:
        decrypted_record = await DecryptedRecord.decrypt(encrypted_record=encrypted_record, derived_key=master_password)
        if decrypted_record.login == login and decrypted_record.password == password:
            await db_manager.relational_db.delete_password(message.from_user.id, service, encrypted_record.ciphertext)
            continue
        decrypted_records.append(decrypted_record)

    if decrypted_records:
        pwds_offset = await db_manager.key_value_db.get_pwds_offset(state)

        return await message.answer(
            text=PASSWORD_DELETED_TEXT + gen_passwords_text(service, pwds_offset),
            reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, pwds_offset, services_offset),
            parse_mode="Markdown"
        )
    else:
        services = await db_manager.relational_db.get_services(message.from_user.id, offset=0)
        if services:
            return await message.answer(
                text=PASSWORD_DELETED_TEXT + gen_services_text(services_offset=0),
                reply_markup=Keyboards.inline.pwd_mgr_services(services, services_offset=0)
            )
        else:
            return await message.answer(
                text=PASSWORD_DELETED_TEXT + NO_SERVICES_TEXT,
                reply_markup=Keyboards.inline.pwd_mgr_no_services()
            )


@fsm_router.message(StateFilter(PasswordManagerStates.EnterService), F.text)
async def service_enter(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        master_password = split_user_input(user_input=message.text, maxsplit=1)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    service = await db_manager.key_value_db.get_service(state)
    decrypted_records, pwds_offset, services_offset = await show_service_logins(message, state, master_password, service)
    return await message.answer(
        text=gen_passwords_text(service, pwds_offset),
        reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, pwds_offset, services_offset),
        parse_mode="Markdown"
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ChangeService), F.text)
async def change_service(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        new_service = split_user_input(user_input=message.text, maxsplit=1)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    new_service = new_service[0]
    old_service = await db_manager.key_value_db.get_service(state)
    services_offset = await db_manager.key_value_db.get_services_offset(state)

    await db_manager.relational_db.change_service(
        new_service=new_service,
        user_id=message.from_user.id,
        old_service=old_service
    )

    services = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
    return await message.answer(
        text=gen_services_text(services_offset),
        reply_markup=Keyboards.inline.pwd_mgr_services(services, services_offset)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteServices), F.text)
async def delete_services(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        master_password = split_user_input(user_input=message.text, maxsplit=1)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    await db_manager.relational_db.delete_services(message.from_user.id)
    return await message.answer(
        text=ALL_SERVICES_DELETED_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_no_services()
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteService), F.text)
async def delete_service(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        master_password = split_user_input(user_input=message.text, maxsplit=1)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    service = await db_manager.key_value_db.get_service(state)
    await db_manager.relational_db.delete_service(message.from_user.id, service)
    services_offset = await db_manager.key_value_db.get_services_offset(state)

    services = await db_manager.relational_db.get_services(message.from_user.id, services_offset)
    if services:
        return await message.answer(
            text=SERVICE_DELETED_TEXT + gen_services_text(services_offset=0),
            reply_markup=Keyboards.inline.pwd_mgr_services(services, services_offset)
        )
    else:
        return await message.answer(
            text=SERVICE_DELETED_TEXT + NO_SERVICES_TEXT,
            reply_markup=Keyboards.inline.pwd_mgr_no_services()
        )


@fsm_router.message(StateFilter(PasswordManagerStates.ImportFromFile), F.document)
async def import_from_file(message: Message, state: FSMContext) -> Message:
    current_state = await handle_message_deletion(state, message)

    try:
        master_password = split_user_input(user_input=message.caption, maxsplit=1)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)

    try:
        await process_importing_from_file(message=message, master_password=master_password)
    except Exception as e:
        return await message.answer(
            text=f"{str(e)}\n\n{ENTER_TEXT}",
            reply_markup=Keyboards.inline.pwd_mgr_menu()
        )

    services = await db_manager.relational_db.get_services(message.from_user.id, offset=0)
    return await message.answer(
        text=IMPORT_FROM_FILE_FSM + gen_services_text(services_offset=0),
        reply_markup=Keyboards.inline.pwd_mgr_services(services, services_offset=0)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ExportToFile), F.text)
async def export_to_file(message: Message, state: FSMContext) -> Union[tuple[Message, Message], Message]:
    current_state = await handle_message_deletion(state, message)
    
    try:
        master_password = split_user_input(user_input=message.text, maxsplit=1)
        await validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await resend_user_input_request(state, message, str(e), current_state)
    
    document = await process_exporting_to_file(master_password=master_password, user_id=message.from_user.id)
    document_message = await message.answer_document(
        document=document,
        caption=EXPORT_TO_FILE_TEXT,
    )
    message = await message.answer(
        text=ENTER_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_menu()
    )
    return document_message, message
