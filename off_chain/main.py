# Standard Library Imports
import sys
import os

from configuration.log_load_setting import logger
from database.db_migrations import DatabaseMigrations
from configuration.database import Database
from session import Session

# Import the modules we've created
from blockchain_manager import blockchain_interactor
from gui_manager import setup_gui

def setup_database():
    try:
        DatabaseMigrations.run_migrations()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)  # Stops the application if there is a critical error

if __name__ == "__main__":
    # Configure the database before starting the graphical interface
    setup_database()
    
    # Create a session
    session = Session()
    
    # Setup GUI and get application instance
    app, window = setup_gui(session)
    
    # Start the application event loop
    sys.exit(app.exec_())
