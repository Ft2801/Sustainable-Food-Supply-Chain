# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace
from configuration.log_load_setting import logger
from configuration.database import Database


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
            'DROP TABLE IF EXISTS Credenziali' # No dependencies
        ]

        TABLE_CREATION_QUERIES = [
            '''
            CREATE TABLE  Credenziali (
                Id_credenziali INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL                
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
                Co2_emessa REAL NOT NULL DEFAULT 0,
                Co2_compensata REAL NOT NULL DEFAULT 0,
                Token INTEGER NOT NULL DEFAULT 100,
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
                Consumo_CO2 REAL NOT NULL,
                quantita REAL NOT NULL CHECK(quantita > 0),
                Tipo TEXT CHECK(tipo IN ('produzione', 'trasporto', 'trasformazione', 'vendita')) NOT NULL,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
                FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE ComposizioneLotto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_lotto_output INTEGER NOT NULL,
                id_lotto_input INTEGER NOT NULL,
                quantità_utilizzata REAL NOT NULL CHECK(quantità_utilizzata > 0),
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
                Co2_compensata REAL NOT NULL,
                Nome_azione TEXT NOT NULL,
                FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
            )
            ''',
            '''
            CREATE TABLE Magazzino (
                id_azienda TEXT NOT NULL,
                id_lotto TEXT NOT NULL,
                quantita REAL NOT NULL CHECK(quantita >= 0),
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
                Quantita REAL NOT NULL,
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
            logger.info("Migrations already executed. Skipping...")
            return

        try:
            db = Database()
            queries_with_params = [(query, ()) for query in TABLE_DELETION_QUERIES + TABLE_CREATION_QUERIES]
            db.execute_transaction(queries_with_params)

            # Check if the migrations were executed
            DatabaseMigrations._migrations_executed = True
            logger.info("BackEnd: run_migrations: Migrations completed successfully.")

        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            raise Exception(f"Migration error: {e}")
        
        # Esegui le query di seed solo se le migrazioni sono appena state eseguite
        try:
            # Chiamata alla funzione per inserire i seed
            DatabaseMigrations.insert_seed_data(db)

            logger.info("BackEnd: run_migrations: Seed dei dati iniziali completato.")
        except Exception as e:
            logger.error(f"Errore durante l'inserimento dei dati di seed: {e}")

    @staticmethod
    def insert_seed_data(db):

        try:
            # Seed delle credenziali
            SEED_CREDENZIALI = [
                ("aaa", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
                ("ttt", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
                ("trasf", "3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
                ("riv","3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45"),
                ("cert","3f0409ad2ac4570392adef46536c00e46c60d702d3822788319590de4c146a45")
            ]

            for username, password in SEED_CREDENZIALI:
                db.execute_query("""
                    INSERT OR IGNORE INTO Credenziali (Username, Password)
                    VALUES (?, ?)
                """, (username, password))

            # Ottieni gli ID delle credenziali inserite
            credenziali = db.fetch_results("SELECT Id_credenziali, Username FROM Credenziali")

            # Seed aziende di esempio collegate agli ID credenziali
            SEED_AZIENDE = [
                ("aaa", "Azienda Agricola Verde", "Via Roma 1", "Agricola", 10.5, 2.0),
                ("ttt", "Trasporti EcoExpress", "Via Milano 2", "Trasportatore", 30.0, 5.0),
                ("trasf", "Certificazioni BioCheck", "Via Torino 3", "Trasformatore", 5.0, 1.5),
                ("riv", "riv BioCheck", "Via Torino 3", "Rivenditore", 5.0, 1.5),
                ("cert", "cert BioCheck", "Via Torino 3", "Certificatore", 5.0, 1.5),
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

            


            # Operazioni di produzione delle materie prime
            operazioni = [
    # Produzione mele
                (1, 1, 1001, 50.0, 100.0, 'produzione'),
                # Produzione zucchero
                (1, 2, 1002, 25.0, 50.0, 'produzione'),
                # Trasformazione in succo
                (2, 1, 1010, 25.0, 50.0, 'trasporto'),

                (2, 2, 1020, 25.0, 50.0, 'trasporto'),

                (3, 3, 1100, 10.0, 100.0, 'trasformazione'),

                (2, 3, 1011, 25.0, 50.0, 'trasporto'),

                (4, 3, 2000, 1.0, 10.0, 'vendita'),

                
            ]

            for op in operazioni:
                db.execute_query("""
                    INSERT OR IGNORE INTO Operazione (Id_azienda, Id_prodotto, Id_lotto, Consumo_CO2, quantita, Tipo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, op)

            SEED_MAGAZZINO = [

                
                (1,1001, 100),
                (1,1002,50),
                (3,1010,200),
                (3,1020,100)
            ]

            for id_az, id_lot, qt in SEED_MAGAZZINO:
                db.execute_query("""
                    INSERT OR IGNORE INTO Magazzino (id_azienda, id_lotto, quantita)
                    VALUES (?, ?,?)
                """, (id_az, id_lot,qt))

            # ComposizioneLotto: il succo di mela in bottiglia è fatto da mele e zucchero
            composizioni = [
                  # usa 40 zucchero
                (1010, 1001, 50.0),
                (1020, 1002, 50.0),
                (1100,1010,20),
                (1100,1020,20),
                (1011,1100,10),
                (2000,1011,5)
            ]

            for output_lotto, input_lotto, quantita_usata in composizioni:
                db.execute_query("""
                    INSERT OR IGNORE INTO ComposizioneLotto (id_lotto_output, id_lotto_input, quantità_utilizzata)
                    VALUES (?, ?, ?)
                """, (output_lotto, input_lotto, quantita_usata))

            certificati = [
                (1001,"desc1",5),
                (1100,"des2c",5),
                (2000,"desc3",5)

            ]

            for id_lotto, desc, id_az in certificati:
                db.execute_query("""
                    INSERT OR IGNORE INTO Certificato (Id_lotto, Descrizione, Id_azienda_certificatore)
                    VALUES (?, ?, ?)
                """, (id_lotto, desc, id_az))

            
                
                
           

            # Richiesta di prodotto da parte di un rivenditore (vendita)
            db.execute_query("""
                INSERT INTO Richiesta (
                    Id_richiedente, Id_ricevente, Id_trasportatore, 
                    Id_prodotto, Quantita, Stato_ricevente, Stato_trasportatore
                )
                VALUES ( ?, ?, ?, ?, ?, ?, ?)
            """, (  
                1,  # Id_richiedente (azienda che vende il succo di mela in bottiglia)
                2,  # Id_ricevente (azienda di distribuzione)
                3,  # Id_trasportatore (trasportatore)
                2,  # Id prodotto "Succo di mela in bottiglia"
                50.0,  # Quantità richiesta
                'In attesa',  # Stato_ricevente
                'In attesa'   # Stato_trasportatore
            ))

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
            logger.info("Seed dei dati iniziali completato.")

        except Exception as e:
            logger.error(f"Errore durante l'inserimento dei dati di seed: {e}")


