import hashlib
import hmac
import os

VERIFY_ITERATIONS = 200_000
VERIFY_SALT_SIZE = 16


def hash_master_password(master_password: str) -> dict:
    salt = os.urandom(VERIFY_SALT_SIZE)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        master_password.encode("utf-8"),
        salt,
        VERIFY_ITERATIONS,
    )
    return {
        "salt": salt.hex(),
        "hash": pw_hash.hex(),
        "iterations": VERIFY_ITERATIONS,
    }


def verify_master_password(master_password: str, record: dict) -> bool:
    salt = bytes.fromhex(record["salt"])
    iterations = record.get("iterations", VERIFY_ITERATIONS)
    candidate_hash = hashlib.pbkdf2_hmac(
        "sha256",
        master_password.encode("utf-8"),
        salt,
        iterations,
    )
    stored_hash = bytes.fromhex(record["hash"])
    return hmac.compare_digest(candidate_hash, stored_hash)
