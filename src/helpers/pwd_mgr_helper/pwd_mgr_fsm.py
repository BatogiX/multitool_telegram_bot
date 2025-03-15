import csv
import re
from io import BytesIO

import aiofiles
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile

from config import bot_cfg, db_manager
from keyboards import Keyboards
from utils import BotUtils
from utils.storage_utils import StorageUtils
from models.callback_data import PasswordManagerCallbackData as PwdMgrCb
from . import EncryptedRecord, DecryptedRecord
from .weak_pwd_exception import WeakPasswordException

MAX_CHAR_LIMIT: int = 64


class PasswordManagerFsmHelper(BotUtils):
    @staticmethod
    def _validate_master_password(master_password: str) -> bool:
        """Validate Master Password"""
        if len(master_password) < 12:
            raise WeakPasswordException("The Master Password must contain at least 12 characters.")

        if not re.search(r'[A-Z]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one capital letter.")

        if not re.search(r'[a-z]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one lowercase letter.")

        if not re.search(r'[0-9]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one digit.")

        if not re.search(r'[\W_]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one special character.")

        return True

    @classmethod
    def is_master_password_weak(cls, master_password: str) -> str:
        try:
            cls._validate_master_password(master_password)
        except WeakPasswordException as e:
            return str(e)
        return ""

    @staticmethod
    async def show_service_logins(message: Message, state: FSMContext, master_password: str, service: str) -> None:
        pwd_offset = await StorageUtils.get_pm_pwd_offset(state)
        services_offset = await StorageUtils.get_pm_services_offset(state)
        encrypted_records = await db_manager.relational_db.get_passwords(
            user_id=message.from_user.id,
            service=service,
            offset=pwd_offset,
            limit=bot_cfg.dynamic_buttons_limit
        )
        decrypted_records: list[DecryptedRecord] = []
        for encrypted_record in encrypted_records:
            decrypted_records.append(DecryptedRecord.decrypt(encrypted_record, master_password))
        text = (
            f"*Service:* {service}\n"
            "Choose your login to see password"
        )
        await message.answer(
            text=text,
            reply_markup=Keyboards.inline.pwd_mgr_passwords(decrypted_records, service, pwd_offset, services_offset),
            parse_mode="Markdown"
        )

    @staticmethod
    def has_valid_input_length(login: str, password: str) -> bool:
        """Checks if the combined input length exceeds the max character limit."""
        return len(f"{PwdMgrCb.EnterPassword.__prefix__}{bot_cfg.sep}{login}{bot_cfg.sep}{password}") <= MAX_CHAR_LIMIT

    @staticmethod
    async def create_password_record(decrypted_record: DecryptedRecord, user_id: int, master_password: str) -> None:
        encrypted_record = EncryptedRecord.encrypt(decrypted_record, master_password)
        await db_manager.relational_db.create_password(user_id, encrypted_record.service, encrypted_record.ciphertext)

    @staticmethod
    async def split_user_input(user_input: str, maxsplit: int, sep: str = bot_cfg.sep) -> tuple:
        parts = tuple(user_input.split(sep=sep))
        return parts if len(parts) == maxsplit else tuple()

    @staticmethod
    async def resend_user_input_request(
            state: FSMContext,
            message: Message,
            error_message: str,
            current_state: str,
    ) -> None:
        await state.set_state(current_state)
        input_format = await StorageUtils.get_pm_input_format_text(state)
        message_to_delete = await message.answer(
            text=f"{error_message}\n\n{input_format}",
            reply_markup=Keyboards.inline.return_to_services(offset=0)
        )
        await StorageUtils.set_message_id_to_delete(state, message_to_delete.message_id)

    @staticmethod
    async def handle_message_deletion(state: FSMContext, message: Message) -> str:
        current_state = await state.get_state()
        await state.set_state(None)
        await BotUtils.delete_fsm_message(state, message)
        await message.delete()
        return current_state

    @classmethod
    async def process_importing_from_file(cls, message: Message, master_password: str):
        temp_file_path: str = await cls.download_file(message)

        async with aiofiles.open(temp_file_path, "r") as f:
            content: str = await f.read()
            lines: list[str] = content.splitlines()

        encrypted_records: list[EncryptedRecord] = []
        reader = csv.DictReader(lines)
        for row in reader:
            service: str = row.get("url", "").replace(bot_cfg.sep, "")
            login: str = row.get("username", "").replace(bot_cfg.sep, "")
            password: str = row.get("password", "").replace(bot_cfg.sep, "")
            decrypted_record = DecryptedRecord(service, login, password)
            if service and login and password:
                encrypted_records.append(EncryptedRecord.encrypt(decrypted_record, master_password))

        await db_manager.relational_db.import_passwords(user_id=message.from_user.id, encrypted_records=encrypted_records)
        await cls._delete_file(temp_file_path)

    @staticmethod
    async def process_exporting_to_file(master_password: str, user_id: int) -> BufferedInputFile:
        encrypted_records: list[EncryptedRecord] = await db_manager.relational_db.export_passwords(user_id=user_id)

        csv_lines = ['"url","username","password"']
        for encrypted_record in encrypted_records:
            decrypted_record: DecryptedRecord = DecryptedRecord.decrypt(encrypted_record, master_password)
            csv_lines.append(f'"{decrypted_record.service}","{decrypted_record.login}","{decrypted_record.password}"')

        csv_content = "\n".join(csv_lines).encode('utf-8')
        buffer = BytesIO(csv_content)

        return BufferedInputFile(file=buffer.read(), filename=f"{user_id}_passwords.csv")
