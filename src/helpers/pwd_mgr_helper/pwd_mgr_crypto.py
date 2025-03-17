from __future__ import annotations

import base64
import json
import os
import re

from argon2.low_level import hash_secret_raw
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel

from config import db_manager, crypto_cfg

MSG_ERROR_MASTER_PASS = "Wrong Master Password"


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
        time_cost=crypto_cfg.argon2_time_cost,
        memory_cost=crypto_cfg.argon2_memory_cost,
        parallelism=crypto_cfg.argon2_parallelism,
        hash_len=crypto_cfg.argon2_hash_length,
        type=crypto_cfg.argon2_type,
    )
    return raw_key


class PasswordManagerCryptoHelper:
    """Provides cryptographic utilities for password management."""

    @classmethod
    async def validate_master_password(cls, master_password: str, user_id: int) -> None:
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
        if rand_encrypted_record:
            try:
                PasswordManagerCryptoHelper.DecryptedRecord.decrypt(rand_encrypted_record, master_password)
            except InvalidTag:
                raise InvalidTag(MSG_ERROR_MASTER_PASS)

    class EncryptedRecord(BaseModel):
        """
        Represents an encrypted record containing a service name and ciphertext.
        """
        service: str
        ciphertext: str

        @classmethod
        def encrypt(
            cls,
            decrypted_record: PasswordManagerCryptoHelper.DecryptedRecord,
            master_password: str
        ) -> PasswordManagerCryptoHelper.EncryptedRecord:
            """
            Encrypts login credentials.

            :param decrypted_record: The record containing login and password to be encrypted.
            :param master_password: The master password used for key derivation.
            :return: An EncryptedRecord instance containing the service name and ciphertext.
            """
            salt = os.urandom(crypto_cfg.argon2_random_salt_length)
            nonce = os.urandom(crypto_cfg.random_nonce_length)

            derived_key = derive_key(master_password, salt)
            aesgcm = AESGCM(derived_key)

            plaintext = json.dumps({
                "login": decrypted_record.login,
                "password": decrypted_record.password
            }).encode()

            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            ciphertext_with_salt_and_nonce_b64 = base64.urlsafe_b64encode(nonce + ciphertext + salt).decode()
            return cls(service=decrypted_record.service, ciphertext=ciphertext_with_salt_and_nonce_b64)

    class DecryptedRecord(BaseModel):
        """
        Represents a decrypted record containing a service name, login, and password.
        """
        service: str
        login: str
        password: str

        @classmethod
        def decrypt(
            cls,
            encrypted_record: PasswordManagerCryptoHelper.EncryptedRecord,
            master_password: str
        ) -> PasswordManagerCryptoHelper.DecryptedRecord:
            """
            Decrypts an `EncryptedRecord` and returns a `DecryptedRecord`.

            :param encrypted_record: The encrypted record to decrypt.
            :param master_password: The user's master password used to derive the decryption key.
            :return: A DecryptedRecord containing the service, login, and password.
            :raises InvalidTag: If the decryption fails due to an incorrect key or data corruption.
            """
            data = base64.urlsafe_b64decode(encrypted_record.ciphertext)

            nonce = data[:crypto_cfg.random_nonce_length]
            ciphertext = data[crypto_cfg.random_nonce_length:-crypto_cfg.argon2_random_salt_length]
            salt = data[-crypto_cfg.argon2_random_salt_length:]

            derived_key = derive_key(master_password, salt)
            aesgcm = AESGCM(derived_key)
            try:
                plaintext = aesgcm.decrypt(nonce, ciphertext, None).decode()
            except InvalidTag:
                raise

            login, password = json.loads(plaintext).values()
            return cls(service=encrypted_record.service, login=login, password=password)
