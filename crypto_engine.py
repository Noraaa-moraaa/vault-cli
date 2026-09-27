import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PBKDF2_ITERATIONS = 200_000
SALT_SIZE = 16


class DecryptionError(Exception):
    pass


def generate_salt() -> bytes:
    return os.urandom(SALT_SIZE)


def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key_bytes = kdf.derive(master_password.encode("utf-8"))
    return base64.urlsafe_b64encode(key_bytes)


def encrypt(plaintext: bytes, master_password: str, salt: bytes) -> bytes:
    key = derive_key(master_password, salt)
    fernet = Fernet(key)
    return fernet.encrypt(plaintext)


def decrypt(ciphertext: bytes, master_password: str, salt: bytes) -> bytes:
    key = derive_key(master_password, salt)
    fernet = Fernet(key)
    try:
        return fernet.decrypt(ciphertext)
    except InvalidToken:
        raise DecryptionError("Incorrect master password or corrupted vault file.")
