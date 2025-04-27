from __future__ import annotations

import asyncio
import base64
import json
import os
from typing import Iterable

import argon2.low_level
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel

from config import crypto_cfg
from utils import add_protocol, strip_protocol


def gen_salt() -> bytes:
    return os.urandom(crypto_cfg.argon2_random_salt_length)


def gen_nonce() -> bytes:
    return os.urandom(crypto_cfg.random_nonce_length)


async def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit encryption key from a master password using Argon2.

    :param master_password: The user-provided master password.
    :param salt: Salt for key derivation.
    :return: A securely derived 256-bit key.
    """
    return await asyncio.to_thread(_derive_key, master_password, salt)


def _derive_key(master_password: str, salt: bytes) -> bytes:
    raw_key = argon2.low_level.hash_secret_raw(
        secret=master_password.encode() + crypto_cfg.pepper,
        salt=salt,
        time_cost=crypto_cfg.argon2_time_cost,
        memory_cost=crypto_cfg.argon2_memory_cost,
        parallelism=crypto_cfg.argon2_parallelism,
        hash_len=crypto_cfg.argon2_hash_length,
        type=crypto_cfg.argon2_type,
    )
    return raw_key


class EncryptedRecord(BaseModel):
    """
    Represents an encrypted record containing a service name and ciphertext.
    """
    service: str
    ciphertext: str

    @classmethod
    async def encrypt(
        cls,
        decrypted_records: Iterable[DecryptedRecord],
        derived_key: bytes
    ) -> list[EncryptedRecord]:
        """
        Encrypts login credentials.

        :param decrypted_records: The record containing login and password to be encrypted.
        :param derived_key: Derived key from Argon2.
        :return: An EncryptedRecord instance containing the service name and ciphertext.
        """
        return await asyncio.to_thread(cls._encrypt, decrypted_records, derived_key)

    @classmethod
    def _encrypt(
        cls,
        decrypted_records: Iterable[DecryptedRecord],
        derived_key: bytes
    ) -> list[EncryptedRecord]:
        aesgcm = AESGCM(derived_key)

        encrypted_records = []
        for decrypted_record in decrypted_records:
            nonce = gen_nonce()
            plaintext = decrypted_record.model_dump_json(exclude={"service"}).encode("utf-8")
            ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
            b64 = base64.urlsafe_b64encode(nonce + ciphertext).decode()

            service = strip_protocol(decrypted_record.service)
            encrypted_records.append(cls(service=service, ciphertext=b64))
        return encrypted_records


class DecryptedRecord(BaseModel):
    """
    Represents a decrypted record containing a service name, login, and password.
    """
    service: str
    login: str
    password: str

    @classmethod
    async def decrypt(
        cls,
        encrypted_record: Iterable[EncryptedRecord],
        derived_key: bytes
    ) -> list[DecryptedRecord]:
        """
        Decrypts an `EncryptedRecord` and returns a `DecryptedRecord`.

        :param encrypted_record: The encrypted record to decrypt.
        :param derived_key: The user's master password used to derive the decryption key.
        :return: A DecryptedRecord containing the service, login, and password.
        :raises InvalidTag: If the decryption fails due to an incorrect key or data corruption.
        """
        return await asyncio.to_thread(cls._decrypt, encrypted_record, derived_key)

    @classmethod
    def _decrypt(
        cls,
        encrypted_records: Iterable[EncryptedRecord],
        derived_key: bytes
    ) -> list[DecryptedRecord]:
        aesgcm = AESGCM(derived_key)

        decrypted_records = []
        for encrypted_record in encrypted_records:
            b64 = base64.urlsafe_b64decode(encrypted_record.ciphertext)
            nonce = b64[:crypto_cfg.random_nonce_length]
            ciphertext = b64[crypto_cfg.random_nonce_length:]

            try:
                plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
            except InvalidTag:
                raise

            data = json.loads(plaintext.decode("utf-8"))
            data["service"] = add_protocol(encrypted_record.service)
            decrypted_records.append(cls(**data))
        return decrypted_records
