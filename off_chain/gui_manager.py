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
            logger.error("Blockchain setup timed out")
            blockchain_setup.join()  # Aspetta comunque il completamento del thread
        logger.warning("Proceeding without blockchain functionality")
        if blockchain_setup.error_message:
            logger.error(f"Blockchain setup failed: {blockchain_setup.error_message}")

    time.sleep(1)

    # Create the main window
    window = VistaAccedi()
    window.show()
    
    # Hide splash screen
    splash.finish(window)
    
    # Start the application event loop
    return app, window
