from typing import Optional

import asyncio
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db_manager
from handlers.pwd_mgr_handlers.texts import *
from keyboards import Keyboards
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from models.states import PasswordManagerStates
from utils import BotUtils
from models.kv import *

callback_router = Router(name=__name__)


@callback_router.callback_query(PwdMgrCb.Enter.filter())
async def enter(query: CallbackQuery) -> Message:
    return await query.message.edit_text(
        text=ENTER_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_menu()
    )


@callback_router.callback_query(PwdMgrCb.EnterServices.filter())
async def enter_services(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.EnterServices) -> Message:
    services_offset = callback_data.services_offset

    commands = [
        PasswordManagerServicesOffset(services_offset),
        GetState(None, state.key)
    ]
    services, _ = await asyncio.gather(
        db_manager.relational_db.get_services(query.from_user.id, services_offset),
        db_manager.key_value_db.execute_batch(
            db_manager.key_value_db.set_pm_services_offset(),
            db_manager.key_value_db.set_state(None, state.key),
            storage_key=state.key
        )
    )

    return await query.message.edit_text(
        text=gen_services_text(services_offset),
        reply_markup=Keyboards.inline.pwd_mgr_services(services, services_offset),
    ) if services else await query.message.edit_text(
        text=NO_SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_no_services(),
    )


@callback_router.callback_query(PwdMgrCb.CreateService.filter())
async def create_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.CreateService) -> Message:
    services_offset = callback_data.services_offset

    commands = [
        MessageIdToDelete(query.message.message_id),
        PasswordManagerInputFormat(CREATE_SERVICE_TEXT),
        GetState(PasswordManagerStates.CreateService, state.key)
    ]
    record, _ = await asyncio.gather(
        db_manager.relational_db.get_rand_password(query.from_user.id),
        db_manager.key_value_db.execute_batch(*commands)
    )

    return await query.message.edit_text(
        text=CREATE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_services(services_offset)
    ) if record else await query.message.edit_text(
        text=WARNING + CREATE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_services(services_offset)
    )


@callback_router.callback_query(PwdMgrCb.DeleteServices.filter())
async def delete_services(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeleteServices) -> Message:
    services_offset = callback_data.services_offset

    await db_manager.key_value_db.execute_batch(
        MessageIdToDelete(query.message.message_id),
        PasswordManagerInputFormat(DELETE_SERVICES_TEXT),
        GetState(PasswordManagerStates.DeleteServices, state.key)
    )

    return await query.message.edit_text(
        text=DELETE_SERVICES_TEXT,
        reply_markup=Keyboards.inline.return_to_services(services_offset)
    )


@callback_router.callback_query(PwdMgrCb.EnterService.filter())
async def enter_service(query: CallbackQuery, callback_data: PwdMgrCb.EnterService, state: FSMContext) -> Optional[Message]:
    service, services_offset, pwd_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    commands = [
        Service(service),
        PasswordManagerPasswordsOffset(pwd_offset),
        PasswordManagerInputFormat(ASK_MASTER_PASSWORD_TEXT),
        GetState(PasswordManagerStates.EnterService, state.key)
    ]

    if query.message:
        commands.append(MessageIdToDelete(query.message.message_id))

    await db_manager.key_value_db.execute_batch(*commands)

    #  Default Callback
    if query.message:
        return await query.message.edit_text(
            text=ASK_MASTER_PASSWORD_TEXT,
            reply_markup=Keyboards.inline.return_to_services(services_offset)
        )

    #  Callback from inline_query (Message can't be deleted)
    await query.bot.send_message(
        chat_id=query.from_user.id,
        text=ASK_MASTER_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_services(services_offset)
    )


