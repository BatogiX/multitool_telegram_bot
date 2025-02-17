from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import db_manager
from keyboards import InlineKeyboards
from models.callback_data import PasswordManagerCallbackData as PwManCb
from models.fsm_states import PasswordManagerStates
from utils.storage_utils import StorageUtils

ENTER_TEXT = "Choose option"
IMPORT_FROM_FILE_TEXT = "Please send the file and enter your Master Password in caption"
SERVICES_TEXT = "*SERVICES*\n\nChoose service"
NO_SERVICES_TEXT = "*SERVICES*\n\nYou don't have any services yet. Create one now?"
DELETE_SERVICES_TEXT = "Are you sure you want to delete all services?\n\nIf yes - please enter your Master Password"
ASK_MASTER_PASSWORD_TEXT = "Please enter your Master Password"
CREATE_PASSWORD_TEXT = "Please enter your <Master Password> <login> <password>"
CHANGE_SERVICE_TEXT = "Please enter new service name"
DELETE_SERVICE_TEXT = "Are you sure you want to delete this service?\n\nIf yes - please enter \"I CONFIRM\""
DELETE_PASSWORD_TEXT = "Are you sure you want to delete this password?\n\nIf yes - please enter your <Master Password> <login> <password>"
CREATE_SERVICE_TEXT = "Please enter <Master Password> <service name> <login> <password>"
WARNING: str = (
    "❗WARNING❗\n"
    "If you lose your Master Password you won't be able to decrypt your passwords. "
    "We do not store your Master Password and key for encryption/decryption in any way, "
    "so we won't be able to recover it for you.\n\n"
    "Your Master Password must be at least 12 characters long and contain at least one number, "
    "one uppercase letter, one lowercase letter and one special character.\n\n"
)

callback_router = Router(name=__name__)


@callback_router.callback_query(PwManCb.Enter.filter())
async def enter(query: CallbackQuery, state: FSMContext):
    if await state.get_state() in PasswordManagerStates:
        await state.set_state(None)

    await query.message.edit_text(
        text=ENTER_TEXT,
        reply_markup=InlineKeyboards.pwd_mgr_menu()
    )


@callback_router.callback_query(PwManCb.EnterServices.filter())
async def enter_services(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.EnterServices):
    if await state.get_state() in PasswordManagerStates:
        await state.set_state(None)

    offset = callback_data.services_offset
    await StorageUtils.set_pm_services_offset(state=state, offset=offset)
    services = await db_manager.relational_db.get_services(user_id=query.from_user.id, offset=offset)
    if services:
        await query.message.edit_text(
            text=SERVICES_TEXT,
            reply_markup=InlineKeyboards.pwd_mgr_services(services=services, offset=offset),
            parse_mode="Markdown"
        )
    else:
        await query.message.edit_text(
            text=NO_SERVICES_TEXT,
            reply_markup=InlineKeyboards.pwd_mgr_services(services=[], offset=offset),
            parse_mode="Markdown"
        )


@callback_router.callback_query(PwManCb.CreateService.filter())
async def create_service(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.CreateService, ):
    await state.set_state(PasswordManagerStates.CreateService)
    await StorageUtils.set_message_to_delete(state=state, message_id=query.message.message_id)
    offset = callback_data.services_offset

    await StorageUtils.set_pm_input_format_text(state=state, text=CREATE_SERVICE_TEXT)
    await query.message.edit_text(
        text=WARNING + CREATE_SERVICE_TEXT,
        reply_markup=InlineKeyboards.return_to_services(offset)
    )


@callback_router.callback_query(PwManCb.DeleteServices.filter())
async def delete_services(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.DeleteServices):
    await state.set_state(PasswordManagerStates.DeleteServices)
    await StorageUtils.set_message_to_delete(state=state, message_id=query.message.message_id)
    offset = callback_data.services_offset

    await StorageUtils.set_pm_input_format_text(state=state, text=DELETE_SERVICES_TEXT)
    await query.message.edit_text(
        text=DELETE_SERVICES_TEXT,
        reply_markup=InlineKeyboards.return_to_services(offset=offset)
    )


