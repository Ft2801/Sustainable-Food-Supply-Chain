# assign_hardhat_accounts.py - Assegna gli account Hardhat alle nuove aziende che si registrano

import sqlite3
import os
import sys
from web3 import Web3
from typing import Optional, List, Tuple

# Aggiungi il percorso root del progetto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from off_chain.configuration.log_load_setting import logger

# Percorso del database
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "database.db")

# URL del nodo Hardhat
NODE_URL = "http://127.0.0.1:8545"

# Lista delle aziende principali (che hanno già account assegnati)
MAIN_COMPANIES = [
    "Azienda Agricola Verde",
    "Trasporti EcoExpress",
    "trasformazione BioCheck",
    "riv BioCheck",
    "cert BioCheck"
]

def add_address_column():
    """Aggiunge la colonna 'address' alla tabella Credenziali se non esiste già"""
    try:
        # Connessione al database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verifica se la colonna 'address' esiste già
        cursor.execute("PRAGMA table_info(Credenziali)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'address' not in column_names:
            # Aggiungi la colonna 'address'
            cursor.execute("ALTER TABLE Credenziali ADD COLUMN address TEXT")
            logger.info("Colonna 'address' aggiunta alla tabella Credenziali")
            conn.commit()
        else:
            logger.info("La colonna 'address' esiste già nella tabella Credenziali")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Errore nell'aggiunta della colonna 'address': {e}")
        return False

def get_available_accounts() -> List[str]:
    """Ottiene gli account Hardhat disponibili (non ancora assegnati)"""
    try:
        # Connessione a Web3
        logger.info(f"Tentativo di connessione al nodo Hardhat su {NODE_URL}")
        w3 = Web3(Web3.HTTPProvider(NODE_URL))
        if not w3.is_connected():
            logger.error("Impossibile connettersi al nodo Hardhat. Assicurati che il nodo sia in esecuzione.")
            return []
        logger.info("Connessione al nodo Hardhat riuscita")
        
        # Ottieni tutti gli account Hardhat
        all_hardhat_accounts = w3.eth.accounts
        logger.info(f"Trovati {len(all_hardhat_accounts)} account Hardhat totali")
        
        # Connessione al database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Ottieni gli account giu00e0 assegnati
        cursor.execute("""
            SELECT c.address 
            FROM Credenziali c 
            WHERE c.address IS NOT NULL
        """)
        assigned_accounts = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Filtra gli account disponibili (non ancora assegnati)
        available_accounts = [account for account in all_hardhat_accounts if account not in assigned_accounts]
        logger.info(f"Trovati {len(available_accounts)} account Hardhat disponibili")
        
        return available_accounts
    except Exception as e:
        logger.error(f"Errore nell'ottenimento degli account Hardhat disponibili: {e}")
        return []

def assign_account_to_company(company_id: int) -> Optional[str]:
    """Assegna un account Hardhat a una specifica azienda"""
    try:
        # Ottieni gli account disponibili
        available_accounts = get_available_accounts()
        if not available_accounts:
            logger.warning("Nessun account Hardhat disponibile per l'assegnazione")
            return None
        
        # Prendi il primo account disponibile
        account_to_assign = available_accounts[0]
        
        # Connessione al database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Ottieni l'ID delle credenziali dell'azienda
        cursor.execute("""
            SELECT a.Id_credenziali, a.Nome 
            FROM Azienda a 
            WHERE a.Id_azienda = ?
        """, (company_id,))
        result = cursor.fetchone()
        
        if not result:
            logger.warning(f"Azienda con ID {company_id} non trovata")
            conn.close()
            return None
        
        credentials_id, company_name = result
        
        # Verifica se l'azienda ha giu00e0 un indirizzo
        cursor.execute("""
            SELECT c.address 
            FROM Credenziali c 
            WHERE c.Id_credenziali = ?
        """, (credentials_id,))
        current_address = cursor.fetchone()[0]
        
        if current_address:
            logger.info(f"L'azienda {company_name} (ID: {company_id}) ha giu00e0 un indirizzo: {current_address}")
            conn.close()
            return current_address
        
        # Assegna l'account all'azienda
        cursor.execute(
            "UPDATE Credenziali SET address = ? WHERE Id_credenziali = ?", 
            (account_to_assign, credentials_id)
        )
        conn.commit()
        
        logger.info(f"Assegnato account {account_to_assign} all'azienda {company_name} (ID: {company_id})")
        conn.close()
        
        return account_to_assign
    except Exception as e:
        logger.error(f"Errore nell'assegnazione dell'account all'azienda {company_id}: {e}")
        return None

def get_company_address(company_id: int) -> Optional[str]:
    """Ottiene l'indirizzo Ethereum di un'azienda specifica"""
    try:
        # Connessione al database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Ottieni l'indirizzo dell'azienda
        cursor.execute("""
            SELECT c.address 
            FROM Azienda a 
            JOIN Credenziali c ON a.Id_credenziali = c.Id_credenziali
            WHERE a.Id_azienda = ?
        """, (company_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if not result:
            logger.warning(f"Azienda con ID {company_id} non trovata")
            return None
        
        return result[0]
    except Exception as e:
        logger.error(f"Errore nell'ottenimento dell'indirizzo dell'azienda {company_id}: {e}")
        return None

def get_accounts_status() -> Tuple[int, int, List[str]]:
    """Ottiene lo stato degli account Hardhat (totali, assegnati, disponibili)"""
    try:
        # Connessione a Web3
        w3 = Web3(Web3.HTTPProvider(NODE_URL))
        if not w3.is_connected():
            logger.error("Impossibile connettersi al nodo Hardhat")
            return 0, 0, []
        
        # Ottieni tutti gli account Hardhat
        all_accounts = w3.eth.accounts
        total_accounts = len(all_accounts)
        
        # Connessione al database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Ottieni gli account giu00e0 assegnati
        cursor.execute("""
            SELECT c.address 
            FROM Credenziali c 
            WHERE c.address IS NOT NULL
        """)
        assigned_accounts = [row[0] for row in cursor.fetchall()]
        assigned_count = len(assigned_accounts)
        
        # Calcola gli account disponibili
        available_accounts = [account for account in all_accounts if account not in assigned_accounts]
        
        conn.close()
        
        return total_accounts, assigned_count, available_accounts
    except Exception as e:
        logger.error(f"Errore nell'ottenimento dello stato degli account: {e}")
        return 0, 0, []

def assign_hardhat_accounts():
    """Assegna gli account Hardhat alle aziende che non ne hanno uno"""
    try:
        # Ottieni gli account disponibili
        available_accounts = get_available_accounts()
        if not available_accounts:
            logger.warning("Nessun account Hardhat disponibile per l'assegnazione")
            return False
        
        # Connessione al database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Ottieni tutte le aziende senza indirizzo
        cursor.execute("""
            SELECT a.Id_azienda, a.Nome, a.Tipo, c.Id_credenziali 
            FROM Azienda a 
            JOIN Credenziali c ON a.Id_credenziali = c.Id_credenziali
            WHERE c.address IS NULL OR c.address = ''
        """)
        companies_without_address = cursor.fetchall()
        
        if not companies_without_address:
            logger.info("Tutte le aziende hanno giu00e0 un indirizzo")
            conn.close()
            return True
        
        # Assegna gli account disponibili alle aziende senza indirizzo
        account_index = 0
        for company in companies_without_address:
            if account_index >= len(available_accounts):
                logger.warning("Non ci sono piu00f9 account disponibili")
                break
                
            company_id, company_name, company_type, credentials_id = company
            
            # Assegna l'account all'azienda
            account_to_assign = available_accounts[account_index]
            cursor.execute(
                "UPDATE Credenziali SET address = ? WHERE Id_credenziali = ?", 
                (account_to_assign, credentials_id)
            )
            logger.info(f"Assegnato account {account_to_assign} all'azienda {company_name} (ID: {company_id}, Tipo: {company_type})")
            account_index += 1
        
        conn.commit()
        logger.info(f"Assegnati {account_index} account Hardhat alle aziende")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Errore nell'assegnazione degli account Hardhat: {e}")
        return False

def main():
    try:
        logger.info("Inizio dello script di gestione degli account Hardhat")
        logger.info(f"Percorso del database: {DATABASE_PATH}")
        
        # Verifica che il file del database esista
        if not os.path.exists(DATABASE_PATH):
            logger.error(f"Il file del database non esiste: {DATABASE_PATH}")
            return
            
        # Aggiungi la colonna 'address' se non esiste
        if not add_address_column():
            logger.error("Errore nell'aggiunta della colonna 'address'")
            return
        
        # Ottieni lo stato degli account
        total, assigned, available = get_accounts_status()
        logger.info(f"Stato degli account Hardhat: {total} totali, {assigned} assegnati, {len(available)} disponibili")
        
        # Mostra le opzioni disponibili
        print("\nGestione degli account Hardhat")
        print("=========================\n")
        print(f"Account Hardhat totali: {total}")
        print(f"Account assegnati: {assigned}")
        print(f"Account disponibili: {len(available)}\n")
        print("Opzioni disponibili:")
        print("1. Assegna account alle aziende senza indirizzo")
        print("2. Assegna account a un'azienda specifica")
        print("3. Visualizza lo stato degli account")
        print("4. Esci\n")
        
        choice = input("Seleziona un'opzione (1-4): ")
        
        if choice == "1":
            # Assegna gli account Hardhat alle aziende senza indirizzo
            if assign_hardhat_accounts():
                logger.info("Assegnazione degli account Hardhat completata con successo")
            else:
                logger.error("Errore nell'assegnazione degli account Hardhat")
        
        elif choice == "2":
            # Assegna un account a un'azienda specifica
            company_id = input("Inserisci l'ID dell'azienda: ")
            try:
                company_id = int(company_id)
                address = assign_account_to_company(company_id)
                if address:
                    print(f"Account {address} assegnato all'azienda con ID {company_id}")
                else:
                    print(f"Impossibile assegnare un account all'azienda con ID {company_id}")
            except ValueError:
                print("L'ID dell'azienda deve essere un numero intero")
        
        elif choice == "3":
            # Visualizza lo stato degli account
            total, assigned, available = get_accounts_status()
            print(f"\nAccount Hardhat totali: {total}")
            print(f"Account assegnati: {assigned}")
            print(f"Account disponibili: {len(available)}")
            
            if available:
                print("\nAccount disponibili:")
                for i, account in enumerate(available):
                    print(f"{i+1}. {account}")
        
        elif choice == "4":
            print("Uscita dal programma")
        
        else:
            print("Opzione non valida")
            
    except Exception as e:
        logger.error(f"Errore imprevisto durante l'esecuzione dello script: {e}")

if __name__ == "__main__":
    main()
