import os
import tempfile
import unittest
import auth
import crypto_engine
import password_gen
import storage
import vault_manager


class TestCryptoEngine(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        salt = crypto_engine.generate_salt()
        plaintext = b"top secret data"
        ciphertext = crypto_engine.encrypt(plaintext, "correct-password", salt)
        result = crypto_engine.decrypt(ciphertext, "correct-password", salt)
        self.assertEqual(plaintext, result)

    def test_wrong_password_fails(self):
        salt = crypto_engine.generate_salt()
        ciphertext = crypto_engine.encrypt(b"data", "right-password", salt)
        with self.assertRaises(crypto_engine.DecryptionError):
            crypto_engine.decrypt(ciphertext, "wrong-password", salt)

    def test_tampered_ciphertext_fails(self):
        salt = crypto_engine.generate_salt()
        ciphertext = bytearray(crypto_engine.encrypt(b"data", "pw", salt))
        ciphertext[-1] ^= 0xFF  # flip bits to corrupt
        with self.assertRaises(crypto_engine.DecryptionError):
            crypto_engine.decrypt(bytes(ciphertext), "pw", salt)


class TestAuth(unittest.TestCase):
    def test_correct_password_verifies(self):
        record = auth.hash_master_password("hunter2")
        self.assertTrue(auth.verify_master_password("hunter2", record))

    def test_incorrect_password_fails(self):
        record = auth.hash_master_password("hunter2")
        self.assertFalse(auth.verify_master_password("wrongpass", record))


class TestVaultManager(unittest.TestCase):
    def setUp(self):
        self.vault = vault_manager.new_empty_vault_data()

    def test_add_and_find_entry(self):
        entry = vault_manager.add_entry(
            self.vault, "Test Site", "password", {"username": "u", "password": "p"}
        )
        found = vault_manager.find_entry(self.vault, entry["id"])
        self.assertEqual(found["title"], "Test Site")

    def test_invalid_entry_type_rejected(self):
        with self.assertRaises(ValueError):
            vault_manager.add_entry(self.vault, "Bad", "not_a_real_type", {})

    def test_search_by_title(self):
        vault_manager.add_entry(self.vault, "Gmail Account", "password", {})
        vault_manager.add_entry(self.vault, "Bike Lock", "lock_combo", {})
        results = vault_manager.search_entries(self.vault, "gmail")
        self.assertEqual(len(results), 1)

    def test_delete_entry(self):
        entry = vault_manager.add_entry(self.vault, "Temp", "note", {"body": "x"})
        vault_manager.delete_entry(self.vault, entry["id"])
        with self.assertRaises(vault_manager.EntryNotFoundError):
            vault_manager.find_entry(self.vault, entry["id"])


class TestPasswordGen(unittest.TestCase):
    def test_generated_length(self):
        pw = password_gen.generate_password(length=20)
        self.assertEqual(len(pw), 20)

    def test_no_ambiguous_chars_by_default(self):
        for _ in range(20):
            pw = password_gen.generate_password(length=24)
            for ch in password_gen.AMBIGUOUS_CHARS:
                self.assertNotIn(ch, pw)


class TestStorage(unittest.TestCase):
    def test_atomic_write_and_read(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_vault.dat")
            salt = crypto_engine.generate_salt()
            auth_record = auth.hash_master_password("pw123456")
            ciphertext = crypto_engine.encrypt(b"{}", "pw123456", salt)

            storage.create_new_vault_file(path, salt, auth_record, ciphertext)
            self.assertTrue(storage.vault_exists(path))

            loaded = storage.load_vault_file(path)
            self.assertEqual(loaded["meta"]["salt"], salt.hex())


if __name__ == "__main__":
    unittest.main()
