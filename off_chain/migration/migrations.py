import sqlite3
from configuration.db_load_setting import DATABASE_PATH

def create_tables():
    """Crea le tabelle necessarie nel database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Credenziali (
        Id_credenziali INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE NOT NULL,
        Password TEXT NOT NULL,
        topt_secret TEXT NOT NULL
    )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Soglie (
            Operazione TEXT NOT NULL,
            Prodotto TEXT NOT NULL,
            Soglia_Massima REAL NOT NULL,
            Tipo TEXT NOT NULL,
            PRIMARY KEY (Operazione, Prodotto)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Azienda (
            Id_azienda INTEGER PRIMARY KEY AUTOINCREMENT,
            Id_credenziali INTEGER NOT NULL,
            Tipo TEXT CHECK(Tipo IN ('Agricola', 'Trasportatore', 'Trasformatore', 'Rivenditore', 'Certificatore')),
            Nome TEXT NOT NULL,
            Indirizzo TEXT NOT NULL,
            CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Id_credenziali) REFERENCES Credenziali(Id_credenziali) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Prodotto (
            Id_prodotto INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT NOT NULL,
            Quantita REAL NOT NULL,
            Stato INTEGER,
            Data_di_inserimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Operazione (
            Id_operazione INTEGER PRIMARY KEY AUTOINCREMENT,
            Id_azienda INTEGER NOT NULL,
            Id_prodotto INTEGER NOT NULL,
            Data_operazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Consumo_CO2 REAL NOT NULL,
            Operazione TEXT,
            FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
            FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Certificato (
            Id_certificato INTEGER PRIMARY KEY AUTOINCREMENT,
            Id_prodotto INTEGER NOT NULL,
            Descrizione TEXT,
            Id_azienda_certificatore INTEGER NOT NULL,
            Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Id_azienda_certificatore) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE,
            FOREIGN KEY (Id_prodotto) REFERENCES Prodotto(Id_prodotto) ON DELETE CASCADE
        )
    ''')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Composizione (
            Prodotto INTEGER NOT NULL,
            Materia_prima INTEGER NOT NULL,
            PRIMARY KEY (Prodotto, Materia_prima)
        )
    """)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Azioni_compensative (
            Id_azione INTEGER PRIMARY KEY AUTOINCREMENT,
            Data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Id_azienda INTEGER NOT NULL,
            Co2_compensata REAL NOT NULL,
            Nome_azione TEXT NOT NULL,
            FOREIGN KEY (Id_azienda) REFERENCES Azienda(Id_azienda) ON DELETE CASCADE
        )
    """)

    # Commit delle modifiche e chiusura della connessione
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
