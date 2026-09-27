import argparse
import sys
import auth
import crypto_engine
import password_gen
import storage
import ui_helpers
import vault_manager

VAULT_PATH = "vault.dat"

def open_vault(path: str) -> tuple:
    try:
        record = storage.load_vault_file(path)
    except storage.VaultNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    master_password = ui_helpers.prompt_master_password()

    if not auth.verify_master_password(master_password, record["meta"]["auth"]):
        print("Error: incorrect master password.", file=sys.stderr)
        sys.exit(1)

    salt = bytes.fromhex(record["meta"]["salt"])
    ciphertext = record["ciphertext"].encode("utf-8")

    try:
        plaintext = crypto_engine.decrypt(ciphertext, master_password, salt)
    except crypto_engine.DecryptionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    vault_data = vault_manager.load_decrypted(plaintext)
    return vault_data, record, master_password


def save_vault(path: str, vault_data: dict, record: dict, master_password: str) -> None:
    salt = bytes.fromhex(record["meta"]["salt"])
    plaintext = vault_manager.dump_for_encryption(vault_data)
    ciphertext = crypto_engine.encrypt(plaintext, master_password, salt)
    storage.save_ciphertext(path, record, ciphertext)

def cmd_init(args):
    if storage.vault_exists(args.path):
        print(f"A vault already exists at '{args.path}'. Delete it manually to start over.")
        sys.exit(1)

    print("Creating a new vault.")
    master_password = ui_helpers.prompt_master_password(confirm=True)
    if len(master_password) < 8:
        print("Error: master password must be at least 8 characters.", file=sys.stderr)
        sys.exit(1)

    enc_salt = crypto_engine.generate_salt()
    auth_record = auth.hash_master_password(master_password)

    empty_vault = vault_manager.new_empty_vault_data()
    plaintext = vault_manager.dump_for_encryption(empty_vault)
    ciphertext = crypto_engine.encrypt(plaintext, master_password, enc_salt)

    storage.create_new_vault_file(args.path, enc_salt, auth_record, ciphertext)
    print(f"Vault created at '{args.path}'. Keep your master password safe -- it cannot be recovered.")


def cmd_add(args):
    vault_data, record, master_password = open_vault(args.path)

    fields = {}
    if args.username:
        fields["username"] = args.username
    if args.url:
        fields["url"] = args.url

    if args.secret:
        secret_value = _prompt_secret(args.type)
        secret_key = {"password": "password", "lock_combo": "combo", "note": "body"}[args.type]
        fields[secret_key] = secret_value

    tags = args.tags.split(",") if args.tags else []
    entry = vault_manager.add_entry(vault_data, args.title, args.type, fields, tags)
    save_vault(args.path, vault_data, record, master_password)
    print(f"Added entry '{entry['title']}' (id: {entry['id'][:8]}).")


def _prompt_secret(entry_type: str) -> str:
    import getpass as _getpass
    label = {"password": "Password", "lock_combo": "Combination", "note": "Note body"}[entry_type]
    if entry_type == "note":
        return input(f"{label}: ")
    return _getpass.getpass(f"{label} (input hidden): ")


def cmd_list(args):
    vault_data, _, _ = open_vault(args.path)
    entries = vault_manager.list_entries(vault_data, entry_type=args.type, tag=args.tag)
    ui_helpers.print_entry_table(entries)


def cmd_show(args):
    vault_data, _, _ = open_vault(args.path)
    try:
        entry = vault_manager.find_entry(vault_data, args.entry_id)
    except vault_manager.EntryNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    ui_helpers.print_entry_detail(entry, reveal_secrets=args.reveal)

    if args.copy:
        secret_key = {"password": "password", "lock_combo": "combo", "note": "body"}.get(entry["entry_type"])
        secret_value = entry["fields"].get(secret_key, "")
        if ui_helpers.copy_to_clipboard(secret_value):
            print("(copied secret to clipboard)")
        else:
            print("(clipboard copy unavailable -- install 'pyperclip' to enable this)")


