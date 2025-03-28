from typing import Optional

import asyncio
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db_manager
from handlers.pwd_mgr_handlers.texts import ENTER_TEXT, IMPORT_FROM_FILE_TEXT, SERVICES_TEXT, NO_SERVICES_TEXT, DELETE_SERVICES_TEXT, ASK_MASTER_PASSWORD_TEXT, \
    CREATE_PASSWORD_TEXT, CHANGE_SERVICE_TEXT, DELETE_SERVICE_TEXT, DELETE_PASSWORD_TEXT, CREATE_SERVICE_TEXT, SERVICE_TEXT, LOGIN_TEXT, PASSWORD_TEXT, WARNING
from keyboards import Keyboards
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from models.states import PasswordManagerStates
from utils import BotUtils

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

    services, _, _ = await asyncio.gather(
        db_manager.relational_db.get_services(query.from_user.id, services_offset),
        db_manager.key_value_db.set_pm_services_offset(offset=services_offset, state=state),
        state.set_state(None)
    )

    return await query.message.edit_text(
        text=SERVICES_TEXT + str(services_offset + 1),
        reply_markup=Keyboards.inline.pwd_mgr_services(services, services_offset),
    ) if services else await query.message.edit_text(
        text=NO_SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_no_services(),
    )


@callback_router.callback_query(PwdMgrCb.CreateService.filter())
async def create_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.CreateService) -> Message:
    services_offset = callback_data.services_offset

    record, _, _, _ = await asyncio.gather(
        db_manager.relational_db.get_rand_password(query.from_user.id),
        state.set_state(PasswordManagerStates.CreateService),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_pm_input_format_text(CREATE_SERVICE_TEXT, state)
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

    await asyncio.gather(
        state.set_state(PasswordManagerStates.DeleteServices),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_pm_input_format_text(DELETE_SERVICES_TEXT, state)
    )

    return await query.message.edit_text(
        text=DELETE_SERVICES_TEXT,
        reply_markup=Keyboards.inline.return_to_services(services_offset)
    )


@callback_router.callback_query(PwdMgrCb.EnterService.filter())
async def enter_service(query: CallbackQuery, callback_data: PwdMgrCb.EnterService, state: FSMContext) -> Optional[Message]:
    service, services_offset, pwd_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await asyncio.gather(
        state.set_state(PasswordManagerStates.EnterService),
        db_manager.key_value_db.set_service(service, state),
        db_manager.key_value_db.set_pm_services_offset(services_offset, state),
        db_manager.key_value_db.set_pm_pwd_offset(pwd_offset, state),
        db_manager.key_value_db.set_pm_input_format_text(ASK_MASTER_PASSWORD_TEXT, state)
    )

    #   Default Callback
    if query.message:
        await db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state)
        return await query.message.edit_text(
            text=ASK_MASTER_PASSWORD_TEXT,
            reply_markup=Keyboards.inline.return_to_services(services_offset)
        )

    #   Callback from inline_query (Message can't be deleted)
    await query.bot.send_message(
        chat_id=query.from_user.id,
        text=ASK_MASTER_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_services(services_offset)
    )


@callback_router.callback_query(PwdMgrCb.CreatePassword.filter())
async def create_password(query: CallbackQuery, callback_data: PwdMgrCb.CreatePassword, state: FSMContext) -> Message:
    service, services_offset, pwds_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await asyncio.gather(
        state.set_state(PasswordManagerStates.CreatePassword),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_service(service, state),
        db_manager.key_value_db.set_pm_input_format_text(CREATE_PASSWORD_TEXT, state)
    )

    return await query.message.edit_text(
        text=CREATE_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_passwords(service, services_offset, pwds_offset)
    )


@callback_router.callback_query(PwdMgrCb.EnterPassword.filter())
async def enter_password(query: CallbackQuery, callback_data: PwdMgrCb.EnterPassword, state: FSMContext) -> Message:
    login, password = BotUtils.escape_markdown_v2(callback_data.login), BotUtils.escape_markdown_v2(callback_data.password)

    service, services_offset, pwds_offset = await asyncio.gather(
        db_manager.key_value_db.get_service(state),
        db_manager.key_value_db.get_pm_services_offset(state),
        db_manager.key_value_db.get_pm_pwd_offset(state)
    )
    service = BotUtils.escape_markdown_v2(service)

    text = (
        SERVICE_TEXT + service +
        LOGIN_TEXT + f"`{login}`" +
        PASSWORD_TEXT + f"`{password}`"
    )

    return await query.message.edit_text(
        text=text,
        reply_markup=Keyboards.inline.pwd_mgr_password(service, services_offset, pwds_offset),
        parse_mode="MarkdownV2"
    )


@callback_router.callback_query(PwdMgrCb.ChangeService.filter())
async def change_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.ChangeService) -> Message:
    old_service, services_offset, pwds_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await asyncio.gather(
        state.set_state(PasswordManagerStates.ChangeService),
        db_manager.key_value_db.set_service(old_service, state),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_pm_input_format_text(CHANGE_SERVICE_TEXT, state)
    )

    return await query.message.edit_text(
        text=CHANGE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_passwords(old_service, services_offset, pwds_offset)
    )


@callback_router.callback_query(PwdMgrCb.DeleteService.filter())
async def delete_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeleteService) -> Message:
    service_to_delete, services_offset, pwds_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await asyncio.gather(
        state.set_state(PasswordManagerStates.DeleteService),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_service(service_to_delete, state),
        db_manager.key_value_db.set_pm_input_format_text(DELETE_SERVICE_TEXT, state)
    )

    return await query.message.edit_text(
        text=DELETE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_passwords(service_to_delete, services_offset, pwds_offset)
    )


@callback_router.callback_query(PwdMgrCb.DeletePassword.filter())
async def delete_password(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeletePassword) -> Message:
    service, services_offset, pwds_offset = callback_data.service, callback_data.services_offset, callback_data.pwds_offset

    await asyncio.gather(
        state.set_state(PasswordManagerStates.DeletePassword),
        db_manager.key_value_db.set_message_id_to_delete(query.message.message_id, state),
        db_manager.key_value_db.set_pm_input_format_text(DELETE_PASSWORD_TEXT, state)
    )

    return await query.message.edit_text(
        text=DELETE_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_password(service, services_offset, pwds_offset)
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
