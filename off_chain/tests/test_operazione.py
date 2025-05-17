# pylint: disable= no-name-in-module
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
import unittest
import sqlite3
from faker import Faker
from off_chain.configuration.database import Database

class TestOperazioni(unittest.TestCase):

    def setUp(self):
        self.db = Database()
        self.fake = Faker()
        self.test_data_ids = {
            "credenziali": [],
            "aziende": [],
            "prodotti": [],
            "operazioni": [] # Using a unique identifier like Id_lotto for operations
        }

        # Create base data needed for most tests
        self._crea_dati_prerequisiti()

    def _crea_utente_azienda_prodotto(self):
        # Crea Credenziali
        username_azienda = self.fake.user_name() + "_azienda"
        password_azienda = self.fake.password(length=12)
        totp_secret_azienda = self.fake.sha256()

        # Insert credentials and get ID
        self.db.execute_query("""
            INSERT OR IGNORE INTO Credenziali (Username, Password, totp_secret)
            VALUES (?, ?, ?)
            """, (username_azienda, password_azienda, totp_secret_azienda))
        cred_id = self.db.fetch_one(
            "SELECT Id_credenziali FROM Credenziali WHERE Username = ?",
            (username_azienda,)
        )
        
        if not cred_id:
            self.fail(
                f"Failed to create/fetch credentials for {username_azienda}")
        self.test_data_ids["credenziali"].append(username_azienda)

        # Crea Azienda
        nome_azienda = self.fake.company() + " TestOp"
        tipo_azienda = self.fake.random_element(
            elements=("Agricola", "Trasportatore",
            "Trasformatore", "Rivenditore", "Certificatore"))
        indirizzo_azienda = self.fake.address()
        # Insert company and get ID
        self.db.execute_query("""
            INSERT INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo)
            VALUES (?, ?, ?, ?)
            """, (cred_id, tipo_azienda, nome_azienda, indirizzo_azienda))
        
        az_id = self.db.fetch_one(
            "SELECT Id_azienda FROM Azienda WHERE Nome = ?",
            (nome_azienda,)
        )
        if not az_id:
            self.fail(f"Failed to create/fetch azienda {nome_azienda}")
        
        self.test_data_ids["aziende"].append(nome_azienda)

        # Crea Prodotto
        nome_prodotto = self.fake.word() + "_prodotto_test"
        stato_prodotto = self.fake.random_int(min=0, max=2)
        
        # Insert product and get ID
        self.db.execute_query("""
            INSERT INTO Prodotto (Nome, Stato)
            VALUES (?, ?)
            """, (nome_prodotto, stato_prodotto))
        
        prod_id = self.db.fetch_one(
            "SELECT Id_prodotto FROM Prodotto WHERE Nome = ?",
            (nome_prodotto,)
        )
        if not prod_id:
            self.fail(f"Failed to create/fetch prodotto {nome_prodotto}")

        self.test_data_ids["prodotti"].append(nome_prodotto)
        return az_id, prod_id

    def _crea_dati_prerequisiti(self):
        self.az_id_test, self.prod_id_test = self._crea_utente_azienda_prodotto()

    def test_registrazione_operazione_successo(self):
        id_lotto = self.fake.random_number(digits=8, fix_len=True)
        consumo_co2 = round(self.fake.random_number(digits=3, fix_len=True) * self.fake.random_digit_not_null() / 10, 2)
        quantita = self.fake.random_int(min=1, max=1000)
        tipo_operazione = self.fake.random_element(
            elements=("produzione", "trasporto", "vendita"))
        self.test_data_ids["operazioni"].append(id_lotto)

        self.db.execute_query("""
            INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (self.az_id_test, self.prod_id_test, id_lotto,
            consumo_co2, quantita, tipo_operazione))

        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Operazione WHERE Id_lotto = ? AND Id_azienda = ? AND Id_prodotto = ?", 
            (id_lotto, self.az_id_test, self.prod_id_test))
        self.assertEqual(result, 1,
            "Operazione non registrata correttamente nel database.")

    def test_registrazione_operazione_azienda_inesistente(self):
        id_azienda_inesistente = self.fake.random_number(digits=10, fix_len=True)
        id_lotto = self.fake.random_number(digits=8, fix_len=True)
        consumo_co2 = round(
            self.fake.random_number(digits=3, fix_len=True) * self.fake.random_digit_not_null() / 10, 2)
        quantita = self.fake.random_int(min=1, max=1000)
        tipo_operazione = "produzione"
        # No need to add to test_data_ids['operazioni'] as it should fail

        with self.assertRaises(Exception,
            msg="Inserimento operazione con Id_azienda inesistente non ha sollevato eccezione."):
            self.db.execute_query("""
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_azienda_inesistente, self.prod_id_test,
            id_lotto, consumo_co2, quantita, tipo_operazione))
        
        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Operazione WHERE Id_lotto = ?", (id_lotto,))
        self.assertEqual(result, 0,
            "Operazione inserita erroneamente con Id_azienda inesistente.")

    def test_registrazione_operazione_prodotto_inesistente(self):
        """Test inserting an operation with a non-existent product ID."""
        id_lotto = self.fake.random_number(digits=8, fix_len=True)
        consumo_co2 = round(
            self.fake.random_number(digits=3, fix_len=True) * self.fake.random_digit_not_null() / 10, 2)
        quantita = self.fake.random_int(min=1, max=1000)
        tipo_operazione = "trasporto"

        # Attempt to insert with a non-existent product ID (very large number)
        id_prodotto_inesistente = 999999999
        
        try:
            self.db.execute_query("""
                INSERT INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.az_id_test, id_prodotto_inesistente,
            id_lotto, consumo_co2, quantita, tipo_operazione))
            self.fail(
                "Should have raised an IntegrityError for non-existent product ID")
        except sqlite3.IntegrityError:
            pass

        # Verify the operation wasn't inserted
        result = self.db.fetch_one(
            "SELECT COUNT(*) FROM Operazione WHERE Id_lotto = ?", (id_lotto,))
        self.assertEqual(result, 0,
        "Operation should not have been inserted with invalid product ID")

    def tearDown(self):
        # Delete operations first due to potential foreign key constraints
        if self.test_data_ids["operazioni"]:
            op_placeholders = ', '.join(
                ['?'] * len(self.test_data_ids["operazioni"]))
            self.db.execute_query(
                f"DELETE FROM Operazione WHERE Id_lotto IN ({op_placeholders})",
                tuple(self.test_data_ids["operazioni"]))

        # Delete prodotti
        if self.test_data_ids["prodotti"]:
            prod_placeholders = ', '.join(
                ['?'] * len(self.test_data_ids["prodotti"]))
            self.db.execute_query(
                f"DELETE FROM Prodotto WHERE Nome IN ({prod_placeholders})",
                tuple(self.test_data_ids["prodotti"]))

        if self.test_data_ids["aziende"]:
            az_placeholders = ', '.join(
                ['?'] * len(self.test_data_ids["aziende"]))
            self.db.execute_query(
                f"DELETE FROM Azienda WHERE Nome IN ({az_placeholders})",
                tuple(self.test_data_ids["aziende"]))

        if self.test_data_ids["credenziali"]:
            cred_placeholders = ', '.join(
                ['?'] * len(self.test_data_ids["credenziali"]))
            self.db.execute_query(
                f"DELETE FROM Credenziali WHERE Username IN ({cred_placeholders})",
                    tuple(self.test_data_ids["credenziali"]))
        
        self.db.close()

if __name__ == '__main__':
    unittest.main()
