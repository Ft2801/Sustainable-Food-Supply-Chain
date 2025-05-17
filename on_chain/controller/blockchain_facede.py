import os
import random
from colorama import init
from web3 import Web3
from solcx import compile_standard, get_installed_solc_versions, install_solc

class BlockchainDeployController:
    """
    DeployController handles initialization, compilation and deployment for Solidity contract, establishing 
    a connection with Ganache through Web3.
    """

    init(convert=True)

    def __init__(self):
        """
        Initializes the deployment controller with Ethereum HTTP provider and Solidity 
        compiler version.
        
        """
        
        self.http_provider = 'http://ganache:8545'
        self.solc_version = '0.8.0'
        try:
            # Check if the HTTP provider is reachable
            self.w3 : Web3 = Web3(Web3.HTTPProvider(self.http_provider))
            if not self.w3.isConnected():
                raise ConnectionError("Unable to connect to the Ethereum network.")
        except Exception as e:
            self.w3 = None
        self.contract = None

    def compile_and_deploy(self, contract_source_path, account=None):
        """
        Compiles and deploys a smart contract to an Ethereum network.
        
        Args:
            contract_source_path (str): Path to the Solidity contract source file.
            account (str): The Ethereum account to deploy from (randomly chosen if not provided).
        """
        # Resolve the full path of the contract source file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        shared_dir_path = os.path.dirname(os.path.dirname(dir_path))
        contract_full_path = os.path.normpath(os.path.join(shared_dir_path, contract_source_path))

        # Read the Solidity source code from file
        with open(contract_full_path, 'r') as file:
            contract_source_code = file.read()

        # Compile the contract and then deploy it
        self.compile_contract(contract_source_code)
        account = random.choice(self.w3.eth.accounts)
        self.deploy_contract(account)

    def compile_contract(self, solidity_source):
        """
        Compiles a Solidity contract using the specified version of solc.
        
        Args:
            solidity_source (str): The source code of the Solidity contract.
        """
        # Install solc version if not already installed
        if self.solc_version not in get_installed_solc_versions():
            install_solc(self.solc_version)

        # Compile the Solidity source code
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {"on_chain/HealthCareRecords.sol": {"content": solidity_source}},
            "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
        }, solc_version=self.solc_version)

        # Extract the ABI and bytecode
        self.contract_id, self.contract_interface = next(iter(compiled_sol['contracts']['on_chain/HealthCareRecords.sol'].items()))
        self.abi = self.contract_interface['abi']
        self.bytecode = self.contract_interface['evm']['bytecode']['object']

    def deploy_contract(self, account):
        """
        Deploys the compiled contract using the provided account.
        
        Args:
            account (str): The account to deploy the contract from.
        """
        try:
            # Create the contract in Web3
            contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)

             # Send transaction to deploy the contract
            tx_hash = contract.constructor().transact({'from': account})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.contract = self.w3.eth.contract(address=tx_receipt.contractAddress, abi=self.abi)
            logger.info(f"Contract deployed at address: {tx_receipt.contractAddress}")
        except Exception as e:
            raise e
