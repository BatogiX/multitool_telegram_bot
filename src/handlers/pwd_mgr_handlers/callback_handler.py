import asyncio
from typing import Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards.inline
from database import db
import helpers.pwd_mgr_helper.texts as texts
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from models.states import PasswordManagerStates
from utils import escape_markdown_v2

callback_router = Router(name=__name__)


@callback_router.callback_query(PwdMgrCb.Enter.filter())
async def enter(query: CallbackQuery) -> Message:
    record = await db.relational.get_rand_password(query.from_user.id)

    return await query.message.edit_text(
        text=texts.ENTER_TEXT,
        reply_markup=keyboards.inline.pwd_mgr_menu_ikm(record)
    )


@callback_router.callback_query(PwdMgrCb.EnterServices.filter())
async def enter_services(
    query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.EnterServices
) -> Message:
    services_offset = callback_data.services_offset

    services, _ = await asyncio.gather(
        db.relational.get_services(query.from_user.id, services_offset),
        db.key_value.execute_batch(
            db.key_value.set_services_offset(services_offset, state),
            db.key_value.clear_state(state)
        )
    )

    if services:
        return await query.message.edit_text(
            text=texts.gen_services_text(services_offset),
            reply_markup=keyboards.inline.pwd_mgr_services_ikm(services, services_offset),
        )
    else:
        return await query.message.edit_text(
            text=texts.NO_SERVICES_TEXT,
            reply_markup=keyboards.inline.pwd_mgr_no_services_ikm,
        )


@callback_router.callback_query(PwdMgrCb.CreateService.filter())
async def create_service(
    query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.CreateService
) -> Message:
    record, _ = await asyncio.gather(
        db.relational.get_rand_password(query.from_user.id),
        db.key_value.execute_batch(
            db.key_value.set_message_id_to_delete(query.message.message_id, state),
            db.key_value.set_input_format_text(texts.CREATE_SERVICE_TEXT, state),
            db.key_value.set_state(PasswordManagerStates.CreateService.state, state)
        )
    )

    if record:
        return await query.message.edit_text(
            text=texts.CREATE_SERVICE_TEXT,
            reply_markup=keyboards.inline.return_to_services_ikm(callback_data.services_offset)
        )
    else:
        return await query.message.edit_text(
            text=texts.WARNING + texts.CREATE_SERVICE_TEXT,
            reply_markup=keyboards.inline.return_to_services_ikm(callback_data.services_offset)
        )


@callback_router.callback_query(PwdMgrCb.DeleteServices.filter())
async def delete_services(
    query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeleteServices
) -> Message:
    await db.key_value.execute_batch(
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.DELETE_SERVICES_TEXT, state),
        db.key_value.set_state(PasswordManagerStates.DeleteService.state, state)
    )

    return await query.message.edit_text(
        text=texts.DELETE_SERVICES_TEXT,
        reply_markup=keyboards.inline.return_to_services_ikm(callback_data.services_offset)
    )


@callback_router.callback_query(PwdMgrCb.EnterService.filter())
async def enter_service(
    query: CallbackQuery, callback_data: PwdMgrCb.EnterService, state: FSMContext
) -> Optional[Message]:
    coroutines = [
        db.key_value.set_service(callback_data.service, state),
        db.key_value.set_pwds_offset(callback_data.pwds_offset, state),
        db.key_value.set_input_format_text(texts.ASK_MASTER_PASSWORD_TEXT, state),
        db.key_value.set_state(PasswordManagerStates.EnterService.state, state)
    ]
    if query.message:
        coroutines.append(db.key_value.set_message_id_to_delete(query.message.message_id, state))
    await db.key_value.execute_batch(*coroutines)

    #  Default Callback
    if query.message:
        return await query.message.edit_text(
            text=texts.ASK_MASTER_PASSWORD_TEXT,
            reply_markup=keyboards.inline.return_to_services_ikm(callback_data.services_offset)
        )

    #  Callback from inline_query (Message can't be deleted)
    await query.bot.send_message(
        chat_id=query.from_user.id,
        text=texts.ASK_MASTER_PASSWORD_TEXT,
        reply_markup=keyboards.inline.return_to_services_ikm(callback_data.services_offset)
    )


@callback_router.callback_query(PwdMgrCb.CreatePassword.filter())
async def create_password(
    query: CallbackQuery, callback_data: PwdMgrCb.CreatePassword, state: FSMContext
) -> Message:
    await db.key_value.execute_batch(
        db.key_value.set_service(callback_data.service, state),
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.CREATE_PASSWORD_TEXT, state),
        db.key_value.set_state(PasswordManagerStates.CreatePassword.state, state)
    )

    return await query.message.edit_text(
        text=texts.CREATE_PASSWORD_TEXT,
        reply_markup=keyboards.inline.return_to_passwords_ikm(
            callback_data.service, callback_data.services_offset, callback_data.pwds_offset
        )
    )


