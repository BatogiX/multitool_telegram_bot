from __future__ import annotations

import asyncio
import csv
import re
from io import BytesIO

import aiofiles
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
from cryptography.exceptions import InvalidTag
from pydantic import ValidationError

import keyboards.inline
from config import bot_cfg
from database import db
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from utils import delete_file, download_file, delete_fsm_message
from . import derive_key
from .pwd_mgr_crypto import DecryptedRecord, EncryptedRecord

MAX_CHAR_LIMIT = 64
MAX_SERVICE_CHAR_LIMIT = 45
MSG_ERROR_INVALID_FORMAT = "Wrong format"
MSG_ERROR_LONG_INPUT = "Login or password is too long"
MSG_ERROR_MASTER_PASS = "Wrong Master Password"
MIN_RECORD_LENGTH = len(f"{PwdMgrCb.EnterPassword.__prefix__}{bot_cfg.sep}{bot_cfg.sep}")


async def show_service_logins(
    message: Message,
    state: FSMContext,
    derived_key: bytes,
    service: str
) -> tuple[list[DecryptedRecord], int, int]:
    pwd_offset, services_offset = await db.key_value.execute_batch(
        db.key_value.get_pwds_offset(state),
        db.key_value.get_services_offset(state),
    )
    encrypted_records = await db.relational.get_passwords(
        user_id=message.from_user.id,
        service=service,
        offset=pwd_offset
    )
    decrypted_records = await DecryptedRecord.decrypt(encrypted_records, derived_key)

    return decrypted_records, pwd_offset, services_offset


def has_valid_input_length(login: str, password: str) -> None:
    """Checks if the combined input length exceeds the max character limit."""
    record_length = MIN_RECORD_LENGTH + len(login + password)
    if record_length > MAX_CHAR_LIMIT:
        raise ValueError(MSG_ERROR_LONG_INPUT)


def has_valid_service_length(service: str) -> None:
    if len(service) > MAX_SERVICE_CHAR_LIMIT:
        raise ValueError(f"Service must be <= {MAX_SERVICE_CHAR_LIMIT} symbols length")


async def create_password_record(
    decrypted_record: DecryptedRecord, user_id: int, derived_key: bytes
) -> None:
    encrypted_record = await EncryptedRecord.encrypt(decrypted_record, derived_key)
    await db.relational.create_password(
        user_id, encrypted_record.service, encrypted_record.ciphertext
    )


def split_user_input(user_input: str, maxsplit: int, sep: str = bot_cfg.sep) -> tuple[str, ...]:
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
    input_format, _ = await db.key_value.execute_batch(
        db.key_value.get_input_format_text(state),
        db.key_value.set_state(current_state, state)
    )
    message_to_delete = await message.answer(
        text=f"{error_message}\n\n{input_format}",
        reply_markup=keyboards.inline.return_to_services_ikm(services_offset=0)
    )
    await db.key_value.set_message_id_to_delete(message_to_delete.message_id, state)
    return message_to_delete


async def handle_message_deletion(state: FSMContext, message: Message) -> str:
    results, _ = await asyncio.gather(
        db.key_value.execute_batch(
            db.key_value.get_state(state),
            db.key_value.get_message_id_to_delete(state),
            db.key_value.clear_state(state)
        ),
        message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id),
    )
    current_state, message_id, _ = results
    await delete_fsm_message(message_id, message)
    return current_state


async def process_importing_from_file(message: Message, derived_key: bytes):
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

    decrypted_records = []
    reader = csv.DictReader(lines)
    for row in reader:
        service = row.get("url", "").replace(bot_cfg.sep, "")
        login = row.get("username", "").replace(bot_cfg.sep, "")
        password = row.get("password", "").replace(bot_cfg.sep, "")
        try:
            has_valid_service_length(service)
            has_valid_input_length(login, password)
            decrypted_record = DecryptedRecord(service=service, login=login, password=password)
        except (ValueError, ValidationError):
            continue
        decrypted_records.append(decrypted_record)
    encrypted_records = await EncryptedRecord.encrypt(decrypted_records, derived_key)

    await db.relational.import_passwords(
        user_id=message.from_user.id, encrypted_records=encrypted_records
    )


async def process_exporting_to_file(derived_key: bytes, user_id: int) -> BufferedInputFile:
    encrypted_records = await db.relational.export_passwords(user_id=user_id)
    decrypted_records = await DecryptedRecord.decrypt(encrypted_records, derived_key)

    csv_lines = ['"url","username","password"']
    for record in decrypted_records:
        csv_lines.append(
            f'"{record.service}","{record.login}","{record.password}"'
        )

    csv_content = "\n".join(csv_lines).encode('utf-8')
    buffer = BytesIO(csv_content)

    return BufferedInputFile(file=buffer.read(), filename=f"{user_id}_passwords.csv")


async def validate_master_password(master_password: str, user_id: int) -> bytes:
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

    salt = await db.relational.get_salt(user_id)
    return await derive_key(master_password, salt)


async def validate_derived_key(user_id: int, derived_key: bytes) -> None:
    rand_encrypted_record = await db.relational.get_rand_password(user_id)
    if rand_encrypted_record:
        try:
            await DecryptedRecord.decrypt(rand_encrypted_record, derived_key)
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
