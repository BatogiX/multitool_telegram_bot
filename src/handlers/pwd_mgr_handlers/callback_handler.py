from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import bot_cfg, db_manager
from keyboards import Keyboards
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from models.states import PasswordManagerStates
from utils import StorageUtils, BotUtils

ENTER_TEXT: str = "Choose option"
IMPORT_FROM_FILE_TEXT: str = "Please send the .csv file and enter your Master Password in caption"
SERVICES_TEXT: str = "Choose service"
NO_SERVICES_TEXT: str = "You don't have any services yet. Create one now?"
DELETE_SERVICES_TEXT: str = "Are you sure you want to delete all services?\n\nIf yes - please enter your Master Password"
ASK_MASTER_PASSWORD_TEXT: str = "Please enter your Master Password"
CREATE_PASSWORD_TEXT: str = "Please enter your <Master Password> <login> <password>"
CHANGE_SERVICE_TEXT: str = "Please enter new service name"
CONFIRMATION_TEXT: str = "\"I CONFIRM\""
DELETE_SERVICE_TEXT: str = f"Are you sure you want to delete this service?\n\nIf yes - please enter {CONFIRMATION_TEXT}"
DELETE_PASSWORD_TEXT: str = "Are you sure you want to delete this password?\n\nIf yes - please enter your <Master Password> <login> <password>"
CREATE_SERVICE_TEXT: str = "Please enter <Master Password> <service name> <login> <password>"
SERVICE_TEXT = "*Service*: "
LOGIN_TEXT = "\n\n*Login*: "
PASSWORD_TEXT = "\n*Password*: "
WARNING: str = (
    "❗WARNING❗\n"
    "If you lose your Master Password you won't be able to decrypt your passwords. "
    "We do not store your Master Password and key for encryption/decryption in any way, "
    "so we won't be able to recover it for you.\n\n"
    "Your Master Password must be at least 12 characters long and contain at least one number, "
    "one uppercase letter, one lowercase letter and one special character.\n\n"
)

callback_router = Router(name=__name__)


@callback_router.callback_query(PwdMgrCb.Enter.filter())
async def enter(query: CallbackQuery, state: FSMContext) -> Message:
    if await state.get_state() in PasswordManagerStates:
        await state.set_state(None)

    return await query.message.edit_text(
        text=ENTER_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_menu()
    )


@callback_router.callback_query(PwdMgrCb.EnterServices.filter())
async def enter_services(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.EnterServices) -> Message:
    if await state.get_state() in PasswordManagerStates:
        await state.set_state(None)

    offset = callback_data.services_offset
    await StorageUtils.set_pm_services_offset(state=state, offset=offset)
    services = await db_manager.relational_db.get_services(
        user_id=query.from_user.id, offset=offset, limit=bot_cfg.dynamic_buttons_limit)

    return await query.message.edit_text(
        text=SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_services(services=services, offset=offset),
        parse_mode="Markdown"
    ) if services else await query.message.edit_text(
        text=NO_SERVICES_TEXT,
        reply_markup=Keyboards.inline.pwd_mgr_no_services(),
        parse_mode="Markdown"
    )


@callback_router.callback_query(PwdMgrCb.CreateService.filter())
async def create_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.CreateService) -> Message:
    await state.set_state(PasswordManagerStates.CreateService)
    await StorageUtils.set_message_id_to_delete(state=state, message_id=query.message.message_id)
    offset = callback_data.services_offset

    await StorageUtils.set_pm_input_format_text(state=state, text=CREATE_SERVICE_TEXT)
    return await query.message.edit_text(
        text=WARNING + CREATE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_services(offset)
    )


@callback_router.callback_query(PwdMgrCb.DeleteServices.filter())
async def delete_services(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeleteServices) -> Message:
    await state.set_state(PasswordManagerStates.DeleteServices)
    await StorageUtils.set_message_id_to_delete(state=state, message_id=query.message.message_id)
    offset = callback_data.services_offset

    await StorageUtils.set_pm_input_format_text(state=state, text=DELETE_SERVICES_TEXT)
    return await query.message.edit_text(
        text=DELETE_SERVICES_TEXT,
        reply_markup=Keyboards.inline.return_to_services(offset=offset)
    )


