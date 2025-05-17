# interact_contract.py - Uses contract_addresses.json to call functions on the blockchain.

import json
import os
import time
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

        # Load contract addresses and ABIs
        contract_data_path = os.path.join(os.path.dirname(__file__), "contract_addresses.json")
        try:
            with open(contract_data_path, 'r') as f:
                self.contract_data = json.load(f)
                logger.info(f"Successfully loaded contract data from {contract_data_path}")
        except FileNotFoundError:
            logger.error(f"Contract data file not found at {contract_data_path}")
            # Try to look for the file in the parent directory
            alternative_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "on_chain", "contract_addresses.json")
            logger.info(f"Trying alternative path: {alternative_path}")
            try:
                with open(alternative_path, 'r') as f:
                    self.contract_data = json.load(f)
                    logger.info(f"Successfully loaded contract data from alternative path: {alternative_path}")
            except FileNotFoundError:
                logger.error(f"Contract data file not found at alternative path: {alternative_path}")
                raise Exception("Contract data file not found. Please deploy contracts first.")
        
        # Default account for transactions
        self.default_account = self.w3.eth.accounts[0]
        self.w3.eth.default_account = self.default_account
        
        # Initialize contracts
        self.contracts = {}
        for name, data in self.contract_data['contracts'].items():
            self.contracts[name] = self.w3.eth.contract(
                address=data['address'],
                abi=data['abi']
            )

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