@callback_router.callback_query(PwdMgrCb.EnterPassword.filter())
async def enter_password(
    query: CallbackQuery, callback_data: PwdMgrCb.EnterPassword, state: FSMContext
) -> Message:
    login = escape_markdown_v2(callback_data.login)
    password = escape_markdown_v2(callback_data.password)

    service, services_offset, pwds_offset = await db.key_value.execute_batch(
        db.key_value.get_service(state),
        db.key_value.get_services_offset(state),
        db.key_value.get_pwds_offset(state)
    )

    return await query.message.edit_text(
        text=texts.gen_credentials(service, login, password),
        parse_mode="MarkdownV2",
        reply_markup=keyboards.inline.pwd_mgr_password_ikm(
            service, login, password, pwds_offset, services_offset
        )
    )


@callback_router.callback_query(PwdMgrCb.ChangeService.filter())
async def change_service(
    query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.ChangeService
) -> Message:
    await db.key_value.execute_batch(
        db.key_value.set_service(callback_data.service, state),
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.CHANGE_SERVICE_TEXT, state),
        db.key_value.set_state(PasswordManagerStates.ChangeService.state, state),
        db.key_value.set_pwds_offset(callback_data.pwds_offset, state)
    )

    return await query.message.edit_text(
        text=texts.CHANGE_SERVICE_TEXT,
        reply_markup=keyboards.inline.return_to_passwords_ikm(
            callback_data.service, callback_data.services_offset, callback_data.pwds_offset
        )
    )


@callback_router.callback_query(PwdMgrCb.DeleteService.filter())
async def delete_service(
    query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeleteService
) -> Message:
    await db.key_value.execute_batch(
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_service(callback_data.service, state),
        db.key_value.set_input_format_text(texts.DELETE_SERVICE_TEXT, state),
        db.key_value.set_state(PasswordManagerStates.DeleteService.state, state)
    )

    return await query.message.edit_text(
        text=texts.DELETE_SERVICE_TEXT,
        reply_markup=keyboards.inline.return_to_passwords_ikm(
            callback_data.service, callback_data.services_offset, callback_data.pwds_offset
        )
    )


@callback_router.callback_query(PwdMgrCb.DeletePassword.filter())
async def delete_password(
    query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeletePassword
) -> Message:
    login, password = callback_data.login, callback_data.password  # No need to escape MarkdownV2

    service, _, _, _ = await db.key_value.execute_batch(
        db.key_value.get_service(state),
        db.key_value.set_state(PasswordManagerStates.DeletePassword.state, state),
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.DELETE_PASSWORD_TEXT, state)
    )

    credentials = texts.gen_credentials(service, login, password)
    text = escape_markdown_v2(texts.DELETE_PASSWORD_TEXT)
    return await query.message.edit_text(
        text=credentials + text,
        reply_markup=keyboards.inline.return_to_password_ikm(login, password),
        parse_mode="MarkdownV2"
    )


@callback_router.callback_query(PwdMgrCb.UpdateCredentials.filter())
async def update_credentials(
    query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.UpdateCredentials
) -> Message:
    login, password = callback_data.login, callback_data.password  # No need to escape MarkdownV2

    service, _, _, _ = await db.key_value.execute_batch(
        db.key_value.get_service(state),
        db.key_value.set_state(PasswordManagerStates.UpdateCredentials.state, state),
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.UPDATE_CREDENTIALS_TEXT, state)
    )

    credentials = texts.gen_credentials(service, login, password)
    text = escape_markdown_v2(texts.UPDATE_CREDENTIALS_TEXT)
    return await query.message.edit_text(
        text=credentials + "\n\n" + text,
        reply_markup=keyboards.inline.return_to_password_ikm(login, password),
        parse_mode="MarkdownV2"
    )


@callback_router.callback_query(PwdMgrCb.ImportFromFile.filter())
async def import_from_file(query: CallbackQuery, state: FSMContext) -> Message:
    await db.key_value.execute_batch(
        db.key_value.set_state(PasswordManagerStates.ImportFromFile.state, state),
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.IMPORT_FROM_FILE_TEXT, state)
    )

    return await query.message.edit_text(
        text=texts.IMPORT_FROM_FILE_TEXT,
        reply_markup=keyboards.inline.return_to_pwd_mgr_ikm
    )


@callback_router.callback_query(PwdMgrCb.ExportToFile.filter())
async def export_to_file(query: CallbackQuery, state: FSMContext) -> Message:
    await db.key_value.execute_batch(
        db.key_value.set_state(PasswordManagerStates.ExportToFile.state, state),
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.ASK_MASTER_PASSWORD_TEXT, state)
    )

    return await query.message.edit_text(
        text=texts.ASK_MASTER_PASSWORD_TEXT,
        reply_markup=keyboards.inline.return_to_pwd_mgr_ikm
    )


@callback_router.callback_query(PwdMgrCb.ChangeMasterPassword.filter())
async def change_master_password(query: CallbackQuery, state: FSMContext) -> Message:
    await db.key_value.execute_batch(
        db.key_value.set_state(PasswordManagerStates.ChangeMasterPassword.state, state),
        db.key_value.set_message_id_to_delete(query.message.message_id, state),
        db.key_value.set_input_format_text(texts.CHANGE_MASTER_PASSWORD_TEXT, state)
    )

    return await query.message.edit_text(
        text=texts.CHANGE_MASTER_PASSWORD_TEXT,
        reply_markup=keyboards.inline.return_to_pwd_mgr_ikm
    )
