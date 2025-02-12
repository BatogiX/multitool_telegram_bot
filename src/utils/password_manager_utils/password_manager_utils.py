import re
import secrets

from argon2.low_level import hash_secret_raw, Type
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes, AEADEncryptionContext, CipherContext

from config import pm_config, bot_config as c
from models.passwords_record import EncryptedRecord, DecryptedRecord
from models.passwords_record.weak_password_exception import WeakPasswordException


class PasswordManagerUtils:
    """Class for passwords_record manager utils"""

    @staticmethod
    def gen_salt(size: int = pm_config.SALT_LEN) -> bytes:
        """Generate salt (128-bit by default)"""
        return secrets.token_bytes(size)

    @staticmethod
    def _gen_iv(size: int = pm_config.GCM_IV_SIZE) -> bytes:
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
            master_password: str, salt: bytes,
            time_cost: int = pm_config.ARGON2.TIME_COST,
            memory_cost: int = pm_config.ARGON2.MEMORY_COST,
            parallelism: int = pm_config.ARGON2.PARALLELISM,
            length: int = pm_config.ARGON2.HASH_LEN
    ) -> bytes:
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
    def encrypt_passwords_record(data: str, key: bytes) -> EncryptedRecord:
        iv: bytes = PasswordManagerUtils._gen_iv()
        cipher: Cipher[modes.GCM] = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor: AEADEncryptionContext = cipher.encryptor()
        ciphertext: bytes = encryptor.update(data.encode()) + encryptor.finalize()
        return EncryptedRecord(
            iv=iv,
            tag=encryptor.tag,
            ciphertext=ciphertext
        )

    @staticmethod
    def decrypt_passwords_record(iv: bytes, tag: bytes, ciphertext: bytes, key: bytes) -> DecryptedRecord | None:
        cipher: Cipher[modes.GCM] = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor: CipherContext = cipher.decryptor()
        try:
            decrypted_record: str = (decryptor.update(ciphertext) + decryptor.finalize()).decode()
        except InvalidTag:
            raise
        else:
            login, password = decrypted_record.split(c.sep)
            return DecryptedRecord(
                login=login,
                password=password
            )
