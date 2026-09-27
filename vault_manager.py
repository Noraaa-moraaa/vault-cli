import json
import uuid
from datetime import datetime, timezone

ENTRY_TYPES = ("password", "note", "lock_combo")


class EntryNotFoundError(Exception):
    pass


def new_empty_vault_data() -> dict:
    return {"entries": []}


def load_decrypted(plaintext_bytes: bytes) -> dict:
    return json.loads(plaintext_bytes.decode("utf-8"))


def dump_for_encryption(vault_data: dict) -> bytes:
    return json.dumps(vault_data, indent=2).encode("utf-8")


def add_entry(vault_data: dict, title: str, entry_type: str, fields: dict, tags=None) -> dict:
    if entry_type not in ENTRY_TYPES:
        raise ValueError(f"Unknown entry_type '{entry_type}'. Must be one of {ENTRY_TYPES}.")

    entry = {
        "id": str(uuid.uuid4()),
        "title": title,
        "entry_type": entry_type,
        "fields": fields,
        "tags": tags or [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    vault_data["entries"].append(entry)
    return entry


def list_entries(vault_data: dict, entry_type: str = None, tag: str = None) -> list:
    entries = vault_data["entries"]
    if entry_type:
        entries = [e for e in entries if e["entry_type"] == entry_type]
    if tag:
        entries = [e for e in entries if tag in e.get("tags", [])]
    return entries


def find_entry(vault_data: dict, entry_id: str) -> dict:
    for e in vault_data["entries"]:
        if e["id"] == entry_id or e["id"].startswith(entry_id):
            return e
    raise EntryNotFoundError(f"No entry found matching id '{entry_id}'.")


def search_entries(vault_data: dict, query: str) -> list:
    q = query.lower()
    results = []
    for e in vault_data["entries"]:
        haystack = e["title"].lower() + " " + " ".join(e.get("tags", [])).lower()
        if q in haystack:
            results.append(e)
    return results


def update_entry(vault_data: dict, entry_id: str, **updates) -> dict:
    entry = find_entry(vault_data, entry_id)
    for key, value in updates.items():
        if value is not None:
            if key == "fields":
                entry["fields"].update(value)
            else:
                entry[key] = value
    entry["updated_at"] = datetime.now(timezone.utc).isoformat()
    return entry


def delete_entry(vault_data: dict, entry_id: str) -> None:
    entry = find_entry(vault_data, entry_id)
    vault_data["entries"].remove(entry)
