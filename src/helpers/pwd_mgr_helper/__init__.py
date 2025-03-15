from .pwd_mgr_crypto import EncryptedRecord, DecryptedRecord
from .pwd_mgr_fsm import PasswordManagerFsmHelper


class PasswordManagerHelper(
    EncryptedRecord,
    DecryptedRecord,
    PasswordManagerFsmHelper,
):
    pass


__all__ = "PasswordManagerHelper"
