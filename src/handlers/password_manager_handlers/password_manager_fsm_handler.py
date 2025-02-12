from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from cryptography.exceptions import InvalidTag

from config import db_manager
from keyboards import InlineKeyboards
from models.fsm_states import PasswordManagerStates
from models.passwords_record import DecryptedRecord, EncryptedRecord
from models.passwords_record.weak_password_exception import WeakPasswordException
from utils import BotUtils
from utils.fsm_data_utils import FSMDataUtils
from utils.password_manager_utils import PasswordManagerUtils
from config import sep

fsm_router = Router(name=__name__)


async def check_master_password(master_password: str, message: Message) -> bytes | None:
    try:
        PasswordManagerUtils.validate_master_password(master_password)
    except WeakPasswordException as e:
        await message.answer(str(e), reply_markup=InlineKeyboards.return_to_passwd_man())
        return None

    rand_encrypted_record: EncryptedRecord = await db_manager.relational_db.get_rand_passwords_record(message.from_user.id)
    salt: bytes = await db_manager.relational_db.get_salt(message.from_user.id)
    key: bytes = PasswordManagerUtils.derive_key(master_password, salt)
    if rand_encrypted_record:
        try:
            PasswordManagerUtils.decrypt_passwords_record(
                iv=rand_encrypted_record.iv,
                tag=rand_encrypted_record.tag,
                ciphertext=rand_encrypted_record.ciphertext,
                key=key
            )
        except InvalidTag:
            await message.answer("Wrong Master Password", reply_markup=InlineKeyboards.return_to_passwd_man())
            return None
    return key


async def create_password_record(login: str, password: str, service: str, message: Message, key: bytes) -> None:
    data_to_encrypt: str = f"{login}{sep}{password}"
    encrypted_record: EncryptedRecord = PasswordManagerUtils.encrypt_passwords_record(data_to_encrypt, key)

    await db_manager.relational_db.create_password_record(
        user_id=message.from_user.id,
        service=service,
        iv=encrypted_record.iv,
        tag=encrypted_record.tag,
        ciphertext=encrypted_record.ciphertext
    )


async def entering_service(message: Message, service: str, key: bytes) -> None:
    encrypted_record: list[EncryptedRecord] = await db_manager.relational_db.get_passwords_records(message.from_user.id, service)
    decrypted_data: list[DecryptedRecord] = []
    for data in encrypted_record:
        decrypted_data.append(PasswordManagerUtils.decrypt_passwords_record(data.iv, data.tag, data.ciphertext, key))

    text: str = (
        f"*Service:* {service}\n"
        "Choose your login to see password"
    )

    await message.answer(
        text=text,
        reply_markup=InlineKeyboards.passwd_man_passwords(decrypted_data, service),
        parse_mode="Markdown"
    )


@fsm_router.message(StateFilter(PasswordManagerStates.CreateService), F.text)
async def create_service(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()

    master_password, service, login, password = message.text.split()
    key: bytes = await check_master_password(master_password, message)
    if not key:
        return

    await create_password_record(
        login=login,
        password=password,
        service=service,
        message=message,
        key=key
    )

    data: list[DecryptedRecord] = [DecryptedRecord(login, password)]
    text: str = (
        f"*Service:* {service}\n"
        "Choose your login to see password"
    )

    await message.answer(
        text=text,
        reply_markup=InlineKeyboards.passwd_man_passwords(data, service),
        parse_mode="Markdown"
    )
    await FSMDataUtils.set_service(state, service)


@fsm_router.message(StateFilter(PasswordManagerStates.CreatePassword), F.text)
async def create_password(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()


    master_password, login, password = message.text.split()
    key: bytes = await check_master_password(master_password, message)
    if not key:
        return

    service: str = await FSMDataUtils.get_service(state)
    await create_password_record(
        login=login,
        password=password,
        service=service,
        message=message,
        key=key
    )

    await entering_service(message, service, key)


@fsm_router.message(StateFilter(PasswordManagerStates.EnteringService), F.text)
async def service_enter(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()

    master_password: str = message.text
    key: bytes = await check_master_password(master_password, message)
    if not key:
        return

    service: str = await FSMDataUtils.get_service(state)
    await entering_service(message, service, key)


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

    services: list[str] = await db_manager.relational_db.get_services(message.from_user.id)
    await message.answer(
        text="Choose service",
        reply_markup=InlineKeyboards.passwd_man_services(services)
    )


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingServices), F.text)
async def delete_services(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()

    master_password: str = message.text
    key: bytes = await check_master_password(master_password, message)
    if not key:
        return

    await db_manager.relational_db.delete_services(message.from_user.id)
    await message.answer(
        text="All services deleted successfully",
        reply_markup=InlineKeyboards.passwd_man_services()
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

        services: list[str] = await db_manager.relational_db.get_services(message.from_user.id)
        text: str = "Service was deleted successfully\n\n"
        if services:
            await message.answer(
                text=text + "Choose service",
                reply_markup=InlineKeyboards.passwd_man_services(services)
            )
        else:
            await message.answer(
                text=text + "You don't have any services yet. Create one now?",
                reply_markup=InlineKeyboards.passwd_man_services()
            )
    else:
        services: list[str] = await db_manager.relational_db.get_services(message.from_user.id)
        text: str = "Service was not deleted\n\n"
        await message.answer(
            text=text + "Choose service",
            reply_markup=InlineKeyboards.passwd_man_services(services)
        )


@fsm_router.message(StateFilter(PasswordManagerStates.ConfirmDeletingPassword), F.text)
async def delete_password(message: Message, state: FSMContext):
    await state.set_state(None)
    await BotUtils.delete_fsm_message(state, message)
    await message.delete()

    master_password, login, password = message.text.split(sep)
    key: bytes = await check_master_password(master_password, message)
    if not key:
        return

    service: str = await FSMDataUtils.get_service(state)
    encrypted_records: list[EncryptedRecord] = await db_manager.relational_db.get_passwords_records(
        message.from_user.id,
        service
    )

    decrypted_records: list[DecryptedRecord] = []
    for data in encrypted_records:
        decrypted_record: DecryptedRecord = PasswordManagerUtils.decrypt_passwords_record(data.iv, data.tag, data.ciphertext, key)
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
        await message.answer(
            text=text,
            reply_markup=InlineKeyboards.passwd_man_passwords(decrypted_records, service),
            parse_mode="Markdown"
        )
    else:
        text: str = "Password was deleted successfully\n\n"
        services: list[str] = await db_manager.relational_db.get_services(message.from_user.id)
        if services:
            await message.answer(
                text=text + "Choose service",
                reply_markup=InlineKeyboards.passwd_man_services(services)
            )
        else:
            await message.answer(
                text=text + "You don't have any services yet. Create one now?",
                reply_markup=InlineKeyboards.passwd_man_services()
            )