@callback_router.callback_query(PwdMgrCb.EnterService.filter())
async def enter_service(query: CallbackQuery, callback_data: PwdMgrCb.EnterService, state: FSMContext) -> Message:
    service, pwd_offset = callback_data.service, callback_data.pwd_offset
    await state.set_state(PasswordManagerStates.EnterService)
    await StorageUtils.set_service(state, service)
    await StorageUtils.set_pm_pwd_offset(state, pwd_offset)
    await StorageUtils.set_pm_input_format_text(state=state, text=ASK_MASTER_PASSWORD_TEXT)

    if query.message:
        await StorageUtils.set_message_id_to_delete(state, query.message.message_id)
        return await query.message.edit_text(
            text=ASK_MASTER_PASSWORD_TEXT,
            reply_markup=Keyboards.inline.return_to_services(offset=pwd_offset)
        )
    else:
        message = await query.bot.send_message(
            chat_id=query.from_user.id,
            text=ASK_MASTER_PASSWORD_TEXT,
            reply_markup=Keyboards.inline.return_to_services(offset=pwd_offset)
        )
        await StorageUtils.set_message_id_to_delete(state, message.message_id)
        return message


@callback_router.callback_query(PwdMgrCb.CreatePassword.filter())
async def create_password(query: CallbackQuery, callback_data: PwdMgrCb.CreatePassword, state: FSMContext) -> Message:
    service = callback_data.service
    await state.set_state(PasswordManagerStates.CreatePassword)
    await StorageUtils.set_message_id_to_delete(state, query.message.message_id)
    await StorageUtils.set_service(state, service)

    await StorageUtils.set_pm_input_format_text(state, CREATE_PASSWORD_TEXT)
    return await query.message.edit_text(
        text=CREATE_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_services(offset=0)
    )


@callback_router.callback_query(PwdMgrCb.EnterPassword.filter())
async def enter_password(query: CallbackQuery, callback_data: PwdMgrCb.EnterPassword, state: FSMContext) -> Message:
    login, password = BotUtils.escape_markdown_v2(callback_data.login), BotUtils.escape_markdown_v2(callback_data.password)
    service: str = BotUtils.escape_markdown_v2(await StorageUtils.get_service(state))

    text = (
        SERVICE_TEXT + service +
        LOGIN_TEXT + f"`{login}`" +
        PASSWORD_TEXT + f"`{password}`"
    )

    return await query.message.edit_text(
        text=text,
        reply_markup=Keyboards.inline.pwd_mgr_password(offset=0, service=service),
        parse_mode="MarkdownV2"
    )


@callback_router.callback_query(PwdMgrCb.ChangeService.filter())
async def change_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.ChangeService) -> Message:
    old_service = callback_data.service
    await state.set_state(PasswordManagerStates.ChangeService)
    await StorageUtils.set_service(state, old_service)
    await StorageUtils.set_message_id_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, CHANGE_SERVICE_TEXT)
    return await query.message.edit_text(
        text=CHANGE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_services(offset=0)
    )


@callback_router.callback_query(PwdMgrCb.DeleteService.filter())
async def delete_service(query: CallbackQuery, state: FSMContext, callback_data: PwdMgrCb.DeleteService) -> Message:
    service_to_delete = callback_data.service
    await state.set_state(PasswordManagerStates.DeleteService)
    await StorageUtils.set_message_id_to_delete(state, query.message.message_id)
    await StorageUtils.set_service(state, service_to_delete)

    await StorageUtils.set_pm_input_format_text(state, DELETE_SERVICE_TEXT)
    return await query.message.edit_text(
        text=DELETE_SERVICE_TEXT,
        reply_markup=Keyboards.inline.return_to_services(offset=0)
    )


@callback_router.callback_query(PwdMgrCb.DeletePassword.filter())
async def delete_password(query: CallbackQuery, state: FSMContext) -> Message:
    await state.set_state(PasswordManagerStates.DeletePassword)
    await StorageUtils.set_message_id_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, DELETE_PASSWORD_TEXT)
    return await query.message.edit_text(
        text=DELETE_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_services(offset=0)
    )


@callback_router.callback_query(PwdMgrCb.ImportFromFile.filter())
async def import_from_file(query: CallbackQuery, state: FSMContext) -> Message:
    await state.set_state(PasswordManagerStates.ImportFromFile)
    await StorageUtils.set_message_id_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, IMPORT_FROM_FILE_TEXT)
    return await query.message.edit_text(
        text=IMPORT_FROM_FILE_TEXT,
        reply_markup=Keyboards.inline.return_to_pwd_mgr()
    )


@callback_router.callback_query(PwdMgrCb.ExportToFile.filter())
async def export_to_file(query: CallbackQuery, state: FSMContext) -> Message:
    await state.set_state(PasswordManagerStates.ExportToFile)
    await StorageUtils.set_message_id_to_delete(state, query.message.message_id)

    await StorageUtils.set_pm_input_format_text(state, ASK_MASTER_PASSWORD_TEXT)
    return await query.message.edit_text(
        text=ASK_MASTER_PASSWORD_TEXT,
        reply_markup=Keyboards.inline.return_to_pwd_mgr()
    )