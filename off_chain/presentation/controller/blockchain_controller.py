from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import json
import os
import sqlite3
from session import Session
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl
from configuration.log_load_setting import logger
import subprocess
import requests
import time

# CONFIGURAZIONE
NODE_URL = "http://127.0.0.1:8545"  # Nodo Hardhat

# Ottieni il percorso assoluto alla directory del progetto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

# Usa percorsi assoluti per i file di configurazione
# Percorso diretto all'ABI del contratto negli artifacts
ABI_PATH = os.path.join(PROJECT_ROOT, "on_chain", "artifacts", "contracts", "SustainableFoodChain.sol", "SustainableFoodChain.json")
ADDRESS_PATH = os.path.join(PROJECT_ROOT, "on_chain", "contract_address.json")
# Definizione diretta del percorso del database
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'off_chain', 'database', 'database.db')

# Web3 setup
w3 = Web3(Web3.HTTPProvider(NODE_URL))

class BlockchainController:
    def __init__(self):
        self.controller = CredentialRepositoryImpl()
        with open(ABI_PATH) as f:
            contract_json = json.load(f)
            abi = contract_json["abi"]

        with open(ADDRESS_PATH) as f:
            address_json = json.load(f)
            contract_address = address_json.get("SustainableFoodChain")
            if not contract_address:
                raise ValueError("Indirizzo del contratto non trovato nel file contract_address.json sotto la chiave 'SustainableFoodChain'.")

        self.contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)

    @staticmethod
    def verifica_possesso_chiave(address_eth, signature, challenge):
        message = encode_defunct(text=challenge)
        recovered = Account.recover_message(message, signature=signature)
        return recovered.lower() == address_eth.lower()
    
    

    def firma_operazione(self,tipo, id_lotto, id_operazione):

        account = self.get_address()  # Funzione che recupera account locale

        messaggio = f"Conferma operazione {tipo} sil lotto {id_lotto} con id op {id_operazione}"
        messaggio_encoded = messaggio.replace(" ", "%20")

        url = f"http://localhost:5001/firma_operazione.html?messaggio={messaggio_encoded}&tipo={tipo}&lotto={id_lotto}&op={id_operazione}"
        # Rileva il sistema operativo e apri il browser in modo appropriato
        import platform
        import webbrowser
        
        system = platform.system()
        try:
            if system == 'Windows':
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                proc = subprocess.Popen([chrome_path, url])
                proc.wait()
            elif system == 'Darwin':  # macOS
                # Usa il browser predefinito su macOS
                webbrowser.open(url)
            else:  # Linux e altri
                # Prova a usare il browser predefinito
                webbrowser.open(url)
        except Exception as e:
            raise Exception(f"Errore nell'apertura del browser: {str(e)}")
        
        max_wait = 60  # secondi
        wait_interval = 3  # secondi
        start_time = time.time()

        while time.time() - start_time < max_wait:

            try:
                print(f"Attendo esito operazione {id_operazione} per l'account {account}")
                response = requests.get(f"http://localhost:5001/esito_operazione/{account}/{id_operazione}", timeout=10)
                data = response.json()
                if "esito" in data:
                    esito = data["esito"]
                    logger.info(f"Esito  {esito}")
                    return esito
            except requests.RequestException:
                pass  # Continua a riprovare

            time.sleep(wait_interval)

        raise TimeoutError("Timeout in attesa della firma tramite MetaMask")


    def firma_azione_compensativa(self, tipo, id_azione, co2_compensata):
        """
        Gestisce la firma di un'azione compensativa tramite MetaMask.
        
        Args:
            tipo: Il tipo di azione compensativa (es. 'Piantumazione', 'Energia rinnovabile')
            id_azione: L'ID dell'azione compensativa
            co2_compensata: La quantità di CO2 compensata dall'azione
        
        Returns:
            str: L'esito dell'operazione
        """
        account = self.get_address()  # Funzione che recupera account locale

        # Crea un messaggio descrittivo per l'azione compensativa
        messaggio = f"Conferma azione compensativa '{tipo}' con ID {id_azione} e CO2 compensata {co2_compensata}"
        messaggio_encoded = messaggio.replace(" ", "%20")

        # Costruisci l'URL con tutti i parametri necessari
        url = f"http://localhost:5001/firma_azione_compensativa.html?messaggio={messaggio_encoded}&tipo={tipo}&id_azione={id_azione}&co2_compensata={co2_compensata}"
        
        # Rileva il sistema operativo e apri il browser in modo appropriato
        import platform
        import webbrowser
        
        system = platform.system()
        try:
            if system == 'Windows':
                chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                proc = subprocess.Popen([chrome_path, url])
                proc.wait()
            elif system == 'Darwin':  # macOS
                # Usa il browser predefinito su macOS
                webbrowser.open(url)
            else:  # Linux e altri
                # Prova a usare il browser predefinito
                webbrowser.open(url)
        except Exception as e:
            raise Exception(f"Errore nell'apertura del browser: {str(e)}")
        
        # Attendi la risposta dal servizio web
        max_wait = 60  # secondi
        wait_interval = 3  # secondi
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                print(f"Attendo esito azione compensativa {id_azione} per l'account {account}")
                response = requests.get(f"http://localhost:5001/esito_azione_compensativa/{account}/{id_azione}", timeout=10)
                data = response.json()
                if "esito" in data:
                    esito = data["esito"]
                    logger.info(f"Esito azione compensativa: {esito}")
                    return esito
            except requests.RequestException as e:
                print(f"Errore nella richiesta HTTP: {e}")
                pass  # Continua a riprovare

            time.sleep(wait_interval)

        raise TimeoutError("Timeout in attesa della firma tramite MetaMask")


    def get_address(self):
        try:
            session = Session()
            current_user = getattr(session, "current_user", None)
            if current_user is None:
                raise ValueError("Utente non autenticato (current_user è None)")

            if not isinstance(current_user, dict):
                raise TypeError(f"current_user non è un dizionario: {type(current_user)}")

            if "id_azienda" not in current_user:
                raise ValueError("Chiave 'id_azienda' mancante in current_user")

            return self.controller.get_address_by_id(current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore nel recupero dell'indirizzo dell'utente: {e}")
            raise


    def invia_azione(self, tipo_azione, description, data_azione, co2_compensata, account_address):
        """Registra un'azione compensativa sulla blockchain"""
        try:
            # Debugging dei tipi di dati ricevuti
            logger.info(f"DATI RICEVUTI - tipo_azione: {tipo_azione} (tipo: {type(tipo_azione)}), "
                        f"description: {description} (tipo: {type(description)}), "
                        f"data_azione: {data_azione} (tipo: {type(data_azione)}), "
                        f"co2_compensata: {co2_compensata} (tipo: {type(co2_compensata)})")
            
            # Ottieni l'account dall'indirizzo blockchain dell'utente corrente
            account = Web3.to_checksum_address(account_address)
            nonce = w3.eth.get_transaction_count(account)
            gas_price = w3.eth.gas_price
            
            # Ottieni l'ID dell'azienda dall'indirizzo blockchain
            try:
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                
                # Prima trova l'ID delle credenziali dall'indirizzo blockchain
                cursor.execute(
                    "SELECT Id_credenziali FROM Credenziali WHERE Address = ?",
                    (account_address,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise Exception(f"Nessuna credenziale trovata per l'indirizzo {account_address}")
                    
                id_credenziali = result[0]
                
                # Poi trova l'ID dell'azienda dalle credenziali
                cursor.execute(
                    "SELECT Id_azienda FROM Azienda WHERE Id_credenziali = ?",
                    (id_credenziali,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise Exception(f"Nessuna azienda trovata per le credenziali con ID {id_credenziali}")
                    
                company_id = result[0]
                conn.close()
                
            except Exception as e:
                logger.error(f"Errore nel recupero dell'ID azienda: {e}")
                raise Exception(f"Errore nel recupero dell'ID azienda: {str(e)}")
            
            # Assicurati che i tipi di dati siano corretti per il contratto
            # Converti i tipi se necessario - usa try/except per gestire casi di stringa
            try:
                co2_compensata_int = int(co2_compensata)  # Converti in intero per uint8
            except (ValueError, TypeError):
                logger.warning(f"Impossibile convertire co2_compensata a intero: {co2_compensata}, impostando a 0")
                co2_compensata_int = 0
                
            logger.info(f"Invio azione: tipo={tipo_azione}, desc={description}, data={data_azione}, co2={co2_compensata_int}, company_id={company_id}")
            
            # Il contratto registerCompensationAction accetta solo 3 parametri, non 4
            # L'identificazione dell'azienda avviene tramite msg.sender nel contratto
            tx = self.contract.functions.registerCompensationAction(
                tipo_azione,
                co2_compensata_int,
                description
            ).build_transaction({
                'from': account,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': 300000,
            })

            # Firma e invia la transazione
            tx_hash = w3.eth.send_transaction(tx)
            
            # Aggiorna lo stato dell'azione compensativa nel database
            try:
                # Estrai l'ID dell'azione dalla descrizione se possibile
                id_azione_match = None
                if isinstance(description, str) and "ID" in description:
                    import re
                    id_match = re.search(r'ID\s+(\d+)', description)
                    if id_match:
                        id_azione_match = id_match.group(1)
                        logger.info(f"Estratto ID azione {id_azione_match} dalla descrizione")
                
                # Usa l'ID estratto o cerca nei parametri locali
                id_azione_param = id_azione_match
                if not id_azione_param and 'id_azione' in locals():
                    id_azione_param = id_azione
                
                if id_azione_param:
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    
                    # Verifica se l'azione esiste prima di aggiornare
                    cursor.execute(
                        "SELECT COUNT(*) FROM Azioni_compensative WHERE Id_azione = ?",
                        (id_azione_param,)
                    )
                    if cursor.fetchone()[0] > 0:
                        # Aggiorna il flag blockchain_registered
                        cursor.execute(
                            "UPDATE Azioni_compensative SET blockchain_registered = 1 WHERE Id_azione = ?",
                            (id_azione_param,)
                        )
                        conn.commit()
                        logger.info(f"Azione compensativa {id_azione_param} marcata come registrata sulla blockchain")
                    else:
                        logger.warning(f"Azione compensativa con ID {id_azione_param} non trovata nel database")
                    
                    conn.close()
                else:
                    logger.warning("Impossibile aggiornare lo stato dell'azione compensativa: ID azione non disponibile")
            except Exception as e:
                logger.error(f"Errore nell'aggiornamento dello stato dell'azione compensativa: {e}")
                # Non solleviamo l'eccezione qui per non interrompere il flusso principale
            
            return tx_hash.hex()
        
        except Exception as e:
            logger.error(f"Errore durante l'invio dell'operazione sulla blockchain: {e}")
            raise Exception(f"Errore durante l'invio dell'operazione sulla blockchain: {str(e)}")

    def invia_operazione(self, operation_type, description, batch_id, id_operazione, account_address):
        """Registra un'operazione sulla blockchain"""
        try:
            # Debugging dei tipi di dati ricevuti
            logger.info(f"DATI RICEVUTI - operation_type: {operation_type} (tipo: {type(operation_type)}), "
                        f"batch_id: {batch_id} (tipo: {type(batch_id)}), "
                        f"description: {description} (tipo: {type(description)})")
            
            # Verifica e gestisci tipi di dati anomali
            if isinstance(operation_type, list):
                logger.warning(f"operation_type è una lista: {operation_type}, usando il primo elemento o 0")
                operation_type = operation_type[0] if operation_type else 0
            
            if isinstance(batch_id, list):
                logger.warning(f"batch_id è una lista: {batch_id}, usando il primo elemento o 1")
                batch_id = batch_id[0] if batch_id else 1
                
            # Ottieni l'account dall'indirizzo blockchain dell'utente corrente
            account = Web3.to_checksum_address(account_address)
            nonce = w3.eth.get_transaction_count(account)
            gas_price = w3.eth.gas_price

            # Assicurati che i tipi di dati siano corretti per il contratto
            # operation_type deve essere uint8
            # batch_id deve essere uint256
            # description è una stringa
            
            # Converti i tipi se necessario - usa try/except per gestire casi di stringa
            try:
                operation_type_int = int(operation_type)  # Converti in intero per uint8
            except (ValueError, TypeError):
                logger.warning(f"Impossibile convertire operation_type a intero: {operation_type}, impostando a 0")
                operation_type_int = 0
                
            try:
                batch_id_int = int(batch_id)  # Converti in intero per uint256
            except (ValueError, TypeError):
                logger.warning(f"Impossibile convertire batch_id a intero: {batch_id}, impostando a 1")
                batch_id_int = 1
            
            logger.info(f"Invio operazione: tipo={operation_type_int}, lotto={batch_id_int}, desc={description}")

            tx = self.contract.functions.registerOperation(
                operation_type,
                description,
                1
            ).build_transaction({
                'from': account,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': 300000,
            })

            # Firma e invia la transazione
            tx_hash = w3.eth.send_transaction(tx)
            
            # Aggiorna lo stato dell'operazione nel database
            if id_operazione is not None:
                try:
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE Operazione SET blockchain_registered = 1 WHERE Id_operazione = ?",
                        (id_operazione,)
                    )
                    conn.commit()
                    conn.close()
                    logger.info(f"Operazione {id_operazione} marcata come registrata sulla blockchain")
                except Exception as e:
                    logger.error(f"Errore nell'aggiornamento dello stato dell'operazione: {e}")
                    # Non solleviamo l'eccezione qui per non interrompere il flusso principale
            
            return tx_hash.hex()
        
        except Exception as e:
            logger.error(f"Errore durante l'invio dell'operazione sulla blockchain: {e}")
            raise Exception(f"Errore durante l'invio dell'operazione sulla blockchain: {str(e)}")
            
    def get_operazioni_company(self):
        try:
            address = self.get_address()
            checksum_address = Web3.to_checksum_address(address)
            res = self.contract.functions.getCompanyOperations(checksum_address).call()
            logger.info(f"Operazioni recuperate per l'azienda {address}: {res}")
            return res
        except Exception as e:
            logger.error(f"Errore nel recupero delle operazioni per {address}: {e}")
            raise Exception(f"Errore durante il recupero delle operazioni: {str(e)}")
            
    def is_company_registered(self, address):
        """Verifica se un indirizzo Ethereum è registrato come azienda sulla blockchain
        
        Args:
            address: L'indirizzo Ethereum da verificare
            
        Returns:
            bool: True se l'azienda è registrata, False altrimenti
        """
        try:
            checksum_address = Web3.to_checksum_address(address)
            is_registered = self.contract.functions.isCompanyAddressRegistered(checksum_address).call()
            logger.info(f"Verifica registrazione per l'indirizzo {address}: {is_registered}")
            return is_registered
        except Exception as e:
            logger.error(f"Errore nella verifica della registrazione dell'azienda {address}: {e}")
            return False