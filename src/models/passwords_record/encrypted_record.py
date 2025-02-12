class EncryptedRecord:
    iv: bytes
    tag: bytes
    ciphertext: bytes

    def __init__(self, iv: bytes, tag: bytes, ciphertext: bytes):
        self.iv = iv
        self.tag = tag
        self.ciphertext = ciphertext