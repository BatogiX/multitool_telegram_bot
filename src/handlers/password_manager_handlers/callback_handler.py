from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import db_manager
from keyboards import InlineKeyboards
from models.callback_data import PasswordManagerCallbackData as PwManCb
from models.fsm_states import PasswordManagerStates
from utils.fsm_data_utils import FSMDataUtils

callback_router = Router(name=__name__)


@callback_router.callback_query(PwManCb.Enter.filter())
async def enter_password_manager_menu(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.Enter):
    if await state.get_state() in PasswordManagerStates:
        await state.set_state(None)

    offset = callback_data.services_offset
    services = await db_manager.relational_db.get_services(query.from_user.id, offset)
    if services:
        text = "Choose service"
        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboards.passwd_man_services(services=services, offset=offset)
        )
    else:
        text = "You don't have any services yet. Create one now?"
        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboards.passwd_man_services(services=[], offset=offset)
        )


@callback_router.callback_query(PwManCb.CreateService.filter())
async def create_service(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.CreateService, ):
    await state.set_state(PasswordManagerStates.CreateService)
    await FSMDataUtils.set_message_to_delete(state, query.message.message_id)
    offset = callback_data.services_offset

    warning: str = (
        "❗WARNING❗\n"
        "If you lose your Master Password you won't be able to decrypt your passwords. "
        "We do not store your Master Password and key for encryption/decryption in any way, "
        "so we won't be able to recover it for you.\n\n"
        "Your Master Password must be at least 12 characters long and contain at least one number, "
        "one uppercase letter, one lowercase letter and one special character.\n\n"
    )

    input_format: str = "Enter <Master Password> <service name> <login> <password>"
    await FSMDataUtils.set_pm_input_format_text(state, input_format)

    await query.message.edit_text(
        text=warning + input_format,
        reply_markup=InlineKeyboards.return_to_passwd_man(offset)
    )


@callback_router.callback_query(PwManCb.DeleteServices.filter())
async def delete_services(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.DeleteServices):
    await state.set_state(PasswordManagerStates.ConfirmDeletingServices)
    await FSMDataUtils.set_message_to_delete(state, query.message.message_id)
    offset = callback_data.services_offset

    text = (
        "Are you sure you want to delete all services?\n\n"
        "If yes - enter your Master Password"
    )
    await query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.return_to_passwd_man(offset)
    )


@callback_router.callback_query(PwManCb.EnterService.filter())
async def service_enter(query: CallbackQuery, callback_data: PwManCb.EnterService, state: FSMContext):
    service, offset = callback_data.service, callback_data.pwd_offset
    await state.set_state(PasswordManagerStates.EnteringService)
    await FSMDataUtils.set_service(state, service)
    await FSMDataUtils.set_message_to_delete(state, query.message.message_id)
    await FSMDataUtils.set_pm_pwd_offset(state, offset)

    text = "Enter your Master Password"
    await query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.return_to_passwd_man(offset=0)
    )


@callback_router.callback_query(PwManCb.CreatePassword.filter())
async def create_password(query: CallbackQuery, callback_data: PwManCb.CreatePassword, state: FSMContext):
    service = callback_data.service
    await state.set_state(PasswordManagerStates.CreatePassword)
    await FSMDataUtils.set_message_to_delete(state, query.message.message_id)
    await FSMDataUtils.set_service(state, service)

    input_format = (
        "Enter your <Master Password> <login> <password>"
    )
    await FSMDataUtils.set_pm_input_format_text(state, input_format)
    await query.message.edit_text(
        text=input_format,
        reply_markup=InlineKeyboards.return_to_passwd_man(offset=0)
    )


@callback_router.callback_query(PwManCb.EnterPassword.filter())
async def password_enter(query: CallbackQuery, callback_data: PwManCb.EnterPassword, state: FSMContext):
    login, password = callback_data.login, callback_data.password
    service: str = await FSMDataUtils.get_service(state)

    text = (
        f"*Service*: {service}\n"
        f"*Login*: `{login}`\n"
        f"*Password*: `{password}`"
    )

    await query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.passwd_man_password(offset=0),
        parse_mode="Markdown"
    )


@callback_router.callback_query(PwManCb.ChangeService.filter())
async def change_service(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.ChangeService):
    old_service = callback_data.service
    await state.set_state(PasswordManagerStates.ChangeService)
    await FSMDataUtils.set_service(state, old_service)
    await FSMDataUtils.set_message_to_delete(state, query.message.message_id)

    text = "Enter new service name"
    await query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.return_to_passwd_man(offset=0)
    )


@callback_router.callback_query(PwManCb.DeleteService.filter())
async def delete_service(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.DeleteService, ):
    service_to_delete = callback_data.service
    await state.set_state(PasswordManagerStates.ConfirmDeletingService)
    await FSMDataUtils.set_message_to_delete(state, query.message.message_id)
    await FSMDataUtils.set_service(state, service_to_delete)

    text = (
        "Are you sure you want to delete this service?\n\n"
        "If yes - please enter \"I CONFIRM\""
    )
    await query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.return_to_passwd_man(offset=0)
    )


@callback_router.callback_query(PwManCb.DeletePassword.filter())
async def delete_password(query: CallbackQuery, state: FSMContext):
    await state.set_state(PasswordManagerStates.ConfirmDeletingPassword)
    await FSMDataUtils.set_message_to_delete(state, query.message.message_id)

    input_format = (
        "Are you sure you want to delete this password?\n\n"
        "If yes - enter your <Master Password> <login> <password>"
    )
    await FSMDataUtils.set_pm_input_format_text(state, input_format)
    await query.message.edit_text(
        text=input_format,
        reply_markup=InlineKeyboards.return_to_passwd_man(offset=0)
    )