def cmd_search(args):
    vault_data, _, _ = open_vault(args.path)
    results = vault_manager.search_entries(vault_data, args.query)
    ui_helpers.print_entry_table(results)


def cmd_edit(args):
    vault_data, record, master_password = open_vault(args.path)
    updates = {}
    if args.title:
        updates["title"] = args.title
    if args.tag:
        updates["tags"] = args.tag.split(",")

    try:
        entry = vault_manager.update_entry(vault_data, args.entry_id, **updates)
    except vault_manager.EntryNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    save_vault(args.path, vault_data, record, master_password)
    print(f"Updated entry '{entry['title']}' (id: {entry['id'][:8]}).")


def cmd_delete(args):
    vault_data, record, master_password = open_vault(args.path)
    try:
        entry = vault_manager.find_entry(vault_data, args.entry_id)
    except vault_manager.EntryNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.yes and not ui_helpers.confirm(f"Delete '{entry['title']}'?"):
        print("Cancelled.")
        return

    vault_manager.delete_entry(vault_data, entry["id"])
    save_vault(args.path, vault_data, record, master_password)
    print(f"Deleted entry '{entry['title']}'.")


def cmd_genpass(args):
    pw = password_gen.generate_password(
        length=args.length,
        use_symbols=not args.no_symbols,
    )
    strength = password_gen.password_strength_label(pw)
    print(pw)
    print(f"(strength: {strength})", file=sys.stderr)
    if args.copy and ui_helpers.copy_to_clipboard(pw):
        print("(copied to clipboard)", file=sys.stderr)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vault",
        description="Offline Secure Password & Note Vault (CLI)",
    )
    parser.add_argument("--path", default=VAULT_PATH, help=f"Path to vault file (default: {VAULT_PATH})")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create a new vault").set_defaults(func=cmd_init)

    p_add = sub.add_parser("add", help="Add a new entry")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--type", required=True, choices=vault_manager.ENTRY_TYPES)
    p_add.add_argument("--username", default=None, help="Username (for password entries)")
    p_add.add_argument("--url", default=None, help="Associated URL (for password entries)")
    p_add.add_argument("--tags", default=None, help="Comma-separated tags")
    p_add.add_argument("--secret", action="store_true", help="Prompt for the secret value (password/combo/note body)")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="List entries")
    p_list.add_argument("--type", default=None, choices=vault_manager.ENTRY_TYPES)
    p_list.add_argument("--tag", default=None)
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show a single entry")
    p_show.add_argument("entry_id")
    p_show.add_argument("--reveal", action="store_true", help="Reveal secret fields in plain text")
    p_show.add_argument("--copy", action="store_true", help="Copy the secret field to clipboard")
    p_show.set_defaults(func=cmd_show)

    p_search = sub.add_parser("search", help="Search entries by title/tag")
    p_search.add_argument("query")
    p_search.set_defaults(func=cmd_search)

    p_edit = sub.add_parser("edit", help="Edit an entry's title/tags")
    p_edit.add_argument("entry_id")
    p_edit.add_argument("--title", default=None)
    p_edit.add_argument("--tag", default=None, help="Comma-separated tags (replaces existing)")
    p_edit.set_defaults(func=cmd_edit)

    p_delete = sub.add_parser("delete", help="Delete an entry")
    p_delete.add_argument("entry_id")
    p_delete.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    p_delete.set_defaults(func=cmd_delete)

    p_genpass = sub.add_parser("genpass", help="Generate a strong random password")
    p_genpass.add_argument("--length", type=int, default=16)
    p_genpass.add_argument("--no-symbols", action="store_true")
    p_genpass.add_argument("--copy", action="store_true", help="Copy generated password to clipboard")
    p_genpass.set_defaults(func=cmd_genpass)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
