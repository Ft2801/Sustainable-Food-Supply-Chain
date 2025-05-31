# pylint: disable= no-name-in-module,
# pylint: disable= import-error
# pylint: disable= line-too-long
# pylint: disable= trailing-whitespace

import os
import sqlite3
import subprocess
from typing import List, Dict, Any, Tuple
import sys

# Aggiungi il percorso radice del progetto al sys.path per consentire gli import relativi
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configuration.log_load_setting import logger
from configuration.database import Database
from persistence.repository_impl.richieste_repository_impl import RichiesteRepositoryImpl, BlockchainConfig

def get_all_companies() -> List[Dict[str, Any]]:
    """
    Recupera tutte le aziende dal database
    
    Returns:
        List[Dict[str, Any]]: Lista di dizionari contenenti i dati delle aziende
    """
    db = Database()
    try:
        query = """
        SELECT a.Id_azienda, a.Nome, a.Tipo, a.Indirizzo, c.address 
        FROM Azienda a 
        JOIN Credenziali c ON a.Id_credenziali = c.Id_credenziali
        """
        results = db.fetch_results(query)
        companies = []
        for row in results:
            companies.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'address_physical': row[3],
                'address_eth': row[4]
            })
        return companies
    except Exception as e:
        logger.error(f"Errore nel recupero delle aziende: {e}")
        return []
    finally:
        db.close()

def register_company_on_blockchain(company: Dict[str, Any]) -> bool:
    """
    Registra un'azienda sulla blockchain
    
    Args:
        company (Dict[str, Any]): Dizionario contenente i dati dell'azienda
        
    Returns:
        bool: True se l'operazione è riuscita, False altrimenti
    """
    try:
        # Utilizziamo il metodo esistente nella classe RichiesteRepositoryImpl
        repo = RichiesteRepositoryImpl()
        success = repo.register_company_on_blockchain(company['id'])
        if success:
            logger.info(f"Azienda {company['name']} (ID: {company['id']}) registrata con successo sulla blockchain")
        else:
            logger.warning(f"Impossibile registrare l'azienda {company['name']} (ID: {company['id']}) sulla blockchain")
        return success
    except Exception as e:
        logger.error(f"Errore nella registrazione dell'azienda {company['name']} (ID: {company['id']}) sulla blockchain: {e}")
        return False

def register_all_companies_on_blockchain() -> Tuple[int, int]:
    """
    Registra tutte le aziende sulla blockchain
    
    Returns:
        Tuple[int, int]: (numero di aziende registrate con successo, numero totale di aziende)
    """
    companies = get_all_companies()
    success_count = 0
    total_count = len(companies)
    
    logger.info(f"Trovate {total_count} aziende nel database")
    
    for company in companies:
        if company['address_eth'] and company['address_eth'].startswith('0x'):
            logger.info(f"Tentativo di registrazione dell'azienda {company['name']} (ID: {company['id']}) sulla blockchain")
            if register_company_on_blockchain(company):
                success_count += 1
        else:
            logger.warning(f"L'azienda {company['name']} (ID: {company['id']}) non ha un indirizzo Ethereum valido")
    
    return success_count, total_count

def main():
    """
    Funzione principale
    """
    logger.info("Avvio del processo di registrazione delle aziende sulla blockchain")
    
    # Verifica che la blockchain sia disponibile
    blockchain_config = BlockchainConfig()
    if not blockchain_config.blockchain_available:
        logger.error("Blockchain non disponibile. Assicurati che il nodo Hardhat sia in esecuzione.")
        return
    
    success_count, total_count = register_all_companies_on_blockchain()
    
    logger.info(f"Registrazione completata: {success_count}/{total_count} aziende registrate con successo")

if __name__ == "__main__":
    main()