@callback_router.callback_query(PwdMgrCb.CreatePassword.filter())
async def create_password(query: CallbackQuery, callback_data: PwdMgrCb.CreatePassword, state: FSMContext) -> Message:
    service, services_offset, pwds_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await db_manager.key_value_db.execute_batch(
        Service(service),
        MessageIdToDelete(query.message.message_id),
        PasswordManagerInputFormat(CREATE_PASSWORD_TEXT),
        GetState(PasswordManagerStates.CreatePassword, state.key)
    )

    return await query.message.edit_text(
        text=CREATE_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_passwords(service, services_offset, pwds_offset)
    )


@callback_router.callback_query(PwdMgrCb.EnterPassword.filter())
async def enter_password(query: CallbackQuery, callback_data: PwdMgrCb.EnterPassword) -> Message:
    login, password = BotUtils.escape_markdown_v2(callback_data.login), BotUtils.escape_markdown_v2(callback_data.password)

    service, services_offset, pwds_offset = await db_manager.key_value_db.execute_batch(
        Service.key,
        PasswordManagerServicesOffset.key,
        PasswordManagerPasswordsOffset.key
    )

    return await query.message.edit_text(
        text=gen_credentials(service, login, password),
        reply_markup=Keyboards.inline.pwd_mgr_password(service, login, password, pwds_offset, services_offset),
        parse_mode="MarkdownV2"
    )


@callback_router.callback_query(PwdMgrCb.ChangeService.filter())
async def change_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.ChangeService) -> Message:
    old_service, services_offset, pwds_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await db_manager.key_value_db.execute_batch(
        GetState(PasswordManagerStates.ChangeService, state.key),
        Service(old_service),
        MessageIdToDelete(query.message.message_id),
        PasswordManagerInputFormat(CHANGE_SERVICE_TEXT)
    )

    return await query.message.edit_text(
        text=CHANGE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_passwords(old_service, services_offset, pwds_offset)
    )


@callback_router.callback_query(PwdMgrCb.DeleteService.filter())
async def delete_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeleteService) -> Message:
    service_to_delete, services_offset, pwds_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await db_manager.key_value_db.execute_batch(
        MessageIdToDelete(query.message.message_id),
        Service(service_to_delete),
        PasswordManagerInputFormat(DELETE_SERVICE_TEXT),
        GetState(PasswordManagerStates.DeleteService, state.key)
    )

    return await query.message.edit_text(
        text=DELETE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_passwords(service_to_delete, services_offset, pwds_offset)
    )


@callback_router.callback_query(PwdMgrCb.DeletePassword.filter())
async def delete_password(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeletePassword) -> Message:
    login, password = callback_data.login, callback_data.password  # No need to escape MarkdownV2

    service, _, _, _ = await asyncio.gather(
        db_manager.key_value_db.get_service(state),
        state.set_state(PasswordManagerStates.DeletePassword),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_pm_input_format_text(DELETE_PASSWORD_TEXT, state)
    )

    return await query.message.edit_text(
        text=gen_credentials(service, login, password) + BotUtils.escape_markdown_v2(DELETE_PASSWORD_TEXT),
        reply_markup=Keyboards.inline.return_to_password(login, password),
        parse_mode="MarkdownV2"
    )


@callback_router.callback_query(PwdMgrCb.ImportFromFile.filter())
async def import_from_file(query: CallbackQuery, state: FSMContext) -> Message:
    await asyncio.gather(
        state.set_state(PasswordManagerStates.ImportFromFile),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_pm_input_format_text(IMPORT_FROM_FILE_TEXT, state)
    )

    return await query.message.edit_text(
        text=IMPORT_FROM_FILE_TEXT,
        reply_markup=Keyboards.inline.return_to_pwd_mgr()
    )


@callback_router.callback_query(PwdMgrCb.ExportToFile.filter())
async def export_to_file(query: CallbackQuery, state: FSMContext) -> Message:
    await asyncio.gather(
        state.set_state(PasswordManagerStates.ExportToFile),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_pm_input_format_text(ASK_MASTER_PASSWORD_TEXT, state)
    )

    return await query.message.edit_text(
        text=ASK_MASTER_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_pwd_mgr()
    )
