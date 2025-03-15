import base64
import json
import os
from dataclasses import dataclass

from argon2.low_level import hash_secret_raw, Type
from argon2 import (
    DEFAULT_MEMORY_COST,
    DEFAULT_HASH_LENGTH,
    DEFAULT_PARALLELISM,
    DEFAULT_RANDOM_SALT_LENGTH,
    DEFAULT_TIME_COST,
)
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import db_manager

DEFAULT_RANDOM_NONCE_LENGTH = 16

class PasswordManagerCryptoHelper:
    @classmethod
    async def is_master_password_valid(cls, master_password: str, user_id: int) -> bool:
        """Verifies correctness of master password."""
        rand_encrypted_record: EncryptedRecord = await db_manager.relational_db.get_rand_password(user_id)
        if rand_encrypted_record:
            try:
                DecryptedRecord.decrypt(rand_encrypted_record, master_password)
            except InvalidTag:
                return False
        return True

    @staticmethod
    def derive_key(master_password: str, salt: bytes) -> bytes:
        """
        Derive a 256-bit encryption key from a master password using Argon2.

        :param master_password: The user-provided master password.
        :param salt: Salt for key derivation.
        :return: A securely derived 256-bit key.
        """
        raw_key = hash_secret_raw(
            secret=master_password.encode(),
            salt=salt,
            time_cost=DEFAULT_TIME_COST,
            memory_cost=DEFAULT_MEMORY_COST,
            parallelism=DEFAULT_PARALLELISM,
            hash_len=DEFAULT_HASH_LENGTH,
            type=Type.ID
        )
        return raw_key



@dataclass(frozen=True)
class EncryptedRecord:
    """
    Represents an encrypted record containing a service name and ciphertext.
    """
    service: str
    ciphertext: str

    @classmethod
    def encrypt(cls, decrypted_record: "DecryptedRecord", master_password: str) -> "EncryptedRecord":
        """
        Encrypts login credentials.

        :param decrypted_record: The record containing login and password to be encrypted.
        :param master_password: The master password used for key derivation.
        :return: An EncryptedRecord instance containing the service name and ciphertext.
        """
        salt = os.urandom(DEFAULT_RANDOM_SALT_LENGTH)
        nonce = os.urandom(DEFAULT_RANDOM_NONCE_LENGTH)

        derived_key = derive_key(master_password, salt)
        aesgcm = AESGCM(derived_key)

        plaintext = json.dumps({
            "login": decrypted_record.login,
            "password": decrypted_record.password
        }).encode()

        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        ciphertext_with_salt_nonce = base64.urlsafe_b64encode(nonce + ciphertext + salt).decode()
        return cls(service=decrypted_record.service, ciphertext=ciphertext_with_salt_nonce)


@dataclass(frozen=True)
class DecryptedRecord:
    """
    Represents a decrypted record containing a service name, login, and password.
    """
    service: str
    login: str
    password: str

    @classmethod
    def decrypt(cls, encrypted_record: EncryptedRecord, master_password: str) -> "DecryptedRecord":
        """
        Decrypts an `EncryptedRecord` and returns a `DecryptedRecord`.

        :param encrypted_record: The encrypted record to decrypt.
        :param master_password: The user's master password used to derive the decryption key.
        :return: A DecryptedRecord containing the service, login, and password.
        :raises InvalidTag: If the decryption fails due to an incorrect key or data corruption.
        """
        data = base64.urlsafe_b64decode(encrypted_record.ciphertext)

        nonce = data[:DEFAULT_RANDOM_NONCE_LENGTH]
        ciphertext = data[DEFAULT_RANDOM_NONCE_LENGTH:-DEFAULT_RANDOM_SALT_LENGTH]
        salt = data[-DEFAULT_RANDOM_SALT_LENGTH:]

        derived_key = derive_key(master_password, salt)
        aesgcm = AESGCM(derived_key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None).decode()
        except InvalidTag:
            raise

        login, password = json.loads(plaintext).values()
        return cls(service=encrypted_record.service, login=login, password=password)
