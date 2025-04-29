import asyncio
from typing import Union

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import keyboards.inline
from database import db
import helpers.pwd_mgr_helper as helper
import helpers.pwd_mgr_helper.texts as texts
from helpers.pwd_mgr_helper import DecryptedRecord, EncryptedRecord
from models.states import PasswordManagerStates

fsm_router = Router(name=__name__)


@fsm_router.message(StateFilter(PasswordManagerStates.CreateService), F.text)
async def create_service(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        user_input = helper.split_user_input(user_input=message.text, maxsplit=4)
        master_password, service, login, password = user_input
        helper.has_valid_input_length(login, password)
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    await db.key_value.set_service(service, state)

    decrypted_record = DecryptedRecord(service=service, login=login, password=password)
    await helper.create_password_record(decrypted_record, message.from_user.id, derived_key)
    return await message.answer(
        text=texts.gen_passwords_text(service, pwds_offset=0),
        parse_mode="Markdown",
        reply_markup=keyboards.inline.pwd_mgr_passwords_ikm(
            decrypted_records=[decrypted_record],
            service=service,
            pwd_offset=0,
            services_offset=await db.key_value.get_services_offset(state)
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.CreatePassword), F.text)
async def create_password(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        user_input = helper.split_user_input(user_input=message.text, maxsplit=3)
        master_password, login, password = user_input
        helper.has_valid_input_length(login, password)
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    service = await db.key_value.get_service(state)
    await helper.create_password_record(
        decrypted_record=DecryptedRecord(service=service, login=login, password=password),
        user_id=message.from_user.id,
        derived_key=derived_key
    )
    decrypted_records, pwds_offset, services_offset = await helper.show_service_logins(
        message, state, derived_key, service
    )
    return await message.answer(
        text=texts.gen_passwords_text(service, pwds_offset),
        parse_mode="Markdown",
        reply_markup = keyboards.inline.pwd_mgr_passwords_ikm(
            decrypted_records, service, pwds_offset, services_offset
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeletePassword), F.text)
async def delete_password(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        user_input = helper.split_user_input(user_input=message.text, maxsplit=3)
        master_password, login, password = user_input
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    service, pwds_offset, services_offset = await db.key_value.execute_batch(
        db.key_value.get_service(state),
        db.key_value.get_pwds_offset(state),
        db.key_value.get_services_offset(state)
    )
    encrypted_records = await db.relational.get_passwords(
        user_id=message.from_user.id,
        service=service,
        offset=pwds_offset
    )

    decrypted_records = await DecryptedRecord.decrypt(
        encrypted_records=encrypted_records, derived_key=derived_key
    )
    for i, decrypted_record in enumerate(decrypted_records):
        if decrypted_record.login == login and decrypted_record.password == password:
            encrypted_record = encrypted_records[i]
            await db.relational.delete_password(
                message.from_user.id, service, encrypted_record.ciphertext
            )
            decrypted_records.pop(i)
            break

    if decrypted_records:
        return await message.answer(
            text=texts.PASSWORD_DELETED_TEXT + texts.gen_passwords_text(service, pwds_offset),
            parse_mode="Markdown",
            reply_markup=keyboards.inline.pwd_mgr_passwords_ikm(
                decrypted_records, service, pwds_offset, services_offset
            )
        )
    else:
        services = await db.relational.get_services(message.from_user.id, offset=0)
        if services:
            return await message.answer(
                text=texts.PASSWORD_DELETED_TEXT + texts.gen_services_text(services_offset=0),
                reply_markup=keyboards.inline.pwd_mgr_services_ikm(services, services_offset=0)
            )
        else:
            return await message.answer(
                text=texts.PASSWORD_DELETED_TEXT + texts.NO_SERVICES_TEXT,
                reply_markup=keyboards.inline.pwd_mgr_no_services_ikm
            )


@fsm_router.message(StateFilter(PasswordManagerStates.UpdateCredentials), F.text)
async def update_credentials(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        user_input = helper.split_user_input(user_input=message.text, maxsplit=5)
        master_password, login, password, new_login, new_password = user_input
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    service, pwds_offset, services_offset = await db.key_value.execute_batch(
        db.key_value.get_service(state),
        db.key_value.get_pwds_offset(state),
        db.key_value.get_services_offset(state)
    )
    encrypted_records = await db.relational.get_passwords(
        user_id=message.from_user.id,
        service=service,
        offset=pwds_offset
    )

    decrypted_records = await DecryptedRecord.decrypt(encrypted_records, derived_key)
    for i, decrypted_record in enumerate(decrypted_records):
        if decrypted_record.login == login and decrypted_record.password == password:
            new_pwd_record = await EncryptedRecord.encrypt(
                [DecryptedRecord(
                    service=service,
                    login=new_login,
                    password=new_password
                )],
                derived_key
            )
            await db.relational.update_credentials(
                user_id=message.from_user.id,
                service=service,
                current_ciphertext=encrypted_records[i].ciphertext,
                new_ciphertext=new_pwd_record[0].ciphertext
            )
            break

    return await message.edit_text(
        text=texts.gen_credentials(service, new_login, new_password),
        parse_mode="MarkdownV2",
        reply_markup=keyboards.inline.pwd_mgr_password_ikm(
            service, new_login, new_password, pwds_offset, services_offset
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.EnterService), F.text)
async def service_enter(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        master_password = helper.split_user_input(user_input=message.text, maxsplit=1)[0]
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    service = await db.key_value.get_service(state)
    decrypted_records, pwds_offset, services_offset = await helper.show_service_logins(
        message, state, derived_key, service
    )
    return await message.answer(
        text=texts.gen_passwords_text(service, pwds_offset),
        parse_mode="Markdown",
        reply_markup=keyboards.inline.pwd_mgr_passwords_ikm(
            decrypted_records, service, pwds_offset, services_offset
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ChangeService), F.text)
async def change_service(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        master_password, new_service = helper.split_user_input(user_input=message.text, maxsplit=2)
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    old_service, services_offset, pwds_offset = await db.key_value.execute_batch(
        db.key_value.get_service(state),
        db.key_value.get_services_offset(state),
        db.key_value.get_pwds_offset(state)
    )
    await db.relational.change_service(
        new_service=new_service,
        user_id=message.from_user.id,
        old_service=old_service
    )

    decrypted_records = await DecryptedRecord.decrypt(
        await db.relational.get_passwords(message.from_user.id, new_service, offset=0),
        derived_key
    )
    return await message.answer(
        text=texts.gen_passwords_text(new_service, pwds_offset),
        parse_mode="Markdown",
        reply_markup=keyboards.inline.pwd_mgr_passwords_ikm(
            decrypted_records, new_service, pwds_offset, services_offset
        )
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteServices), F.text)
async def delete_services(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        master_password = helper.split_user_input(user_input=message.text, maxsplit=1)[0]
        await helper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    await db.relational.delete_services(message.from_user.id)
    return await message.answer(
        text=texts.ALL_SERVICES_DELETED_TEXT,
        reply_markup=keyboards.inline.pwd_mgr_no_services_ikm
    )


@fsm_router.message(StateFilter(PasswordManagerStates.DeleteService), F.text)
async def delete_service(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        master_password = helper.split_user_input(user_input=message.text, maxsplit=1)[0]
        await helper.validate_master_password(master_password, message.from_user.id)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    service = await db.key_value.get_service(state)

    coroutines = [
        db.relational.get_services(message.from_user.id, offset=0),
        db.relational.delete_service(message.from_user.id, service)
    ]
    services, _ = await asyncio.gather(*coroutines)

    if services:
        return await message.answer(
            text=texts.SERVICE_DELETED_TEXT + texts.gen_services_text(services_offset=0),
            reply_markup=keyboards.inline.pwd_mgr_services_ikm(services, services_offset=0)
        )
    else:
        return await message.answer(
            text=texts.SERVICE_DELETED_TEXT + texts.NO_SERVICES_TEXT,
            reply_markup=keyboards.inline.pwd_mgr_no_services_ikm
        )


@fsm_router.message(StateFilter(PasswordManagerStates.ImportFromFile), F.document)
async def import_from_file(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        master_password = helper.split_user_input(user_input=message.caption, maxsplit=1)[0]
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    try:
        await helper.process_importing_from_file(message=message, derived_key=derived_key)
    except Exception as e:
        record = await db.relational.get_rand_password(message.from_user.id)
        return await message.answer(
            text=f"{str(e)}\n\n{texts.ENTER_TEXT}",
            reply_markup=keyboards.inline.pwd_mgr_menu_ikm(record)
        )

    services = await db.relational.get_services(message.from_user.id, offset=0)
    return await message.answer(
        text=texts.IMPORT_FROM_FILE_FSM + texts.gen_services_text(services_offset=0),
        reply_markup=keyboards.inline.pwd_mgr_services_ikm(services, services_offset=0)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ExportToFile), F.text)
async def export_to_file(
    message: Message, state: FSMContext
) -> Union[tuple[Message, Message], Message]:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        master_password = helper.split_user_input(user_input=message.caption, maxsplit=1)[0]
        derived_key = await helper.validate_master_password(master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, derived_key)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    document = await helper.process_exporting_to_file(
        derived_key=derived_key, user_id=message.from_user.id
    )
    document_message = await message.answer_document(
        document=document,
        caption=texts.EXPORT_TO_FILE_TEXT,
    )
    record = await db.relational.get_rand_password(message.from_user.id)
    message = await message.answer(
        text=texts.ENTER_TEXT,
        reply_markup=keyboards.inline.pwd_mgr_menu_ikm(record)
    )
    return document_message, message


@fsm_router.message(StateFilter(PasswordManagerStates.ChangeMasterPassword), F.text)
async def change_master_password(message: Message, state: FSMContext) -> Message:
    current_state = await helper.handle_message_deletion(state, message)

    try:
        user_input = helper.split_user_input(user_input=message.text, maxsplit=2)
        old_master_password, new_master_password = user_input
        old_key = await helper.validate_master_password(old_master_password, message.from_user.id)
        await helper.validate_derived_key(message.from_user.id, old_key)
        new_key = await helper.validate_master_password(new_master_password, message.from_user.id)
    except Exception as e:
        return await helper.resend_user_input_request(state, message, str(e), current_state)

    encrypted_records = await db.relational.export_passwords(message.from_user.id)
    decrypted_records = await DecryptedRecord.decrypt(encrypted_records, old_key)
    encrypted_records = await EncryptedRecord.encrypt(decrypted_records, new_key)
    await db.relational.delete_passwords(message.from_user.id)
    await db.relational.import_passwords(message.from_user.id, encrypted_records)

    return await message.answer(
        text=texts.ENTER_TEXT,
        reply_markup=keyboards.inline.pwd_mgr_menu_ikm(encrypted_records[0])
    )
