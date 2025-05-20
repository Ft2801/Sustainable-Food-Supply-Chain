# interact_contract.py - Interacts with contracts on the blockchain using Hardhat.

import json
import os
import time
import glob
from web3 import Web3
from typing import Dict, Any, List
import sys

# Import logger from off_chain configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from off_chain.configuration.log_load_setting import logger

class BlockchainInteractor:
    def __init__(self):
        # Connect to Hardhat node
        max_attempts = 10
        for i in range(max_attempts):
            try:
                self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
                if self.w3.is_connected():
                    logger.info("Connected to Hardhat node")
                    break
            except Exception as e:
                if i == max_attempts - 1:
                    raise Exception(f"Failed to connect to Hardhat node: {e}")
                logger.debug(f"Waiting for Hardhat node... ({i+1}/{max_attempts})")
                time.sleep(1)
        
        # Default account for transactions
        self.default_account = self.w3.eth.accounts[0]
        self.w3.eth.default_account = self.default_account
        
        # Load contract ABIs from artifacts directory
        artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts", "contracts")
        logger.info(f"Loading contract ABIs from {artifacts_dir}")
        
        # Initialize contracts dictionary
        self.contracts = {}
        
        # Get the latest deployed contracts from the blockchain
        self._load_contracts_from_artifacts(artifacts_dir)

    def _load_contracts_from_artifacts(self, artifacts_dir):
        # Mappa per tenere traccia dei contratti trovati
        contract_abis = {}
        
        # Cerca tutti i file JSON nelle sottodirectory di artifacts_dir
        for root, dirs, files in os.walk(artifacts_dir):
            for file in files:
                if file.endswith('.json') and not file.endswith('.dbg.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            contract_data = json.load(f)
                            if 'contractName' in contract_data and 'abi' in contract_data:
                                contract_name = contract_data['contractName']
                                contract_abis[contract_name] = contract_data['abi']
                                logger.info(f"Found ABI for contract {contract_name}")
                    except Exception as e:
                        logger.error(f"Error loading contract ABI from {file_path}: {e}")
        
        # Ottieni gli indirizzi dei contratti deployati
        deployed_contracts = self._get_deployed_contracts()
        
        # Inizializza i contratti con gli ABI e gli indirizzi
        for contract_name, contract_address in deployed_contracts.items():
            if contract_name in contract_abis:
                self.contracts[contract_name] = self.w3.eth.contract(
                    address=contract_address,
                    abi=contract_abis[contract_name]
                )
                logger.info(f"Loaded contract {contract_name} at address {contract_address}")
            else:
                logger.error(f"ABI not found for contract {contract_name}")

    def _get_deployed_contracts(self):
        """Ottiene gli indirizzi dei contratti deployati da Hardhat"""
        # In Hardhat, i contratti vengono deployati in ordine e gli indirizzi sono prevedibili
        # Il primo contratto deployato ha sempre lo stesso indirizzo
        deployed_contracts = {}
        
        # Ottieni le transazioni del blocco di genesi e dei blocchi successivi
        # per trovare i contratti deployati
        try:
            # Ottieni il numero dell'ultimo blocco
            latest_block = self.w3.eth.block_number
            logger.info(f"Scanning {latest_block + 1} blocks for contract deployments")
            
            # Cerca le transazioni di creazione dei contratti
            for block_num in range(latest_block + 1):
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                for tx in block.transactions:
                    # Le transazioni di creazione dei contratti hanno 'to' impostato a None o '0x'
                    if tx.to is None or tx.to == '0x' or tx.to == '0x0000000000000000000000000000000000000000':
                        # Ottieni la ricevuta della transazione per vedere se ha creato un contratto
                        receipt = self.w3.eth.get_transaction_receipt(tx.hash)
                        if receipt.contractAddress:
                            # Cerca di determinare il nome del contratto
                            contract_name = self._get_contract_name_from_code(receipt.contractAddress)
                            if contract_name:
                                deployed_contracts[contract_name] = receipt.contractAddress
                                logger.info(f"Found deployed contract {contract_name} at {receipt.contractAddress}")
            
            # Se non sono stati trovati contratti, usa gli indirizzi predefiniti di Hardhat
            if not deployed_contracts:
                logger.warning("No deployed contracts found, using default Hardhat addresses")
                # Questi sono gli indirizzi predefiniti di Hardhat per i primi contratti deployati
                deployed_contracts = self._get_default_hardhat_addresses()
            
            return deployed_contracts
        except Exception as e:
            logger.error(f"Error getting deployed contracts: {e}")
            # In caso di errore, usa gli indirizzi predefiniti di Hardhat
            return self._get_default_hardhat_addresses()
    
    def _get_contract_name_from_code(self, address):
        """Tenta di determinare il nome del contratto dal suo bytecode"""
        # Questo è un metodo euristico che potrebbe non funzionare in tutti i casi
        # In una implementazione reale, dovresti usare un metodo più robusto
        try:
            # Ottieni il codice del contratto
            code = self.w3.eth.get_code(address)
            code_hex = code.hex()
            
            # Controlla se il codice contiene stringhe che possono indicare il nome del contratto
            contract_names = [
                "SustainableFoodChain"]
            
            for name in contract_names:
                # Converti il nome in esadecimale e cerca nel bytecode
                name_hex = name.encode('utf-8').hex()
                if name_hex in code_hex:
                    return name
            
            # Se non riesci a determinare il nome, usa l'indirizzo come chiave
            return f"Contract_{address[:8]}"
        except Exception as e:
            logger.error(f"Error getting contract name from code: {e}")
            return None
    
    def _get_default_hardhat_addresses(self):
        """Restituisce gli indirizzi predefiniti dei contratti in Hardhat"""
        # Questi sono gli indirizzi predefiniti dei primi contratti deployati in Hardhat
        # L'ordine dipende dall'ordine di deployment nello script deploy.js
        return {
            "SustainableFoodChain": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
        }

    def register_user(self, name: str, email: str, role: str) -> bool:
        """Registra un nuovo utente nel sistema"""
        try:
            tx_hash = self.contracts['UserRegistry'].functions.registerUser(
                name,
                email,
                role
            ).transact({'from': self.default_account})
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.status == 1
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    def get_user(self, address: str) -> Dict[str, Any]:
        """Ottiene le informazioni di un utente"""
        try:
            is_registered = self.contracts['UserRegistry'].functions.isUserRegistered(address).call()
            if not is_registered:
                return {}

            user = self.contracts['UserRegistry'].functions.getUser(address).call()
            return {
                'name': user[0],
                'email': user[1],
                'role': user[2],
                'isActive': user[3],
                'registrationDate': user[4]
            }
        except Exception as e:
            print(f"Error getting user info: {e}")
            return {}

    def create_product(self, name: str, description: str, category: str, unit: str, metadata: str = "") -> int:
        """Crea un nuovo prodotto nel sistema"""
        try:
            tx_hash = self.contracts['ProductRegistry'].functions.createProduct(
                name,
                description,
                category,
                unit,
                metadata
            ).transact({'from': self.default_account})
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 1:
                # Cerca l'evento ProductCreated per ottenere l'ID del prodotto
                event = self.contracts['ProductRegistry'].events.ProductCreated().process_receipt(receipt)[0]
                return event['args']['productId']
            return 0
        except Exception as e:
            print(f"Error creating product: {e}")
            return 0

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Ottiene le informazioni di un prodotto"""
        try:
            product = self.contracts['ProductRegistry'].functions.getProduct(product_id).call()
            return {
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'category': product[3],
                'unit': product[4],
                'producer': product[5],
                'createdAt': product[6],
                'isActive': product[7],
                'metadata': product[8]
            }
        except Exception as e:
            print(f"Error getting product: {e}")
            return {}

def main():
    # Esempio di utilizzo
    try:
        interactor = BlockchainInteractor()
        
        # Registrazione di un nuovo utente
        success = interactor.register_user(
            name="John Doe",
            email="john.doe@example.com",
            role="PRODUCER"
        )
        print(f"User registration {'successful' if success else 'failed'}")
        
        if success:
            # Verifica le informazioni dell'utente
            user_info = interactor.get_user(interactor.default_account)
            print(f"User info: {user_info}")
        
        # Registrazione di un nuovo prodotto
        product_id = interactor.create_product(
            name="Organic Apple",
            description="Fresh organic apples from local farms",
            category="Fruit",
            unit="kg"
        )
        
        if product_id > 0:
            print(f"Product created with ID: {product_id}")
            # Verifica le informazioni del prodotto
            product_info = interactor.get_product(product_id)
            print(f"Product info: {product_info}")
        else:
            print("Product creation failed")
        
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()