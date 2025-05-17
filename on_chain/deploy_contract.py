# deploy_contract.py - Compiles and deploys the contract on the blockchain.
from web3 import Web3
import json
import os
from solcx import compile_standard, install_solc
from typing import Dict, Any, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CONTRACTS_DIR = Path(__file__).parent / "contracts"
CONTRACT_ADDRESSES_FILE = Path(__file__).parent / "contract_addresses.json"
GANACHE_URL = "http://127.0.0.1:8545"

def compile_contracts() -> Dict[str, Any]:
    """
    Compiles all Solidity contracts in the contracts directory.
    Returns the compiled contract data.
    """
    try:
        # Install specific Solidity compiler version
        install_solc("0.8.0")
        
        contract_sources = {}
        compiled_contracts = {}
        
        # Read all .sol files in the contracts directory
        for contract_file in CONTRACTS_DIR.glob("*.sol"):
            with open(contract_file, "r", encoding="utf-8") as file:
                contract_name = contract_file.stem
                contract_sources[contract_name] = {"content": file.read()}
        
        # Compile all contracts
        for name, source in contract_sources.items():
            compiled = compile_standard(
                {
                    "language": "Solidity",
                    "sources": {f"{name}.sol": source},
                    "settings": {
                        "outputSelection": {
                            "*": {
                                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                            }
                        }
                    }
                },
                solc_version="0.8.0"
            )
            compiled_contracts[name] = compiled
            
        logger.info("Contracts compiled successfully")
        return compiled_contracts
    
    except Exception as e:
        logger.error(f"Error compiling contracts: {e}")
        return {}

def deploy_contracts(w3: Web3, compiled_contracts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploys compiled contracts to the blockchain.
    Returns information about deployed contracts.
    """
    try:
        deployed_contracts = {}
        account = w3.eth.accounts[0]  # Use the first account as deployer

        for contract_name, compiled in compiled_contracts.items():
            # Get contract data
            contract_data = compiled['contracts'][f"{contract_name}.sol"][contract_name]
            abi = contract_data['abi']
            bytecode = contract_data['evm']['bytecode']['object']

            # Create contract instance
            Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

            # Deploy contract
            tx_hash = Contract.constructor().transact({'from': account})
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            deployed_contracts[contract_name] = {
                'address': tx_receipt.contractAddress,
                'abi': abi
            }

            logger.info(f"Contract {contract_name} deployed to {tx_receipt.contractAddress}")

        return deployed_contracts

    except Exception as e:
        logger.error(f"Error deploying contracts: {e}")
        return {}

def save_contract_data(deployed_contracts: Dict[str, Any]) -> None:
    """
    Saves deployed contract addresses and ABIs to a JSON file.
    """
    try:
        with open(CONTRACT_ADDRESSES_FILE, 'w') as f:
            json.dump(deployed_contracts, f, indent=2)
        logger.info(f"Contract data saved to {CONTRACT_ADDRESSES_FILE}")
    except Exception as e:
        logger.error(f"Error saving contract data: {e}")

def main() -> None:
    """
    Main function to compile and deploy contracts.
    """
    try:
        # Connect to Ganache
        w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        if not w3.is_connected():
            raise ConnectionError("Could not connect to Ganache")

        # Compile contracts
        compiled_contracts = compile_contracts()
        if not compiled_contracts:
            raise Exception("No contracts compiled")

        # Deploy contracts
        deployed_contracts = deploy_contracts(w3, compiled_contracts)
        if not deployed_contracts:
            raise Exception("No contracts deployed")

        # Save contract data
        save_contract_data(deployed_contracts)
        
    except Exception as e:
        logger.error(f"Error in deployment process: {e}")
        raise

if __name__ == "__main__":
    main()