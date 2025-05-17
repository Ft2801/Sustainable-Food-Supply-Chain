# Standard Library Imports
import sys
import os
import time
import subprocess
import shutil

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


def verify_hardhat_installation():
    """Verifica e installa Hardhat se necessario"""
    logger.info("Verifica dell'installazione di Hardhat...")
    on_chain_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'on_chain')
    
    # Verifica se Hardhat è installato
    hardhat_path = os.path.join(on_chain_dir, 'node_modules', 'hardhat')
    if not os.path.exists(hardhat_path):
        logger.info("Hardhat non trovato. Installazione in corso...")
        try:
            # Installazione di Hardhat
            install_process = subprocess.run(
                'npm install --save-dev hardhat',
                cwd=on_chain_dir,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Hardhat installato con successo")
        except subprocess.CalledProcessError as e:
            logger.error(f"Errore durante l'installazione di Hardhat: {e.stderr}")
            sys.exit(1)
    else:
        logger.info("Hardhat già installato")


def start_hardhat_node():
    """Avvia un nodo Hardhat in un terminale separato"""
    logger.info("Avvio del nodo Hardhat in un terminale separato...")
    on_chain_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'on_chain')
    
    # Comando per aprire un nuovo terminale e avviare Hardhat
    cmd = f'start cmd.exe /k "cd /d {on_chain_dir} && npx hardhat node"'
    
    # Eseguire il comando per aprire un nuovo terminale
    subprocess.run(cmd, shell=True)
    
    # Attendere che il nodo sia avviato
    logger.info("Attesa avvio del nodo Hardhat (10 secondi)...")
    time.sleep(10)  # Attendere 10 secondi per l'avvio del nodo


def compile_and_deploy_contracts():
    """Compila e deploya i contratti sul nodo Hardhat locale"""
    logger.info("Compilazione e deployment dei contratti...")
    on_chain_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'on_chain')
    
    # Compilare i contratti
    logger.info("Compilazione dei contratti...")
    try:
        compile_process = subprocess.run(
            'npx hardhat compile',
            cwd=on_chain_dir,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Compilazione completata con successo")
    except subprocess.CalledProcessError as e:
        logger.error(f"Errore durante la compilazione dei contratti: {e.stderr}")
        sys.exit(1)
    
    # Deployare i contratti
    logger.info("Deployment dei contratti...")
    try:
        deploy_process = subprocess.run(
            'npx hardhat run scripts/deploy.js --network localhost',
            cwd=on_chain_dir,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Deployment completato con successo")
    except subprocess.CalledProcessError as e:
        logger.error(f"Errore durante il deployment dei contratti: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    # Verifica e installa Hardhat se necessario
    verify_hardhat_installation()
    
    # Avvia il nodo Hardhat in un terminale separato
    start_hardhat_node()
    
    # Compila e deploya i contratti
    compile_and_deploy_contracts()
    
    # Configure the database before starting the graphical interface
    setup_database()
    
    # Create a session
    session = Session()
    
    # Setup GUI and get application instance
    app, window = setup_gui(session)
    
    # Messaggio di avvio completato
    logger.info("Applicazione avviata con successo")
    
    # Start the application event loop
    sys.exit(app.exec_())
