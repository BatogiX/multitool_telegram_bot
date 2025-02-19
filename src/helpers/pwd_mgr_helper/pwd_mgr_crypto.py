import re
import secrets

from argon2.low_level import hash_secret_raw, Type
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, AEADEncryptionContext, CipherContext

from config import pwd_mgr_cfg, bot_cfg
from models.db_record.password_record import EncryptedRecord, DecryptedRecord
from .weak_pwd_exception import WeakPasswordException


class PasswordManagerCryptoHelper:
    """Class for password_record manager utils"""

    @staticmethod
    def gen_salt(size: int = pwd_mgr_cfg.SALT_LEN) -> bytes:
        """Generate salt (128-bit by default)"""
        return secrets.token_bytes(size)

    @staticmethod
    def _gen_iv(size: int = pwd_mgr_cfg.GCM_IV_SIZE) -> bytes:
        """Generate salt (96-bit recommended)"""
        return secrets.token_bytes(size)

    @staticmethod
    def validate_master_password(master_password: str) -> bool:
        """Validate Master Password"""
        if len(master_password) < 12:
            raise WeakPasswordException("The Master Password must contain at least 12 characters.")

        if not re.search(r'[A-Z]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one capital letter.")

        if not re.search(r'[a-z]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one lowercase letter.")

        if not re.search(r'[0-9]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one number.")

        if not re.search(r'[\W_]', master_password):
            raise WeakPasswordException("The Master Password must contain at least one special character.")

        return True

    @staticmethod
    def derive_key(
            master_password: str,
            salt: bytes,
            time_cost: int = pwd_mgr_cfg.ARGON2.TIME_COST,
            memory_cost: int = pwd_mgr_cfg.ARGON2.MEMORY_COST,
            parallelism: int = pwd_mgr_cfg.ARGON2.PARALLELISM,
            length: int = pwd_mgr_cfg.ARGON2.HASH_LEN
    ) -> bytes:
        """Derive 256-bit key from Master Password"""
        return hash_secret_raw(
            secret=master_password.encode(),
            salt=salt,
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=length,
            type=Type.ID
        )

    @staticmethod
    def encrypt_record(service: str, login: str, password: str, key: bytes) -> EncryptedRecord:
        record: str = f"{login}{bot_cfg.sep}{password}"
        iv: bytes = PasswordManagerCryptoHelper._gen_iv()
        cipher: Cipher[modes.GCM] = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor: AEADEncryptionContext = cipher.encryptor()
        ciphertext: bytes = encryptor.update(record.encode()) + encryptor.finalize()
        return EncryptedRecord(
            service=service,
            iv=iv,
            tag=encryptor.tag,
            ciphertext=ciphertext
        )

    @staticmethod
    def decrypt_record(encrypted_record: EncryptedRecord, key: bytes) -> DecryptedRecord | None:
        iv: bytes = encrypted_record.iv
        tag: bytes = encrypted_record.tag
        ciphertext: bytes = encrypted_record.ciphertext

        cipher: Cipher[modes.GCM] = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor: CipherContext = cipher.decryptor()
        try:
            decrypted_record: str = (decryptor.update(ciphertext) + decryptor.finalize()).decode()
        except InvalidTag:
            raise
        else:
            login, password = decrypted_record.split(bot_cfg.sep)
            return DecryptedRecord(
                service=encrypted_record.service,
                login=login,
                password=password
            )
