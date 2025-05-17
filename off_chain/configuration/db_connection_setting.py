import atexit
import sqlite3
import os

from configuration.db_load_setting import DATABASE_PATH
from configuration.log_load_setting import logger


class DatabaseConnectionSetting:
    """
    Singleton class to handle SQLite3 database connections
    """

    _connection = None  # variable to store the connection

    @staticmethod
    def get_connection():

        """
        Returns a single instance of the database connection.
        """
        if DatabaseConnectionSetting._connection is None:
            try:
                DatabaseConnectionSetting._connection = sqlite3.connect(DATABASE_PATH)
                logger.info(f"BackEnd: get_connection: Name database is: {os.path.basename(DATABASE_PATH)}")
                logger.info(f"BackEnd: get_connection: Path for the database is: {DATABASE_PATH}")
                DatabaseConnectionSetting._connection.row_factory = sqlite3.Row
                logger.info("BackEnd: get_connection: The database connection was created successfully.")
            except sqlite3.ProgrammingError as e:
                logger.error(f"Cannot operate on a closed database: {e}")
                raise Exception(f"Cannot operate on a closed database: {e}")
            except sqlite3.DatabaseError as e:
                logger.error(f"File is encrypted or is not a database: {e}")
                raise Exception(f"File is encrypted or is not a database: {e}")
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                raise Exception(f"Unexpected Error: {e}")

        logger.info(f"BackEnd: get_connection: The database connection instance is: {DatabaseConnectionSetting._connection}")
        return DatabaseConnectionSetting._connection  # Retorna la conexión única

    @staticmethod
    def close_connection():
        """
        Closes the database connection if it exists.
        """
        if DatabaseConnectionSetting._connection:
            logger.info("BackEnd: Closing database .....")
            DatabaseConnectionSetting._connection.close()
            DatabaseConnectionSetting._connection = None

# Register connection close at the end of the program execution
# atexit.register(DatabaseConnectionSetting.close_connection)
# logger.info("step : Executed close connection ...")
