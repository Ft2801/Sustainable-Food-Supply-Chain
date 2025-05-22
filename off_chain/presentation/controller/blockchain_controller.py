from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
import json
import os
import sqlite3
from session import Session
from persistence.repository_impl.credential_repository_impl import CredentialRepositoryImpl
from configuration.log_load_setting import logger

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

    def get_adress(self):
        try:
            return self.controller.get_adrress_by_id(Session().current_user["id_azienda"])
        except Exception as e:
            logger.error(f"Errore nell'ottenimento dell'utente: {e}")
            raise Exception(f"Errore nel recupero utente: {str(e)}") from e

    def invia_operazione(self, private_key, operation_type, description, batch_id, id_operazione=None):
        account = Account.from_key(private_key)
        sender = account.address

        nonce = w3.eth.get_transaction_count(sender)
        gas_price = w3.eth.gas_price

        tx = self.contract.functions.registerOperation(
            operation_type,
            description,
            batch_id
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
        
        # Se è stato fornito l'ID dell'operazione, aggiorna il suo stato nel database
        if id_operazione is not None:
            try:
                # Aggiorna lo stato dell'operazione nel database
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
