from __future__ import annotations

import asyncio
import base64

import argon2.low_level
import orjson
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from config import CRYPTO_CFG
from models.sql import DecryptedPassword, Password
from utils import add_protocol, strip_protocol
from utils.crypto import gen_nonce
from utils.fields import fields


def _derive_key(master_password: str, salt: bytes) -> bytes:
    return argon2.low_level.hash_secret_raw(
        secret=master_password.encode() + CRYPTO_CFG.pepper,
        salt=salt,
        time_cost=CRYPTO_CFG.argon2_time_cost,
        memory_cost=CRYPTO_CFG.argon2_memory_cost,
        parallelism=CRYPTO_CFG.argon2_parallelism,
        hash_len=CRYPTO_CFG.argon2_hash_length,
        type=CRYPTO_CFG.argon2_type,
    )


async def derive_key(master_password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit encryption key from a master password using Argon2.

    Args:
        master_password: The user-provided master password.
        salt: Salt for key derivation.

    Returns:
        Securely derived 256-bit key.
    """
    return await asyncio.to_thread(_derive_key, master_password, salt)


def _encrypt(derived_key: bytes, *decrypted_passwords: DecryptedPassword) -> list[Password]:
    aesgcm = AESGCM(derived_key)

    encrypted_records: list[Password] = []
    for decrypted_password in decrypted_passwords:
        nonce = gen_nonce()
        included_fields = {fields(DecryptedPassword).login, fields(DecryptedPassword).password}
        plaintext = decrypted_password.model_dump_json(include=included_fields).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

        user_id = decrypted_password.user_id
        service = strip_protocol(decrypted_password.service)
        b64 = base64.b64encode(nonce + ciphertext)
        encrypted_records.append(Password(user_id=user_id, service=service, ciphertext=b64))
    return encrypted_records


def _decrypt(derived_key: bytes, *passwords: Password) -> list[DecryptedPassword]:
    aesgcm = AESGCM(derived_key)

    decrypted_records: list[DecryptedPassword] = []
    for password in passwords:
        b64 = base64.b64decode(password.ciphertext)
        nonce = b64[: CRYPTO_CFG.nonce_length]
        ciphertext = b64[CRYPTO_CFG.nonce_length :]
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)  # Raises InvalidTag
        data: dict[str, str] = orjson.loads(plaintext)

        user_id = password.user_id
        service = add_protocol(password.service)
        login = data[fields(DecryptedPassword).login]
        passw = data[fields(DecryptedPassword).password]
        decrypted_records.append(DecryptedPassword(user_id=user_id, service=service, login=login, password=passw))
    return decrypted_records


async def decrypt_all(derived_key: bytes, *passwords: Password) -> list[DecryptedPassword]:
    return await asyncio.to_thread(_decrypt, derived_key, *passwords)


async def decrypt_one(derived_key: bytes, passwords: Password) -> DecryptedPassword:
    res = await asyncio.to_thread(_decrypt, derived_key, passwords)
    return res[0]


async def encrypt_all(derived_key: bytes, *decrypted_records: DecryptedPassword) -> list[Password]:
    return await asyncio.to_thread(_encrypt, derived_key, *decrypted_records)


async def encrypt_one(derived_key: bytes, decrypted_record: DecryptedPassword) -> Password:
    result = await asyncio.to_thread(_encrypt, derived_key, decrypted_record)
    return result[0]
