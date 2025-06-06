# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace

import sqlite3
import os

class Database:
    _instance = None  # Singleton per la connessione al database
    _connection_initialized = False

    def __new__(cls):
        """Implementa il pattern Singleton per mantenere una singola connessione al database."""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the database connection if not already initialized."""
        if not self._connection_initialized:
            try:
                self.conn = sqlite3.connect("database.db", timeout=10)  # Connessione al database
                # Enable foreign key constraints
                self.conn.execute("PRAGMA foreign_keys = ON")
                self.cur = self.conn.cursor()  # Cursore
                self._connection_initialized = True
            except sqlite3.ProgrammingError as e:
                print(f"Cannot operate on a closed database: {e}")
                raise Exception(f"Cannot operate on a closed database: {e}")
            except sqlite3.DatabaseError as e:
                print(f"File is encrypted or is not a database: {e}")
                raise Exception(f"File is encrypted or is not a database: {e}")
            except Exception as e:
                print(f"Unexpected Error: {e}")
                raise Exception(f"Unexpected Error: {e}")

    def execute_query(self, query, params=()):
        """Esegue una query di modifica (INSERT, UPDATE, DELETE) con gestione errori."""
        if not hasattr(self, "conn") or self.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")
        
        try:
            print(f"Provo ad eseguire {query} con par {params}")
            self.cur.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print("Errore: Violazione di vincolo di unicità.")
            if "UNIQUE constraint failed" in str(e):
                raise Exception("Duplicate key violation")
            raise e
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"Database bloccato (timeout raggiunto?): {e}")
            else:
                print(f"Errore SQL: {e}")
            raise e
        except sqlite3.Error as e:
            print(f"Errore generico nel database: {e}")
            raise e

    def fetch_results(cls, query, params=()):
        """Esegue una query di selezione e restituisce i risultati."""
        if not hasattr(cls, "conn") or cls.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")
        
        try:
            cls._instance.cur.execute(query, params)
            return cls._instance.cur.fetchall()
        
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"Database bloccato (timeout raggiunto?): {e}")
            else:
                print(f"Errore SQL: {e}")
        except sqlite3.Error as e:
            print(f"Errore nella query: {e}")
            return None
        
    def fetch_one(self, query, params=()):
        """Execute a query and return the first column of the first row."""
        if not hasattr(self, "conn") or self.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")
        
        try:
            print(f"Executing query: {query} with params {params}")
            self.cur.execute(query, params)
            result = self.cur.fetchone()
            if result is None:
                return None
            return result[0]  # Return the first column
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"Database bloccato (timeout raggiunto?): {e}")
            else:
                print(f"Errore SQL: {e}")
            raise e
        except sqlite3.Error as e:
            print(f"Errore nella query: {e}")
            raise e

    def execute_transaction(self, queries):
        """
        Esegue più query SQL all'interno di una singola transazione.

        Parameters:
        - queries: Lista di tuple contenenti (query, params).
        """
        if not hasattr(self, "conn") or self.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")

        try:
            self.cur.execute("BEGIN TRANSACTION;")

            for query, params in queries:
                print(f"BackEnd: execute_transaction: Info executing query: {query} with params: {params}")
                self.cur.execute(query, params)

            self.conn.commit()  # Commit di tutte le modifiche
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"Database bloccato (timeout raggiunto?): {e}")
                self.conn.rollback()  # Rollback in caso di errore
                raise Exception(f"Transaction error: {e}")
            else:
                print(f"Errore SQL: {e}")
        except Exception as e:
            self.conn.rollback()  # Rollback in caso di errore
            raise Exception(f"Transaction error: {e}")

    def close(self):
        """Close the database connection safely."""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
                self._connection_initialized = False
                Database._instance = None  # Reset the Singleton
                print("BackEnd: Closing database .....")
            except Exception as e:
                print(f"Error closing database connection: {e}")

    # Alias for close() for backward compatibility
    close_connection = close

    def __del__(self):
        """Ensure safe connection closure when the instance is destroyed."""
        self.close()




class DatabaseMigrations:
    # Variable of the class to track if the migrations were executed
    _migrations_executed = False
    
    @staticmethod
    def run_migrations():
        # Tables must be dropped in reverse order of dependencies
        TABLE_DELETION_QUERIES = [
            'DROP TABLE IF EXISTS Richiesta',  # Depends on Azienda
            'DROP TABLE IF EXISTS Magazzino',  # Depends on Azienda and Operazione
            'DROP TABLE IF EXISTS ComposizioneLotto',  # Depends on Operazione
            'DROP TABLE IF EXISTS Azioni_compensative',  # Depends on Azienda
            'DROP TABLE IF EXISTS Certificato',  # Depends on Azienda
            'DROP TABLE IF EXISTS Operazione',  # Depends on Azienda and Prodotto
            'DROP TABLE IF EXISTS Prodotto',   # No dependencies
            'DROP TABLE IF EXISTS Soglie',     # No dependencies
            'DROP TABLE IF EXISTS Azienda',    # Depends on Credenziali
            'DROP TABLE IF EXISTS Credenziali', # No dependencies
            'DROP TABLE IF EXISTS RichiestaToken'
        ]

        TABLE_CREATION_QUERIES = [
            '''
            CREATE TABLE  Credenziali (
                Id_credenziali INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL,
                Address TEXT NOT NULL              
            )
            ''',
            '''
            CREATE TABLE  Soglie (
                Operazione TEXT NOT NULL,
                Prodotto INTEGER NOT NULL,
                Soglia_Massima INTEGER NOT NULL,
                firma TEXT NOT NULL,
                PRIMARY KEY (Operazione, Prodotto)
            )
            ''',
            '''
            CREATE TABLE  Azienda (
                Id_azienda INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_credenziali INTEGER NOT NULL,
                Tipo TEXT CHECK(Tipo IN ('Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore')),
                Nome TEXT NOT NULL,
                Indirizzo TEXT NOT NULL,
                Co2_emessa INTEGER NOT NULL DEFAULT 0,
                Co2_compensata INTEGER NOT NULL DEFAULT 0,
                Token INTEGER NOT NULL DEFAULT 100 CHECK(Token >= 0),
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_credenziali) REFERENCES Credenziali(Id_credenziali) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE  Prodotto (
                Id_prodotto INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Stato INTEGER,
                Data_di_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE  Operazione (
                Id_operazione INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_azienda INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Id_lotto INTEGER UNIQUE NOT NULL,
                Data_operazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Consumo_CO2 INTEGER NOT NULL,
                quantita INTEGER NOT NULL CHECK(quantita > 0),
                Tipo TEXT CHECK(tipo IN ('produzione','cessione', 'trasporto', 'trasformazione', 'vendita')) NOT NULL,
                blockchain_registered BOOLEAN DEFAULT 0,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE ComposizioneLotto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_lotto_output INTEGER NOT NULL,
                id_lotto_input INTEGER NOT NULL,
                quantità_utilizzata INTEGER NOT NULL CHECK(quantità_utilizzata > 0),
                FOREIGN KEY (id_lotto_input) REFERENCES Operazione(Id_lotto)
            )
            ''',
            '''
            CREATE TABLE  Certificato (
                Id_certificato INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_lotto INTEGER NOT NULL,
                Descrizione TEXT,
                Id_azienda_certificatore INTEGER NOT NULL,
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_azienda_certificatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE  Azioni_compensative (
                Id_azione INTEGER PRIMARY KEY AUTOINCREMENT,
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Id_azienda INTEGER NOT NULL,
                Co2_compensata INTEGER NOT NULL,
                Nome_azione TEXT NOT NULL,
                blockchain_registered BOOLEAN DEFAULT 0,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE Magazzino (
                id_azienda TEXT NOT NULL,
                id_lotto TEXT NOT NULL,
                quantita INTEGER NOT NULL CHECK(quantita >= 0),
                PRIMARY KEY (id_azienda, id_lotto),
                FOREIGN KEY (id_azienda) REFERENCES Azienda(Id_azienda),
                FOREIGN KEY (id_lotto) REFERENCES Operazione(Id_lotto)
)
            ''',
            '''
            CREATE TABLE  Richiesta (
                Id_richiesta INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_richiedente INTEGER NOT NULL,
                Id_ricevente INTEGER NOT NULL,
                Id_trasportatore INTEGER NOT NULL,
                Id_prodotto INTEGER NOT NULL,
                Quantita INTEGER NOT NULL,
                Stato_ricevente TEXT CHECK(Stato_ricevente IN ('In attesa', 'Accettata', 'Rifiutata')),
                Stato_trasportatore TEXT CHECK(Stato_trasportatore IN ('In attesa', 'Accettata', 'Rifiutata')),
                Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (Id_richiedente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
                FOREIGN KEY (Id_ricevente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
                FOREIGN KEY (Id_trasportatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            ''',
             '''
            CREATE TABLE  RichiestaToken (
                Id_richiesta INTEGER PRIMARY KEY AUTOINCREMENT,
                Id_richiedente INTEGER NOT NULL,
                Id_ricevente INTEGER NOT NULL,
                Quantita INTEGER NOT NULL,
                Stato TEXT CHECK(Stato IN ('In attesa', 'Accettata', 'Rifiutata')),
                FOREIGN KEY (Id_richiedente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_ricevente) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            '''
        ]
        
        
        
        # Check if the migrations were already executed
        if DatabaseMigrations._migrations_executed:
            print("Migrations already executed. Skipping...")
            return

        try:
            db = Database()
            queries_with_params = [(query, ()) for query in TABLE_DELETION_QUERIES + TABLE_CREATION_QUERIES]
            db.execute_transaction(queries_with_params)

            # Check if the migrations were executed
            DatabaseMigrations._migrations_executed = True
            print("BackEnd: run_migrations: Migrations completed successfully.")

        except Exception as e:
            print(f"Error during database migration: {e}")
            raise Exception(f"Migration error: {e}")
        
        # Esegui le query di seed solo se le migrazioni sono appena state eseguite
        try:
            # Chiamata alla funzione per inserire i seed
            DatabaseMigrations.insert_seed_data(db)

            print("BackEnd: run_migrations: Seed dei dati iniziali completato.")
        except Exception as e:
            print(f"Errore durante l'inserimento dei dati di seed: {e}")

    @staticmethod
    def insert_seed_data(db):

        try:
            # Seed delle credenziali
            SEED_CREDENZIALI = [
                ("aaa", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45","0x70997970C51812dc3A010C7d01b50e0d17dc79C8"),
                ("ttt", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45","0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"),
                ("trasf", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45","0x90F79bf6EB2c4f870365E785982E1f101E93b906"),
                ("riv","3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45","0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65"),
                ("cert","3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45","0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc")
            ]

            for username, password , address in SEED_CREDENZIALI:
                db.execute_query("""
                    INSERT OR IGNORE INTO Credenziali (Username, Password, Address)
                    VALUES (?, ?, ?)
                """, (username, password, address))

            # Ottieni gli ID delle credenziali inserite
            credenziali = db.fetch_results("SELECT Id_credenziali, Username FROM Credenziali")

            # Seed aziende di esempio collegate agli ID credenziali
            SEED_AZIENDE = [
                ("aaa", "Azienda Agricola Verde", "Via Roma 1", "Agricola", 0, 0),
                ("ttt", "Trasporti EcoExpress", "Via Milano 2", "Trasportatore", 0, 0),
                ("trasf", "trasformazione BioCheck", "Via Torino 3", "Trasformatore", 0, 0),
                ("riv", "riv BioCheck", "Via Torino 3", "Rivenditore", 0, 0),
                ("cert", "cert BioCheck", "Via Torino 3", "Certificatore", 0, 0),
            ]

            for username, nome, indirizzo, tipo, co2_emessa, co2_compensata in SEED_AZIENDE:
                # Trova l'ID credenziale corrispondente
                id_cred = next((idc for idc, user in credenziali if user == username), None)
                if id_cred:
                    db.execute_query("""
                        INSERT OR IGNORE INTO Azienda (Id_credenziali, Tipo, Nome, Indirizzo, Co2_emessa, Co2_compensata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (id_cred, tipo, nome, indirizzo, co2_emessa, co2_compensata))

            # Seed dei prodotti
            SEED_PRODOTTI = [
                
                ("grano", 0),
                ("mais", 0),
                ("soia", 0),
                ("riso", 0),
                ("pomodoro", 0),
                ("latte", 0),
                ("uova", 0),
                ("patate", 0),
                ("mele", 0),
                ("olive", 0),
                ("pane", 1),
                ("farina di grano", 1),
                ("olio di oliva", 1),
                ("passata di pomodoro", 1),
                ("formaggio", 1),
                ("yogurt", 1),
                ("conserve di frutta", 1),
                ("patatine fritte", 1),
                ("pasta", 1),
                ("salsa di soia", 1)
               
            ]

            for nome, stato in SEED_PRODOTTI:
                db.execute_query("""
                    INSERT OR IGNORE INTO Prodotto (Nome, Stato)
                    VALUES (?, ?)
                """, (nome, stato))            


        


            seed_soglie =[
                ("produzione","1","52","b990173ff0b8d24e9d41dbaa64a39cda476c54cf50b465811c788ee36a211369"),
                ("produzione","2","54","2a747f613ae99ad4444a0160f4aa98c3f8e47416889b32ad30dd919c51e3f305"),
                ("produzione","3","56","a410a616aa71fbd65f9981e521e4a5f97578ac61c3a9b89eb51c0c13435e86ec"),
                ("produzione","4","58","9ec909c6ac8cf6f95a9006253e697613ae55cd966ba60267cb71785248138134"),
                ("produzione","5","60","cdcf457fce284d997a5812101c2f4dfdfc33b90341110f3df4fe2667293d0c4d"),
                ("produzione","6","62","ad8ac80719c34313b9dcf0b643e5cf2ce0d9bef6b98aa44992c05225ed0e09e5"),
                ("produzione","7","64","c614cb8ada42609480d56c072c90f8bf1f39e88e40c2d441eb44812bc9eb8c11"),
                ("produzione","8","66","986e12d057d676c28a8fe05fd8e8b5df74aecfea46f2c2112f068a6f681df314"),
                ("produzione","9","68","5c18d53c9d9b206979844e366aa7d1bda5c5ab5e69548bf3ac3048f079032e54"),
                ("produzione","10","70","248035e75c0398d1cac89a7eb7ab7f344abb53d9e034b1d537b5f9aac636057d"),
                ("trasporto","1","52","39de91dc8df31c6d647431e1038d30a188b3cb271cb32e2376162cc2aa0a1809"),
                ("trasporto","2","54","355b3f23021c4eb4011595e07c1ec29c9d05738c36fc633d1294cd88fde1cfca"),
                ("trasporto","3","56","65b95cb7ce4da34377b7aad2ee4d1cfc600deaf866f72facba1c1b6279ca7ad9"),
                ("trasporto","4","58","dc15c7c49ee55383c7c0340c98e86c93f0c6537af87354c29fe721bd494d6692"),
                ("trasporto","5","60","7af322c4bf9e5976d3fc44c9fc9d1fd94421bbdc0d73befd283002156b16375f"),
                ("trasporto","6","62","5bdf17b1e2146f65cbed559d0a29611e87126b4e1067535b63ef3ea8d50cdf1a"),
                ("trasporto","7","64","1e8e3f928f153d6e4fcc0253ece2a01553f8e80e4cfc1a0a29f10bec3116e5f5"),
                ("trasporto","8","66","45692e8a52aa2409f09be9d1bc94504ecef444303778c313ef014c47a3225050"),
                ("trasporto","9","68","cbed9088f381f850cdf829c16b18e35d582d1cef3c23573268e915b05ea2b5bd"),
                ("trasporto","10","70","5aed67eef2b34a458af52a5b007af93ffaae8065f6057ca5cd31b03f11901696"),
                ("trasporto","11","72","87d89d6c294db41145e52baa22ae3ffb977c149367a7184be04d71427a779fec"),
                ("trasporto","12","74","764ef09dd6c7feafd9b944f6cb5ab738b33226774e1cd97f424cd58601249b15"),
                ("trasporto","13","76","fa010ac84b068ec1155ca8737ee1d6b9182e775932e1ec64cad58721cd262a81"),
                ("trasporto","14","78","e2b349d3d520973a51073730f46538f9386e18cbf52cafecb94b7510d81b84fc"),
                ("trasporto","15","80","4403ca5143e1563dd71d2d70a3adc45bd6c095a6f9e616907544de16e8552177"),
                ("trasporto","16","82","c6df47df5a6e67e0e8d9937c3c395f52d832f00e598a24d785c4f4e0410b7119"),
                ("trasporto","17","84","c75ed9ddaa0c589c4f2e5a03b10c99111e3774fe9f1e8a6c7f0e0867171bb5aa"),
                ("trasporto","18","86","3213d26ce8188f954aba886436e79c1872354ed1a49f0cb985aac4558f8a773b"),
                ("trasporto","19","88","4abcb77f774461ff4cef614e0fd832ee1b0a6705636af27c45d3bffa207230d9"),
                ("trasporto","20","90","7f841a27c0258cb1731d4508d0c74bb0224c774c19e132f86b9268c90985026b"),
                ("trasformazione","11","72","1fe11420e35962e9cf7a4adc4b325228ad193ecb424faa43d75daaadcdc80f54"),
                ("trasformazione","12","74","7bc5b3288dc49521fbb2c21e5d49dd7e60b73338a8a6334a88770ba8066af323"),
                ("trasformazione","13","76","c53b2331c946a1bd043f126d90bfe5e7730f622c90153a825f63b8234cf42082"),
                ("trasformazione","14","78","42c5ba186883df7eacb8093f2d3a2bc91a353b746e73534e587e4220a251eba9"),
                ("trasformazione","15","80","370b0055c5812b87a61d780fe0c184461cbecfeecf1d3a11ccca78c1def123d9"),
                ("trasformazione","16","82","3af6bdba0283b293e82a9a2082d4c62a43284d8657199c7aaa71b6b832244395"),
                ("trasformazione","17","84","fd318a0adfecdeba3b27b5b5d904a73763ba10dad68cdeb2882e5a9aabb47878"),
                ("trasformazione","18","86","cddb520efc3eb5406febcbbaa70d9b90aba345a321bcbeef7cca5151adfc627e"),
                ("trasformazione","19","88","7f9603435d71c629687dd6ff334cf74f6d0a966200b11b995f508a98d57c7945"),
                ("trasformazione","20","90","f03e207254eda15a933be9973c79ca0b4d49e31357d92bdc9fdffcf3f3b2ab47"),
                ("vendita","11","72","d73684bae57623bc89c3695221607ddba3c6a1d751b2cd9499cc1feedea0ad32"),
                ("vendita","12","74","7c5cb17ba405a4b3d6975dbd82981275f5990bc5e3fc5cf2fe26a17a9d58dad3"),
                ("vendita","13","76","4a2a92a05059d3f89e47d32a4622e44e4927588271a89a5f834bc6279b9c62f2"),
                ("vendita","14","78","9d78e1cb14c7a89b53bd61bebc479e31162f2ae5097773d98f317b2b3ef192fe"),
                ("vendita","15","80","093db86d689a92e91c97f3937e5f0ec1c2ceb2c0c3ba44ac0401cb233da7e362"),
                ("vendita","16","82","df3a4af3231a16635e18513e7845560e4534ef3efcecd2084d914268739d772a"),
                ("vendita","17","84","84c249ec0294dbca4ffffd2e141bc76e3107a1d4633ccda41eebb24638d45078"),
                ("vendita","18","86","97d70f4de94244de310adaf68285824c4cbc69c9429f13ca0b9dc8294058b994"),
                ("vendita","19","88","3dba4636ba84007fb5fdf9fc16a5a0ad3b4894578d7b0d7ca436cf6d21434254"),
                ("vendita","20","90","0615151f3bca2a36ea87e4cd904c4825b2a766484e8a7e6f8a2ef555a0593ee3"),
            ]

            for op,prod, desc, firma in seed_soglie:
                db.execute_query("""
                    INSERT OR IGNORE INTO Soglie (Operazione, Prodotto, Soglia_Massima,firma)
                    VALUES (?, ?, ?,?)
                """, (op, prod,desc, firma))


            # Logger
            print("Seed dei dati iniziali completato.")

        except Exception as e:
            print(f"Errore durante l'inserimento dei dati di seed: {e}")

if __name__ == "__main__":
    # Esegui le migrazioni
    DatabaseMigrations.run_migrations()

