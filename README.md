# Offline Secure Password & Note Vault

A simple command-line password and notes vault that lets you store passwords, lock combinations, and private notes in **one encrypted local file**.

The main idea of this project is pretty simple: everything stays on your computer. There is **no cloud storage, no server, and no network connection**.

The vault is protected by one master password. The master password itself is never stored.

---

## 1. Requirements

You need:

* Python 3.9 or newer
* pip

You can check your Python version with:

```bash
python3 --version
```

---

## 2. Setting It Up

First, clone the repository and move into the project folder:

```bash
git clone <this-repo-url>
cd vault-cli
```

I recommend using a virtual environment, although it isn't required:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Then install the required packages:

```bash
pip install -r requirements.txt
```

The main dependency is `cryptography`, which is used for the encryption and decryption.

`pyperclip` is optional and is only needed if you want to use the clipboard feature. If it doesn't install properly on your system, the vault itself will still work.

---

# 3. How to Use It

Everything is controlled through `app.py`.

Whenever you use a command that accesses your vault, you'll be asked for your master password. The password is hidden while you're typing it.

### Create a vault

```bash
python3 app.py init
```

You'll be asked to create a master password.

The password must be at least 8 characters long, and you'll need to enter it twice for confirmation.

This creates:

```text
vault.dat
```

in the current directory.

**Important:** There is no password recovery. If you forget your master password, the vault cannot be decrypted.

---

## Add an Entry

You can store different types of information in the vault.

### Password

```bash
python3 app.py add --title "Gmail" --type password --username "you@gmail.com" --secret
```

### Lock combination

```bash
python3 app.py add --title "Bike lock" --type lock_combo --secret
```

### Private note

```bash
python3 app.py add --title "Journal - Sept 27" --type note --secret
```

The `--secret` option asks you for the sensitive information separately instead of putting it directly in the command.

This is useful because anything typed directly into a command can end up in your shell history.

You can also add tags:

```bash
python3 app.py add --title "Work laptop" --type password --secret --tags "work,laptop"
```

---

## List Your Entries

To see everything:

```bash
python3 app.py list
```

Only show passwords:

```bash
python3 app.py list --type password
```

Filter by a tag:

```bash
python3 app.py list --tag work
```

---

## View an Entry

```bash
python3 app.py show <entry_id>
```

By default, the secret is hidden.

To actually show it:

```bash
python3 app.py show <entry_id> --reveal
```

You can also copy it to your clipboard:

```bash
python3 app.py show <entry_id> --reveal --copy
```

You don't have to type the entire entry ID. The first few characters are enough as long as they uniquely identify the entry.

---

## Search

You can search your vault using:

```bash
python3 app.py search gmail
```

---

## Edit an Entry

For example:

```bash
python3 app.py edit <entry_id> --title "New Title" --tag "personal,important"
```

---

## Delete an Entry

```bash
python3 app.py delete <entry_id>
```

The command normally asks for confirmation.

If you want to skip the confirmation:

```bash
python3 app.py delete <entry_id> --yes
```

---

# 4. Password Generator

The project also has a password generator that can be used even if you haven't created a vault yet.

```bash
python3 app.py genpass
```

You can change the length:

```bash
python3 app.py genpass --length 24
```

Generate a password without symbols:

```bash
python3 app.py genpass --no-symbols
```

Or copy the generated password directly:

```bash
python3 app.py genpass --copy
```

The generator uses Python's `secrets` module instead of normal random numbers.

---

# 5. Using a Different Vault Location

Normally, the vault is saved as:

```text
./vault.dat
```

You can choose another location using `--path`.

For example:

```bash
python3 app.py --path /path/to/my_vault.dat init
```

And later:

```bash
python3 app.py --path /path/to/my_vault.dat list
```

This can be useful if you want to keep the vault on another drive or a USB drive.

---

# 6. Running the Tests

The project includes unit tests for the main functionality.

Run them with:

```bash
python3 -m unittest tests.py -v
```

The tests cover things like:

* Encryption and decryption
* Wrong master passwords
* Detecting tampered vault files
* Authentication
* Adding, editing and deleting entries
* Password generation

---

# 7. How the Security Works

I wanted the project to do more than just hide passwords in a normal text file, so the vault uses encryption and password-based key derivation.

### Authentication

The master password is not saved anywhere.

Instead, the project uses:

* PBKDF2-HMAC-SHA256
* A unique salt
* 200,000 iterations

The stored information is used to verify whether the entered master password is correct.

### Encryption

The vault contents are encrypted using `Fernet`.

The encryption key is derived from the master password using PBKDF2 with a separate salt.

This means the actual passwords, notes and other secrets are stored encrypted inside `vault.dat`.

If someone modifies the encrypted vault file, Fernet's authentication detects the change and rejects the data.

### Password Generation

Passwords are generated using Python's `secrets` module, which is designed for security-sensitive random values.

### Atomic Saving

The vault doesn't simply overwrite the existing file while saving.

Instead, it writes the new data to a temporary file first and then replaces the old vault file.

This helps prevent the existing vault from being corrupted if something goes wrong during a save.

---

# 8. Project Structure

```text
vault-cli/
├── app.py             # Main CLI program
├── auth.py            # Master password authentication
├── crypto_engine.py   # Encryption and decryption
├── vault_manager.py   # Adding, editing and deleting entries
├── password_gen.py    # Password generator
├── storage.py         # Reading and saving the vault
├── ui_helpers.py      # CLI input, display and clipboard features
├── tests.py           # Unit tests
├── requirements.txt   # Python dependencies
├── .gitignore
├── statement.md       # Project problem statement
└── README.md
```

---

# 9. Security Notes

A few important things to keep in mind:

* The master password is never stored.
* There is no password recovery or backdoor.
* Forgetting the master password means the vault cannot be decrypted.
* The vault is encrypted while stored on disk.
* `vault.dat` should not be uploaded to a public GitHub repository.
* The vault is excluded through `.gitignore` by default.
* You should still make backups of your vault file somewhere safe.

Also, this project is meant as a personal/educational security project. It doesn't claim to replace professionally audited password managers.

---

## Why I Made This

I made this project to understand how things like **encryption, password authentication, key derivation, secure random generation, file storage, and command-line interfaces** actually work together in a real program.

Instead of just making a program that stores passwords in a text file, I wanted to build something where the stored data is actually protected even if someone gets access to the vault file.

The whole project works locally, so there is no server or cloud system involved.
