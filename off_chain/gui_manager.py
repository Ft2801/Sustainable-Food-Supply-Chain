# Standard Library Imports
import sys
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox

from configuration.log_load_setting import logger
from presentation.view.vista_accedi import VistaAccedi
from blockchain_manager import BlockchainSetupThread

def setup_gui(session):
    """Setup and initialize the GUI components"""
    # Starting the PyQt application
    app = QApplication(sys.argv)
    logger.info("Frontend: Starting the PyQt application...")
    
    logger.info(f"Start session on {session.start_app}")

    # Show Splash Screen
    splash = QSplashScreen(QPixmap("presentation/resources/logo_splash.png"), Qt.WindowStaysOnTopHint)
    splash.show()

    # Start blockchain setup in a separate thread
    blockchain_setup = BlockchainSetupThread(splash_screen=splash)
    blockchain_setup.start()
    
    # Wait for blockchain setup to complete with timeout
    blockchain_setup.join(timeout=60)  # Aumentato a 60 secondi timeout
    
    if not blockchain_setup.is_alive() and blockchain_setup.success:
        logger.info("Blockchain setup completed successfully")
    else:
        if blockchain_setup.is_alive():
            logger.warning("Blockchain setup is taking longer than expected, continuing anyway")
            # Non aspettiamo il completamento del thread per non bloccare l'avvio dell'applicazione
        
        # Invece di mostrare un messaggio di errore, mostriamo un messaggio informativo
        if blockchain_setup.error_message:
            logger.info(f"Note: {blockchain_setup.error_message}. The application will continue with limited blockchain functionality.")
        else:
            logger.info("Note: The application will continue with limited blockchain functionality.")

    time.sleep(1)

    # Create the main window
    window = VistaAccedi()
    window.show()
    
    # Hide splash screen
    splash.finish(window)
    
    # Start the application event loop
    return app, window
