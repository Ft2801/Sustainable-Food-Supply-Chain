# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
import unittest
from faker import Faker
from off_chain.configuration.database import Database

class TestRegistrazione(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.fake = Faker()
        self.test_users = [] # Keep track of users created during tests

    def _create_fake_user(self):
        username = self.fake.user_name()
        password = self.fake.password(length=12, special_chars=True,
            digits=True, upper_case=True, lower_case=True)
        totp_secret = self.fake.sha256()
        return username, password, totp_secret

    def test_registrazione_successo(self):
        username, password, totp_secret = self._create_fake_user()
        self.test_users.append(username)

        # Attempt registration
        self.db.execute_query("""
            INSERT INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?)
        """, (username, password, totp_secret))

        # Verify registration
        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Credenziali WHERE Username = ?", (username,))
        self.assertEqual(result, 1,
        f"Registrazione fallita per l'utente {username}.")

    def test_registrazione_username_duplicato(self):
        username, password, totp_secret = self._create_fake_user()
        self.test_users.append(username) # Add to cleanup list

        # First registration (should succeed)
        self.db.execute_query("""
            INSERT INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?)
        """, (username, password, totp_secret))

        # Attempt to register the same username again
        with self.assertRaises(Exception,
        msg="La registrazione con username duplicato non ha sollevato un'eccezione."):
            self.db.execute_query("""
                INSERT INTO Credenziali (Username, Password, totp_secret)
                VALUES (?, ?, ?)
            """, (username, "another_password", "another_secret"))

        # Verify only one user with that username exists
        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Credenziali WHERE Username = ?",
            (username,))
        self.assertEqual(result, 1,
            "Trovato più di un utente con lo stesso username dopo tentativo di registrazione duplicata.")

    def test_registrazione_password_debole(self):
        username = self.fake.user_name()
        password_debole = "123"
        totp_secret = self.fake.sha256()
        self.test_users.append(username)

        print(f"INFO: Test per password debole ({password_debole}) per l'utente {username} è concettuale e presume validazione a livello applicativo.")
        pass # Placeholder for actual test if application logic is available

    def tearDown(self):
        # Clean up all users created during the tests in this class
        if self.test_users:
            placeholders = ', '.join(['?'] * len(self.test_users))
            self.db.execute_query(
                f"DELETE FROM Credenziali WHERE Username IN ({placeholders})",
                tuple(self.test_users))
        self.db.close()

if __name__ == '__main__':
    unittest.main()