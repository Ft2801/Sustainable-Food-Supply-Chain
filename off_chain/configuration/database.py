import sqlite3
import os
from configuration.db_load_setting import DATABASE_PATH
from configuration.log_load_setting import logger

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
                self.conn = sqlite3.connect(DATABASE_PATH, timeout=10)  # Connessione al database
                # Enable foreign key constraints
                self.conn.execute("PRAGMA foreign_keys = ON")
                self.cur = self.conn.cursor()  # Cursore
                logger.info(f"BackEnd: get_connection: Name database is: {os.path.basename(DATABASE_PATH)}")
                logger.info(f"BackEnd: get_connection: Path for the database is: {DATABASE_PATH}")
                self._connection_initialized = True
            except sqlite3.ProgrammingError as e:
                logger.error(f"Cannot operate on a closed database: {e}")
                raise Exception(f"Cannot operate on a closed database: {e}")
            except sqlite3.DatabaseError as e:
                logger.error(f"File is encrypted or is not a database: {e}")
                raise Exception(f"File is encrypted or is not a database: {e}")
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
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
                logger.error(f"Database bloccato (timeout raggiunto?): {e}")
            else:
                print(f"Errore SQL: {e}")
            raise e
        except sqlite3.Error as e:
            print(f"Errore generico nel database: {e}")
            raise e

    @classmethod
    def fetch_results(cls, query, params=()):
        """Esegue una query di selezione e restituisce i risultati."""
        if not hasattr(cls, "conn") or cls.conn is None:
            raise ConnectionError("La connessione al database non è attiva.")
        
        try:
            cls._instance.cur.execute(query, params)
            return cls._instance.cur.fetchall()
        
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                logger.error(f"Database bloccato (timeout raggiunto?): {e}")
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
                logger.error(f"Database bloccato (timeout raggiunto?): {e}")
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
                logger.info(f"BackEnd: execute_transaction: Info executing query: {query} with params: {params}")
                self.cur.execute(query, params)

            self.conn.commit()  # Commit di tutte le modifiche
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                logger.error(f"Database bloccato (timeout raggiunto?): {e}")
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
                logger.info("BackEnd: Closing database .....")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

    # Alias for close() for backward compatibility
    close_connection = close

    def __del__(self):
        """Ensure safe connection closure when the instance is destroyed."""
        self.close()
