from __future__ import annotations

import asyncio
import csv
import re
from io import BytesIO
from typing import Union

import aiofiles
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
from cryptography.exceptions import InvalidTag
from pydantic import ValidationError

from database import db_manager
from config import bot_cfg
from utils import delete_file, download_file, delete_fsm_message
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from .pwd_mgr_crypto import DecryptedRecord, EncryptedRecord

MAX_CHAR_LIMIT = 64
MSG_ERROR_INVALID_FORMAT = "Wrong format"
MSG_ERROR_LONG_INPUT = "Login or password is too long"
MSG_ERROR_MASTER_PASS = "Wrong Master Password"


async def show_service_logins(
        message: Message,
        state: FSMContext,
        master_password: str,
        service: str
) -> tuple[list[DecryptedRecord], int, int]:
    pwd_offset, services_offset = await asyncio.gather(
        db_manager.key_value_db.get_pwds_offset(state),
        db_manager.key_value_db.get_services_offset(state),
    )
    encrypted_records = await db_manager.relational_db.get_passwords(
        user_id=message.from_user.id,
        service=service,
        offset=pwd_offset
    )
    decrypted_records = []
    for encrypted_record in encrypted_records:
        decrypted_records.append(await DecryptedRecord.decrypt(encrypted_record, master_password))

    return decrypted_records, pwd_offset, services_offset


def has_valid_input_length(login: str, password: str):
    """Checks if the combined input length exceeds the max character limit."""
    if len(f"{PwdMgrCb.EnterPassword.__prefix__}{bot_cfg.sep}{login}{bot_cfg.sep}{password}") > MAX_CHAR_LIMIT:
        raise ValueError(MSG_ERROR_LONG_INPUT)


async def create_password_record(decrypted_record: DecryptedRecord, user_id: int, master_password: str) -> None:
    encrypted_record = await EncryptedRecord.encrypt(decrypted_record, master_password)
    asyncio.create_task(db_manager.relational_db.create_password(user_id, encrypted_record.service, encrypted_record.ciphertext))


def split_user_input(user_input: str, maxsplit: int, sep: str = bot_cfg.sep) -> Union[str, tuple[str, ...]]:
    if maxsplit == 1:
        return user_input

    parts = tuple(user_input.split(sep=sep))
    if len(parts) == maxsplit:
        return parts
    else:
        raise Exception(MSG_ERROR_INVALID_FORMAT)


async def resend_user_input_request(
        state: FSMContext,
        message: Message,
        error_message: str,
        current_state: str,
) -> Message:
    coroutines = [
        db_manager.key_value_db.get_input_format_text(state),
        db_manager.key_value_db.set_state(current_state, state)
    ]
    input_format, _ = await db_manager.key_value_db.execute_batch(*coroutines)
    message_to_delete = await message.answer(
        text=f"{error_message}\n\n{input_format}",
        reply_markup=return_to_services(services_offset=0)
    )
    await db_manager.key_value_db.set_message_id_to_delete(message_to_delete.message_id, state)
    return message_to_delete


async def handle_message_deletion(state: FSMContext, message: Message) -> str:
    coroutines = [
        db_manager.key_value_db.get_state(state),
        db_manager.key_value_db.get_message_id_to_delete(state),
        db_manager.key_value_db.clear_state(state),
    ]
    results, _ = await asyncio.gather(
        db_manager.key_value_db.execute_batch(*coroutines),
        message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id),
    )
    current_state, message_id, _ = results
    await delete_fsm_message(message_id, message)
    return current_state


async def process_importing_from_file(message: Message, master_password: str):
    try:
        temp_file_path = await download_file(message)
    except Exception:
        raise

    try:
        async with aiofiles.open(temp_file_path, "r", encoding="utf-8") as f:
            content = await f.read()
            lines = content.splitlines()
    except Exception:
        raise
    finally:
        await delete_file(temp_file_path)

    encrypted_records = []
    reader = csv.DictReader(lines)
    for row in reader:
        service = row.get("url", None).replace(bot_cfg.sep, "")
        login = row.get("username", None).replace(bot_cfg.sep, "")
        password = row.get("password", None).replace(bot_cfg.sep, "")
        try:
            has_valid_input_length(login, password)
            decrypted_record = DecryptedRecord(service=service, login=login, password=password)
        except (ValueError, ValidationError):
            continue
        encrypted_records.append(await EncryptedRecord.encrypt(decrypted_record, master_password))

    await db_manager.relational_db.import_passwords(user_id=message.from_user.id, encrypted_records=encrypted_records)


async def process_exporting_to_file(master_password: str, user_id: int) -> BufferedInputFile:
    encrypted_records = await db_manager.relational_db.export_passwords(user_id=user_id)

    csv_lines = ['"url","username","password"']
    for encrypted_record in encrypted_records:
        decrypted_record = await DecryptedRecord.decrypt(encrypted_record, master_password)
        csv_lines.append(f'"{decrypted_record.service}","{decrypted_record.login}","{decrypted_record.password}"')

    csv_content = "\n".join(csv_lines).encode('utf-8')
    buffer = BytesIO(csv_content)

    return BufferedInputFile(file=buffer.read(), filename=f"{user_id}_passwords.csv")


async def validate_master_password(master_password: str, user_id: int) -> None:
    """
    Verifies the correctness of a master password.

    :param master_password: The user-provided master password.
    :param user_id: The ID of the user.
    :raise ValueError: If the password does not meet the required complexity.
    :raise InvalidTag: If the decryption fails due to an incorrect key or data corruption.
    """
    try:
        _validate_master_password(master_password)
    except ValueError:
        raise

    rand_encrypted_record = await db_manager.relational_db.get_rand_password(user_id)
    if not rand_encrypted_record:
        return

    try:
        await DecryptedRecord.decrypt(rand_encrypted_record, master_password)
    except InvalidTag:
        raise InvalidTag(MSG_ERROR_MASTER_PASS)


def _validate_master_password(master_password: str):
    """
    Validates if a master password meets security requirements.

    :param master_password: The password to validate.
    :raise ValueError: If the password does not meet the required complexity.
    """
    if len(master_password) < 12:
        raise ValueError("The Master Password must contain at least 12 characters.")
    if not re.search(r'[A-Z]', master_password):
        raise ValueError("The Master Password must contain at least one capital letter.")
    if not re.search(r'[a-z]', master_password):
        raise ValueError("The Master Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', master_password):
        raise ValueError("The Master Password must contain at least one digit.")
    if not re.search(r'[\W_]', master_password):
        raise ValueError("The Master Password must contain at least one special character.")
