import unittest
from faker import Faker
from off_chain.configuration.database import Database

class TestLogin(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.fake = Faker()
        self.test_users = [] # Keep track of users created for login tests

        # Create a user for successful login tests
        self.valid_username = self.fake.user_name()
        self.valid_password = self.fake.password(
            length=12, special_chars=True, digits=True,
            upper_case=True, lower_case=True)
        totp_secret = self.fake.sha256()
        self.test_users.append(self.valid_username)

        self.db.execute_query("""
            INSERT OR IGNORE INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?)
            """, (self.valid_username, self.valid_password, totp_secret))

    def test_login_successo(self):
        # Attempt login with correct credentials
        # In a real app, this would call a login function.
        # Here, we simulate by checking DB.
        result = self.db.fetch_one("""
            SELECT COUNT(*) FROM Credenziali WHERE Username = ? AND Password = ?
            """, (self.valid_username, self.valid_password))
        self.assertEqual(result, 1, "Login fallito con credenziali corrette.")

    def test_login_fallito_password_errata(self):
        wrong_password = self.fake.password(length=10)
        # Attempt login with incorrect password
        result = self.db.fetch_one("""
            SELECT COUNT(*) FROM Credenziali WHERE Username = ? AND Password = ?
            """, (self.valid_username, wrong_password))
        self.assertEqual(result, 0,
            "Login riuscito con password sbagliata, dovrebbe fallire.")

    def test_login_fallito_utente_inesistente(self):
        non_existent_username = self.fake.user_name()
        password = self.fake.password()
        # Attempt login with a username that does not exist
        result = self.db.fetch_one("""
            SELECT COUNT(*) FROM Credenziali WHERE Username = ? AND Password = ?
            """, (non_existent_username, password))
        self.assertEqual(result, 0,
            "Login riuscito con utente inesistente, dovrebbe fallire.")

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
