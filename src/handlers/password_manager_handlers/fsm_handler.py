from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from cryptography.exceptions import InvalidTag

from config import db_manager, bot_config as c
from keyboards import InlineKeyboards
from models.callback_data import PasswordManagerCallbackData as PwManCbData
from models.fsm_states import PasswordManagerStates
from models.passwords_record import DecryptedRecord, EncryptedRecord
from models.passwords_record.weak_password_exception import WeakPasswordException
from utils import BotUtils
from utils.fsm_data_utils import FSMDataUtils
from utils.password_manager_utils import PasswordManagerUtils as PwManUtils

fsm_router = Router(name=__name__)

MAX_CHAR_LIMIT: int = 64
MSG_ERROR_INVALID_FORMAT: str = "Wrong format"
MSG_ERROR_LONG_INPUT: str = "Login or password is too long"
MSG_ERROR_MASTER_PASS: str = "Wrong Master Password"


async def derive_key_from_master_password(master_password: str, message: Message) -> bytes | str:
    """Validates a master password, derives a key, and verifies correctness."""
    try:
        PwManUtils.validate_master_password(master_password)
    except WeakPasswordException as e:
        return str(e)

    salt: bytes = await db_manager.relational_db.get_salt(message.from_user.id)
    key: bytes = PwManUtils.derive_key(master_password, salt)
    rand_record: EncryptedRecord = await db_manager.relational_db.get_rand_passwords_record(message.from_user.id)

    if rand_record:
        try:
            PwManUtils.decrypt_passwords_record(rand_record.iv, rand_record.tag, rand_record.ciphertext, key)
        except InvalidTag:
            return ""
    return key


async def show_service_logins(message: Message, state: FSMContext, key: bytes) -> None:
    service: str = await FSMDataUtils.get_service(state)
    offset: int = await FSMDataUtils.get_pm_pwd_offset(state)
    encrypted_records: list[EncryptedRecord] = await db_manager.relational_db.get_passwords_records(
        user_id=message.from_user.id,
        service=service,
        offset=offset
    )
    decrypted_records: list[DecryptedRecord] = []
    for data in encrypted_records:
        decrypted_records.append(PwManUtils.decrypt_passwords_record(
            data.iv, data.tag, data.ciphertext, key)
        )
    text: str = (
        f"*Service:* {service}\n"
        "Choose your login to see password"
    )
    await message.answer(
        text=text,
        reply_markup=InlineKeyboards.passwd_man_passwords(decrypted_records, service, offset),
        parse_mode="Markdown"
    )


def has_valid_input_length(login: str, password: str) -> bool:
    """Checks if the combined input length exceeds the max character limit."""
    return len(f"{PwManCbData.EnterPassword.__prefix__}{c.sep}{login}{c.sep}{password}") <= MAX_CHAR_LIMIT


async def create_password_record(login: str, password: str, service: str, message: Message, key: bytes) -> None:
    data_to_encrypt: str = f"{login}{c.sep}{password}"
    encrypted_record: EncryptedRecord = PwManUtils.encrypt_passwords_record(data_to_encrypt, key)
    await db_manager.relational_db.create_password_record(
        user_id=message.from_user.id,
        service=service,
        iv=encrypted_record.iv,
        tag=encrypted_record.tag,
        ciphertext=encrypted_record.ciphertext
    )


async def split_user_input(message: Message, maxsplit: int, sep: str = c.sep) -> tuple:
    parts = tuple(message.text.split(sep=sep))
    return parts if len(parts) == maxsplit else tuple()


async def resend_user_input_request(
        state: FSMContext,
        message: Message,
        error_message: str,
        current_state: str,
        custom_error: str | None = None
) -> None:
    error_message: str = custom_error if custom_error else error_message
    await state.set_state(current_state)
    input_format: str = await FSMDataUtils.get_pm_input_format_text(state)
    message_to_delete: Message = await message.answer(
        text=f"{error_message}\n\n{input_format}",
        reply_markup=InlineKeyboards.return_to_passwd_man(offset=0)
    )
    await FSMDataUtils.set_message_to_delete(state, message_to_delete.message_id)


@fsm_router.message(StateFilter(PasswordManagerStates.CreateService), F.text)
async def create_service(message: Message, state: FSMContext):
    """Handler for creating a new password record with service."""
    current_state: str = await state.get_state()
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()
    user_input: tuple[str, ...] = await split_user_input(message=message, maxsplit=4)

    if not user_input:
        return await resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, service, login, password = user_input
    if not has_valid_input_length(login, password):
        return await resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    key: bytes | str = await derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state, custom_error)

    await create_password_record(login, password, service, message, key)
    await message.answer(
        text=f"*Service:* {service}\nChoose your login to see password",
        reply_markup=InlineKeyboards.passwd_man_passwords(
            decrypted_records=[DecryptedRecord(login=login, password=password)],
            service=service,
            offset=0
        ),
        parse_mode="Markdown"
    )
    await FSMDataUtils.set_service(state, service)


