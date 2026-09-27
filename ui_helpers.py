import getpass
import sys

try:
    import pyperclip
    _CLIPBOARD_AVAILABLE = True
except ImportError:
    _CLIPBOARD_AVAILABLE = False


def prompt_master_password(confirm: bool = False) -> str:
    pw = getpass.getpass("Master password: ")
    if confirm:
        pw2 = getpass.getpass("Confirm master password: ")
        if pw != pw2:
            print("Passwords do not match.", file=sys.stderr)
            sys.exit(1)
    return pw


def copy_to_clipboard(text: str) -> bool:
    if not _CLIPBOARD_AVAILABLE:
        return False
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def print_entry_table(entries: list) -> None:
    if not entries:
        print("(no entries found)")
        return

    print(f"{'ID':<10} {'TYPE':<12} {'TITLE':<30} TAGS")
    print("-" * 70)
    for e in entries:
        short_id = e["id"][:8]
        tags = ", ".join(e.get("tags", []))
        print(f"{short_id:<10} {e['entry_type']:<12} {e['title'][:30]:<30} {tags}")


def print_entry_detail(entry: dict, reveal_secrets: bool = False) -> None:
    print(f"ID:      {entry['id']}")
    print(f"Title:   {entry['title']}")
    print(f"Type:    {entry['entry_type']}")
    print(f"Tags:    {', '.join(entry.get('tags', [])) or '(none)'}")
    print(f"Created: {entry['created_at']}")
    print(f"Updated: {entry['updated_at']}")
    print("Fields:")
    for key, value in entry["fields"].items():
        if key.lower() in ("password", "pin", "combo") and not reveal_secrets:
            print(f"  {key}: {'*' * 8}  (use --reveal to show)")
        else:
            print(f"  {key}: {value}")


def confirm(prompt_text: str) -> bool:
    answer = input(f"{prompt_text} [y/N]: ").strip().lower()
    return answer in ("y", "yes")
