import json
import os
import tempfile
from datetime import datetime, timezone

VAULT_VERSION = 1


class VaultNotFoundError(Exception):
    pass


def vault_exists(path: str) -> bool:
    return os.path.isfile(path)


def create_new_vault_file(path: str, enc_salt: bytes, auth_record: dict, ciphertext: bytes) -> None:
    data = {
        "meta": {
            "salt": enc_salt.hex(),
            "auth": auth_record,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": VAULT_VERSION,
        },
        "ciphertext": ciphertext.decode("utf-8"),
    }
    _atomic_write(path, data)


def load_vault_file(path: str) -> dict:
    if not vault_exists(path):
        raise VaultNotFoundError(f"No vault found at '{path}'. Run 'init' first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_ciphertext(path: str, existing_data: dict, ciphertext: bytes) -> None:
    existing_data["ciphertext"] = ciphertext.decode("utf-8")
    _atomic_write(path, existing_data)


def _atomic_write(path: str, data: dict) -> None:
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".vault_tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)  # atomic on POSIX and Windows
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
