# Problem Statement

## 1. Background

Most people have to remember and manage many passwords, PINs, lock combinations, and private notes in their daily life. This can include Wi-Fi passwords, locker combinations, banking PINs, and personal notes. Because it is difficult to remember everything, people may reuse weak passwords or store sensitive information in unsafe places such as normal notes apps, sticky notes, or unencrypted files.

Cloud-based password managers can help with this problem, but they require users to trust a third-party service with their sensitive information. They may also depend on an internet connection.

## 2. Problem

There is a need for a lightweight and fully offline way to store sensitive information that:

* Never sends the stored data over a network.
* Uses proper and industry-standard cryptography instead of simple data hiding or obfuscation.
* Is simple enough to use through a single command-line application without requiring a server or graphical interface.
* Protects the stored information if the vault file is stolen and also reduces the chance of corruption if a write operation is interrupted.

## 3. Scope

### In scope:

* Local encrypted storage for three types of entries: passwords, lock combinations, and free-text notes.
* Master-password-based authentication and key derivation.
* CRUD operations such as adding, listing, viewing, searching, editing, and deleting vault entries through CLI commands.
* A standalone secure password generator.
* Basic features such as masked terminal input, optional clipboard copying, tagging, and searching.

### Out of scope:

* Cloud synchronization or sharing the vault between multiple devices.
* Browser integration or autofill.
* Multiple users or shared vaults.
* Password recovery if the master password is lost. This is intentional because there is no recovery method or backdoor.
* A graphical user interface, since the project is designed as a CLI application.

## 4. Target Users

* Individuals who want to store their passwords and private information locally without depending on a third-party cloud service.
* Students and professionals who want to learn about practical uses of cryptography such as key derivation and authenticated encryption.
* People who want an offline vault that can be used without an internet connection or depending on an external company.

## 5. High-Level Features

| Feature                        | Description                                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Vault initialization           | Creates a new encrypted vault protected by a master password.                                                             |
| Master password authentication | Checks the master password before allowing access to the vault.                                                           |
| Add entries                    | Allows users to store passwords, lock combinations, or notes with optional tags.                                          |
| List / search entries          | Allows users to view entries and filter them by type or tag, or search using keywords.                                    |
| View entry                     | Displays a selected entry while keeping secret information hidden by default.                                             |
| Edit entry                     | Allows the user to change the title or tags of an entry.                                                                  |
| Delete entry                   | Removes an entry from the vault.                                                                                          |
| Password generator             | Generates random passwords using a secure random generator and gives a basic strength indication.                         |
| Clipboard copy                 | Allows a secret value to be copied to the clipboard without displaying it directly in the terminal, when supported.       |
| Atomic persistence             | Saves the vault in a way that helps prevent the existing file from being corrupted if the write operation is interrupted. |

## 6. Functional Modules (Rubric Mapping)

1. **Authentication** — `auth.py`: Handles master password hashing and verification.

2. **Data Encryption/Decryption** — `crypto_engine.py`: Handles key derivation and symmetric authenticated encryption of the vault data.

3. **Entry Management** — `vault_manager.py`: Handles the CRUD operations for vault entries, while `app.py` provides the CLI commands for the user.

## 7. Non-Functional Requirements

1. **Security** — Uses PBKDF2-HMAC-SHA256 with 200,000 iterations and separate salts for authentication and encryption key derivation. Fernet authenticated encryption is used to detect changes or tampering with the encrypted data.

2. **Reliability** — Uses atomic file writes in `storage.py` to reduce the chance of vault corruption if the program is interrupted while saving. The existing vault file is kept safe until the new data is successfully written.

3. **Usability** — Provides masked password and secret input, hides secret information by default when displaying entries, and provides optional clipboard copying. Users can also organize entries using tags and search for them using keywords.

4. **Performance** — Vault operations work in O(n) time because the entries are stored and searched in an in-memory JSON structure. This is suitable for a personal vault containing hundreds or even a few thousand entries without noticeable delay during normal use.