@fsm_router.message(StateFilter(PasswordManagerStates.CreatePassword), F.text)
async def create_password(message: Message, state: FSMContext):
    """Handler for creating a new password for an existing service."""
    current_state: str = await state.get_state()
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()
    user_input: tuple[str, ...] = await split_user_input(message=message, maxsplit=3)

    if not user_input:
        return await resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, login, password = user_input
    if not has_valid_input_length(login, password):
        return await resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    key: bytes | str = await derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state, custom_error)

    service: str = await FSMDataUtils.get_service(state)
    await create_password_record(login, password, service, message, key)
    await show_service_logins(message, state, key)


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingPassword), F.text)
async def delete_password(message: Message, state: FSMContext):
    """Handler for deleting password"""
    current_state: str = await state.get_state()
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()
    user_input: tuple[str, ...] = await split_user_input(message=message, maxsplit=3)

    if not user_input:
        return await resend_user_input_request(state, message, MSG_ERROR_INVALID_FORMAT, current_state)

    master_password, login, password = user_input
    if not has_valid_input_length(login, password):
        return await resend_user_input_request(state, message, MSG_ERROR_LONG_INPUT, current_state)

    key: bytes = await derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state, custom_error)

    service: str = await FSMDataUtils.get_service(state)
    encrypted_records: list[EncryptedRecord] = await db_manager.relational_db.get_passwords_records(
        message.from_user.id,
        service,
        offset=0
    )

    decrypted_records: list[DecryptedRecord] = []
    for data in encrypted_records:
        decrypted_record: DecryptedRecord = PwManUtils.decrypt_passwords_record(data.iv, data.tag,
                                                                                data.ciphertext, key)
        if decrypted_record.login == login and decrypted_record.password == password:
            await db_manager.relational_db.delete_passwords_record(message.from_user.id, service, data.ciphertext)
            continue
        decrypted_records.append(decrypted_record)

    if decrypted_records:
        text: str = (
            "Password was deleted successfully\n\n"
            f"*Service:* {service}\n"
            "Choose your login to see password"
        )
        offset: int = await FSMDataUtils.get_pm_pwd_offset(state)
        await message.answer(
            text=text,
            reply_markup=InlineKeyboards.passwd_man_passwords(decrypted_records, service, offset),
            parse_mode="Markdown"
        )
    else:
        text: str = "Password was deleted successfully\n\n"
        services: list[str] = await db_manager.relational_db.get_services(message.from_user.id, offset=0)
        if services:
            await message.answer(
                text=text + "Choose service",
                reply_markup=InlineKeyboards.passwd_man_services(services=services, offset=0)
            )
        else:
            await message.answer(
                text=text + "You don't have any services yet. Create one now?",
                reply_markup=InlineKeyboards.passwd_man_services(services=[], offset=0)
            )


@fsm_router.message(StateFilter(PasswordManagerStates.EnteringService), F.text)
async def service_enter(message: Message, state: FSMContext):
    current_state: str = await state.get_state()
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()

    master_password: str = message.text
    key: bytes = await derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state, custom_error)

    await show_service_logins(message, state, key)


@fsm_router.message(StateFilter(PasswordManagerStates.ChangeService), F.text)
async def change_service(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)

    new_service: str = message.text
    old_service: str = await FSMDataUtils.get_service(state)

    await db_manager.relational_db.change_service(
        new_service=new_service,
        user_id=message.from_user.id,
        old_service=old_service
    )

    services: list[str] = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
    await message.answer(
        text="Choose service",
        reply_markup=InlineKeyboards.passwd_man_services(services=services, offset=0)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingServices), F.text)
async def delete_services(message: Message, state: FSMContext):
    current_state: str = await state.get_state()
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()

    master_password: str = message.text
    key: bytes = await derive_key_from_master_password(master_password, message)
    if type(key) == str:
        custom_error: str = str(key)
        return await resend_user_input_request(state, message, MSG_ERROR_MASTER_PASS, current_state, custom_error)

    await db_manager.relational_db.delete_services(message.from_user.id)
    await message.answer(
        text="All services deleted successfully",
        reply_markup=InlineKeyboards.passwd_man_services(services=[], offset=0)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingService), F.text)
async def delete_service(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()

    answer: str = message.text
    if answer == "I CONFIRM":
        service: str = await FSMDataUtils.get_service(state)
        await db_manager.relational_db.delete_service(message.from_user.id, service)

        services: list[str] = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
        text: str = "Service was deleted successfully\n\n"
        if services:
            await message.answer(
                text=text + "Choose service",
                reply_markup=InlineKeyboards.passwd_man_services(services, offset=0)
            )
        else:
            await message.answer(
                text=text + "You don't have any services yet. Create one now?",
                reply_markup=InlineKeyboards.passwd_man_services(services=[], offset=0)
            )
    else:
        services: list[str] = await db_manager.relational_db.get_services(user_id=message.from_user.id, offset=0)
        text: str = "Service was not deleted\n\n"
        await message.answer(
            text=text + "Choose service",
            reply_markup=InlineKeyboards.passwd_man_services(services=services, offset=0)
        )
