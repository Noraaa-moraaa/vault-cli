# Offline Secure Password & Note Vault

A command-line tool that lets you store passwords, lock combinations, and
private notes in a single **encrypted local file**. Nothing ever leaves
your machine — there is no cloud sync, no server, and no network call.
You unlock the vault each time with one master password, which is never
itself stored anywhere.


---

## 1. Requirements

- Python 3.9 or newer
- pip (Python's package installer)

Check your Python version:

```bash
python3 --version
```

## 2. Environment Setup

1. Clone or download this repository, then move into it:

   ```bash
   git clone <this-repo-url>
   cd vault-cli
   ```

2. (Recommended, not required) Create a virtual environment so the
   dependencies don't mix with anything else on your system:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # on Windows: .venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   - `cryptography` is required — it powers all encryption/decryption.
   - `pyperclip` is optional — it only enables the `--copy` clipboard
     feature. If it fails to install (rare, some Linux setups need
     `xclip`/`xsel`), the vault still works fine without it; clipboard
     commands will just print a note saying clipboard isn't available.

## 3. Quick Start

All commands are run through `app.py`. Every command that touches vault
data will prompt you for your master password (input is hidden as you
type).

### Create a new vault

```bash
python3 app.py init
```

You'll be asked to set a master password (minimum 8 characters, and you
must type it twice to confirm). This creates a file called `vault.dat`
in the current directory. **There is no password recovery — if you
forget your master password, the vault cannot be decrypted.**

### Add an entry

```bash
# A password entry
python3 app.py add --title "Gmail" --type password --username "you@gmail.com" --secret

# A lock combination
python3 app.py add --title "Bike lock" --type lock_combo --secret

# A private note
python3 app.py add --title "Journal - Sept 27" --type note --secret
```

The `--secret` flag makes it prompt you separately for the sensitive
value (password / combination / note body) so it's never typed directly
on the command line (which would leak into your shell history).

You can tag entries for easy filtering later:

```bash
python3 app.py add --title "Work laptop" --type password --secret --tags "work,laptop"
```

### List entries

```bash
python3 app.py list
python3 app.py list --type password
python3 app.py list --tag work
```

### View a single entry

```bash
python3 app.py show <entry_id>
python3 app.py show <entry_id> --reveal          # show the actual secret
python3 app.py show <entry_id> --reveal --copy   # also copy it to clipboard
```

You only need to type the first few characters of the entry ID shown in
`list` — it matches by prefix.

### Search

```bash
python3 app.py search gmail
```

### Edit an entry

```bash
python3 app.py edit <entry_id> --title "New Title" --tag "personal,important"
```

### Delete an entry

```bash
python3 app.py delete <entry_id>
python3 app.py delete <entry_id> --yes    # skip the confirmation prompt
```

### Generate a strong password

```bash
python3 app.py genpass
python3 app.py genpass --length 24
python3 app.py genpass --no-symbols
python3 app.py genpass --copy             # copies straight to clipboard
```

This works even without an existing vault — it's a standalone utility.

### Using a vault file somewhere else

By default the vault lives at `./vault.dat`. Use `--path` to point at a
different location (e.g. a synced folder, a USB drive):

```bash
python3 app.py --path /path/to/my_vault.dat init
python3 app.py --path /path/to/my_vault.dat list
```

## 4. Running the Tests

```bash
python3 -m unittest tests.py -v
```

This runs unit tests covering encryption/decryption correctness, wrong
password rejection, tamper detection, authentication, vault CRUD
operations, and password generation.

## 5. How It Works (Feature Overview)

- **Authentication** (`auth.py`) — your master password is verified
  against a PBKDF2-HMAC-SHA256 hash + unique salt (200,000 iterations).
  The password itself is never written to disk.
- **Encryption** (`crypto_engine.py`) — a separate key is derived from
  your master password (also via PBKDF2, with its own salt) and used
  with `Fernet` (AES-128 + HMAC) to encrypt the entire vault contents.
  Any tampering with the encrypted file is detected and rejected on
  decryption.
- **Entry management** (`vault_manager.py`) — add, list, search, edit,
  and delete entries of three types: `password`, `lock_combo`, `note`.
- **Password generation** (`password_gen.py`) — cryptographically secure
  random passwords via Python's `secrets` module, with a strength
  label.
- **Storage** (`storage.py`) — the vault is written atomically (write to
  a temp file, then rename over the original) so a crash mid-save can
  never corrupt your existing vault.
- **CLI/UI helpers** (`ui_helpers.py`) — masked password input, secret
  masking on display (unless `--reveal` is passed), and optional
  clipboard copy.

## 6. Project Structure

```
vault-cli/
├── app.py             # CLI entry point (argparse commands)
├── auth.py             # Master password hashing & verification
├── crypto_engine.py    # Symmetric encryption/decryption (Fernet + PBKDF2)
├── vault_manager.py    # In-memory entry CRUD logic
├── password_gen.py     # Secure random password generator
├── storage.py           # Atomic on-disk read/write of the vault file
├── ui_helpers.py        # Masked input, table printing, clipboard
├── tests.py             # Unit tests
├── requirements.txt
├── .gitignore
├── statement.md          # Problem statement / scope / features
└── README.md             # You are here
```

## 7. Security Notes

- Your master password is **never** stored or logged, in any form.
- Losing the master password means the vault **cannot** be recovered —
  this is by design (there is no backdoor).
- The vault file (`vault.dat`) is encrypted at rest, but it is still a
  regular file — back it up like you would any important file, and
  don't commit it to a public git repository (it's excluded via
  `.gitignore` by default).
