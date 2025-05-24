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
    

    def firma_operazione(self,tipo, quantita, unita, prodotto):

        account = self.get_adress()  # Funzione che recupera account locale

        messaggio = f"Conferma operazione {tipo} di {quantita} {unita} di {prodotto}"
        messaggio_encoded = messaggio.replace(" ", "%20")

        url = f"http://localhost:5000/firma_operazione.html?messaggio={messaggio_encoded}&tipo={tipo}&quantita={quantita}&unita={unita}&prodotto={prodotto}"
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        proc = subprocess.Popen([chrome_path, url])
        proc.wait()

        # Dopo la chiusura interrogo il backend per conoscere l'esito
        try:
            res = requests.get(f"http://localhost:5000/esito_operazione/{account}")
            esito = res.json()["esito"]
        except Exception as e:
            raise Exception(f"Errore durante la richiesta dell'esito: {str(e)}")





    def get_adress(self):
        try:
            return self.controller.get_adrress_by_id(Session()._current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore nell'ottenimento dell'utente: {e}")
            raise Exception(f"Errore nel recupero utente: {str(e)}") from e

    def invia_azione_compensativa(self, private_key, action_type, co2_reduction, description, id_azione=None):
        """Registra un'azione compensativa sulla blockchain"""
        account = Account.from_key(private_key)
        sender = account.address

        nonce = w3.eth.get_transaction_count(sender)
        gas_price = w3.eth.gas_price

        tx = self.contract.functions.registerCompensationAction(
            action_type,
            int(co2_reduction),  # Converti in intero per la blockchain
            description
        ).build_transaction({
            'from': sender,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 500000,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        
        # Gestisci sia le versioni vecchie che nuove di Web3.py
        try:
            # Versione più recente di Web3.py
            raw_tx = signed_tx.raw_transaction
        except AttributeError:
            try:
                # Versione precedente di Web3.py
                raw_tx = signed_tx.rawTransaction
            except AttributeError:
                # Se entrambi falliscono, mostra un errore dettagliato
                logger.error(f"Errore: l'oggetto SignedTransaction non ha né l'attributo raw_transaction né rawTransaction. Attributi disponibili: {dir(signed_tx)}")
                raise Exception("Errore nella firma della transazione: formato non supportato")
        
        tx_hash = w3.eth.send_raw_transaction(raw_tx)
        
        # Se è stato fornito l'ID dell'azione, aggiorna il suo stato nel database
        if id_azione is not None:
            try:
                # Aggiorna lo stato dell'azione nel database
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Azioni_compensative SET blockchain_registered = 1 WHERE Id_azione = ?",
                    (id_azione,)
                )
                conn.commit()
                conn.close()
                logger.info(f"Azione compensativa {id_azione} marcata come registrata sulla blockchain")
            except Exception as e:
                logger.error(f"Errore nell'aggiornamento dello stato dell'azione compensativa: {e}")
                # Non solleviamo l'eccezione qui per non interrompere il flusso principale
        
        return tx_hash.hex()

    def invia_operazione(self, operation_type, description, batch_id, id_operazione):
        """Registra un'operazione sulla blockchain"""
        try:
            # Ottieni l'account dall'indirizzo blockchain dell'utente corrente
            account = self.get_adress()
            nonce = w3.eth.get_transaction_count(account)
            gas_price = w3.eth.gas_price

            tx = self.contract.functions.registerOperation(
                operation_type,
                description,
                batch_id
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