@callback_router.callback_query(PwManCb.EnterService.filter())
async def enter_service(query: CallbackQuery, callback_data: PwManCb.EnterService, state: FSMContext):
    service, pwd_offset = callback_data.service, callback_data.pwd_offset
    await state.set_state(PasswordManagerStates.EnterService)
    await StorageUtils.set_service(state, service)
    await StorageUtils.set_pm_pwd_offset(state, pwd_offset)
    await StorageUtils.set_pm_input_format_text(state=state, text=ASK_MASTER_PASSWORD_TEXT)

    if query.message:
        await query.message.edit_text(
            text=ASK_MASTER_PASSWORD_TEXT,
            reply_markup=InlineKeyboards.return_to_services(offset=pwd_offset)
        )
        await StorageUtils.set_message_to_delete(state, query.message.message_id)
    else:
        message = await query.bot.send_message(
            chat_id=query.from_user.id,
            text=ASK_MASTER_PASSWORD_TEXT,
            reply_markup=InlineKeyboards.return_to_services(offset=pwd_offset)
        )
        await StorageUtils.set_message_to_delete(state, message.message_id)


@callback_router.callback_query(PwManCb.CreatePassword.filter())
async def create_password(query: CallbackQuery, callback_data: PwManCb.CreatePassword, state: FSMContext):
    service = callback_data.service
    await state.set_state(PasswordManagerStates.CreatePassword)
    await StorageUtils.set_message_to_delete(state, query.message.message_id)
    await StorageUtils.set_service(state, service)

    await StorageUtils.set_pm_input_format_text(state, CREATE_PASSWORD_TEXT)
    await query.message.edit_text(
        text=CREATE_PASSWORD_TEXT,
        reply_markup=InlineKeyboards.return_to_services(offset=0)
    )


@callback_router.callback_query(PwManCb.EnterPassword.filter())
async def enter_password(query: CallbackQuery, callback_data: PwManCb.EnterPassword, state: FSMContext):
    login, password = callback_data.login, callback_data.password
    service: str = await StorageUtils.get_service(state)

    text = (
        f"*Service*: {service}\n\n"
        f"*Login*: `{login}`\n"
        f"*Password*: `{password}`"
    )

    await query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.pwd_mgr_password(offset=0, service=service),
        parse_mode="Markdown"
    )


@callback_router.callback_query(PwManCb.ChangeService.filter())
async def change_service(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.ChangeService):
    old_service = callback_data.service
    await state.set_state(PasswordManagerStates.ChangeService)
    await StorageUtils.set_service(state, old_service)
    await StorageUtils.set_message_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, CHANGE_SERVICE_TEXT)
    await query.message.edit_text(
        text=CHANGE_SERVICE_TEXT,
        reply_markup=InlineKeyboards.return_to_services(offset=0)
    )


@callback_router.callback_query(PwManCb.DeleteService.filter())
async def delete_service(query: CallbackQuery, state: FSMContext, callback_data: PwManCb.DeleteService, ):
    service_to_delete = callback_data.service
    await state.set_state(PasswordManagerStates.DeleteService)
    await StorageUtils.set_message_to_delete(state, query.message.message_id)
    await StorageUtils.set_service(state, service_to_delete)

    await StorageUtils.set_pm_input_format_text(state, DELETE_SERVICE_TEXT)
    await query.message.edit_text(
        text=DELETE_SERVICE_TEXT,
        reply_markup=InlineKeyboards.return_to_services(offset=0)
    )


@callback_router.callback_query(PwManCb.DeletePassword.filter())
async def delete_password(query: CallbackQuery, state: FSMContext):
    await state.set_state(PasswordManagerStates.DeletePassword)
    await StorageUtils.set_message_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, DELETE_PASSWORD_TEXT)
    await query.message.edit_text(
        text=DELETE_PASSWORD_TEXT,
        reply_markup=InlineKeyboards.return_to_services(offset=0)
    )


@callback_router.callback_query(PwManCb.ImportFromFile.filter())
async def import_from_file(query: CallbackQuery, state: FSMContext):
    await state.set_state(PasswordManagerStates.ImportFromFile)
    await StorageUtils.set_message_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, IMPORT_FROM_FILE_TEXT)
    await query.message.edit_text(
        text=IMPORT_FROM_FILE_TEXT,
        reply_markup=InlineKeyboards.return_to_pwd_mgr()
    )


@callback_router.callback_query(PwManCb.ExportToFile.filter())
async def export_to_file(query: CallbackQuery, state: FSMContext):
    await state.set_state(PasswordManagerStates.ExportToFile)
    await StorageUtils.set_message_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, ASK_MASTER_PASSWORD_TEXT)
    await query.message.edit_text(
        text=ASK_MASTER_PASSWORD_TEXT,
        reply_markup=InlineKeyboards.return_to_pwd_mgr()
    )