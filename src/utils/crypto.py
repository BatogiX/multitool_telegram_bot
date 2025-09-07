from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config.crypto import CryptographyConfig


def get_crypto_cfg() -> CryptographyConfig:
    from config import CRYPTO_CFG  # Circular import # noqa: PLC0415

    return CRYPTO_CFG


def gen_salt() -> bytes:
    crypto_cfg = get_crypto_cfg()
    return secrets.token_bytes(crypto_cfg.salt_length)


def gen_secret() -> str:
    crypto_cfg = get_crypto_cfg()
    return secrets.token_urlsafe(crypto_cfg.salt_length)


def gen_nonce() -> bytes:
    crypto_cfg = get_crypto_cfg()
    return secrets.token_bytes(crypto_cfg.nonce_length)
