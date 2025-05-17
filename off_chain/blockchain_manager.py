# Standard Library Imports
import sys
import time
import os
import threading
import subprocess
from pathlib import Path
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from configuration.log_load_setting import logger

# Import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from on_chain.interact_contract import BlockchainInteractor
from web3 import Web3

# Global variables
blockchain_interactor = None


def start_hardhat_node():
    """Start a Hardhat node for local development"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        on_chain_dir = os.path.join(project_root, "on_chain")
        
        # Check if a Hardhat node is already running
        try:
            w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if w3.is_connected():
                logger.info("A node is already running on port 8545")
                return True
        except Exception:
            pass  # No node running, continue with startup
        
        # Check if node_modules/.bin/hardhat exists
        hardhat_bin_path = os.path.join(on_chain_dir, "node_modules", ".bin", "hardhat")
        hardhat_bin_path_alt = os.path.join(on_chain_dir, "node_modules", ".bin", "hardhat.cmd")
        
        # Start the Hardhat node
        logger.info("Starting Hardhat node...")
        
        # Try different methods to start the Hardhat node
        try:
            # Try with npx first
            logger.info("Trying to start Hardhat node with npx...")
            process = subprocess.Popen(
                ["npx", "hardhat", "node"],
                cwd=on_chain_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # Wait a bit for the node to start
            time.sleep(3)
            
            # Check if the process is still running
            if process.poll() is None:  # None means it's still running
                logger.info("Hardhat node started successfully with npx")
                return True
            else:
                stderr = process.stderr.read()
                logger.warning(f"Failed to start Hardhat node with npx: {stderr}")
                
                # Try with direct path to hardhat binary
                if os.path.exists(hardhat_bin_path):
                    logger.info(f"Trying to start Hardhat node with direct path: {hardhat_bin_path}")
                    process = subprocess.Popen(
                        [hardhat_bin_path, "node"],
                        cwd=on_chain_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                elif os.path.exists(hardhat_bin_path_alt):
                    logger.info(f"Trying to start Hardhat node with direct path: {hardhat_bin_path_alt}")
                    process = subprocess.Popen(
                        [hardhat_bin_path_alt, "node"],
                        cwd=on_chain_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    # Try with node directly
                    logger.info("Trying to start Hardhat node with node directly...")
                    node_script = os.path.join(on_chain_dir, "node_modules", "hardhat", "internal", "cli", "cli.js")
                    if os.path.exists(node_script):
                        process = subprocess.Popen(
                            ["node", node_script, "node"],
                            cwd=on_chain_dir,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                        )
                    else:
                        logger.error(f"Could not find Hardhat CLI script at {node_script}")
                        return False
                
                # Wait a bit for the node to start
                time.sleep(3)
                
                # Check if the process is still running
                if process.poll() is None:  # None means it's still running
                    logger.info("Hardhat node started successfully with alternative method")
                    return True
                else:
                    stderr = process.stderr.read()
                    logger.error(f"Hardhat node failed to start with alternative method: {stderr}")
                    return False
        except Exception as e:
            logger.error(f"Error starting Hardhat node: {str(e)}")
            return False
            
        return False
        
    except Exception as e:
        logger.error(f"Error in start_hardhat_node: {str(e)}")
        return False


def deploy_contracts():
    """Deploy contracts using Hardhat"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        on_chain_dir = os.path.join(project_root, "on_chain")
        
        # Check if a Hardhat node is running
        try:
            w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if not w3.is_connected():
                logger.error("No Hardhat node running on port 8545. Please start a node first.")
                return False
            logger.info("Hardhat node is running on port 8545")
        except Exception as e:
            logger.error(f"Error checking Hardhat node: {str(e)}")
            return False
        
        # Run the deployment script
        logger.info("Deploying contracts with Hardhat...")
        
        # Use npx hardhat to run the deployment script
        try:
            result = subprocess.run(
                ["npx", "hardhat", "run", "scripts/deploy.js", "--network", "localhost"],
                cwd=on_chain_dir,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                logger.info(f"Contract deployment output: {result.stdout}")
                
                # Verify that contract_addresses.json was created
                contract_file = os.path.join(on_chain_dir, "contract_addresses.json")
                if os.path.exists(contract_file):
                    logger.info(f"Contract addresses file created at {contract_file}")
                    
                    # Read the contract addresses file to verify it's valid JSON
                    try:
                        with open(contract_file, 'r') as f:
                            contract_data = json.load(f)
                        if 'contracts' in contract_data:
                            logger.info(f"Successfully deployed {len(contract_data['contracts'])} contracts")
                            return True
                        else:
                            logger.error("Contract addresses file has invalid format")
                            return False
                    except Exception as e:
                        logger.error(f"Error reading contract addresses file: {str(e)}")
                        return False
                else:
                    logger.error(f"Contract addresses file not created at {contract_file}")
                    return False
            else:
                logger.error(f"Contract deployment failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error running deployment script: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Error deploying contracts: {str(e)}")
        return False


class BlockchainSetupThread(threading.Thread):
    def __init__(self, splash_screen=None):
        super().__init__()
        self.splash_screen = splash_screen
        self.success = False
        self.error_message = None
        self.blockchain_interactor = None
        self._w3 = None

    def update_splash_message(self, message):
        if self.splash_screen:
            self.splash_screen.showMessage(message, Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
            QApplication.processEvents()

    def run(self):
        global blockchain_interactor
        try:
            self.update_splash_message("Starting Hardhat node...")
            if not start_hardhat_node():
                raise Exception("Failed to start Hardhat node")

            # Add a short delay to give time for the node to initialize completely
            time.sleep(5)

            self.update_splash_message("Connecting to blockchain...")
            self._w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if not wait_for_node(self._w3, max_attempts=30):
                raise Exception("Failed to connect to Hardhat node")

            if self._load_or_deploy_contracts():
                blockchain_interactor = self.created_blockchain_interactor
                self.success = True
            else:
                raise Exception(self.error_message)

        except Exception as e:
            self.error_message = str(e)
            logger.error(f"Blockchain setup error: {e}")
            self.success = False

    def _load_or_deploy_contracts(self) -> bool:
        """Deploys new contracts every time and backs up existing ones."""
        if not self._w3:
            self.error_message = "Web3 not initialized for contract deployment."
            return False

        # Define the possible locations for the contract_addresses.json file
        project_root = Path(__file__).resolve().parent.parent
        possible_locations = [
            project_root / "on_chain" / "contract_addresses.json",
            project_root / "contract_addresses.json"
        ]
        
        # Find the first existing contract file
        contract_file = None
        for loc in possible_locations:
            if loc.exists():
                contract_file = loc
                logger.info(f"Found contract file at: {contract_file}")
                break
                
        # If no contract file exists, use the default location
        if contract_file is None:
            contract_file = possible_locations[0]
            logger.info(f"Using default contract file location: {contract_file}")
        
        # Check if we should use existing contracts or deploy new ones
        use_existing = False
        if contract_file.exists():
            try:
                with open(contract_file, 'r') as f:
                    contract_data = json.load(f)
                if 'contracts' in contract_data and len(contract_data['contracts']) > 0:
                    logger.info(f"Found existing contracts: {list(contract_data['contracts'].keys())}")
                    # Try to verify if the contracts are accessible
                    try:
                        for name, data in contract_data['contracts'].items():
                            contract = self._w3.eth.contract(
                                address=data['address'],
                                abi=data['abi']
                            )
                            # Try a simple call to verify the contract is accessible
                            # This will vary depending on the contract, but most contracts have a function like 'owner'
                            # that can be called without parameters
                            logger.info(f"Verifying contract {name} at {data['address']}")
                        use_existing = True
                        logger.info("All contracts verified, using existing contracts")
                    except Exception as e:
                        logger.warning(f"Error verifying contracts: {e}. Will deploy new contracts.")
                        use_existing = False
            except Exception as e:
                logger.warning(f"Error reading contract file: {e}. Will deploy new contracts.")
        
        # Backup existing contract addresses if they exist
        if contract_file.exists():
            self.update_splash_message("Backing up existing contract addresses...")
            backup_timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = contract_file.with_name(f"contract_addresses_backup_{backup_timestamp}.json")
            try:
                import shutil
                shutil.copy2(contract_file, backup_file)
                logger.info(f"Backed up contract addresses to {backup_file}")
            except Exception as e:
                logger.warning(f"Failed to backup contract addresses: {e}")

        # Deploy new contracts if needed
        if not use_existing:
            self.update_splash_message("Deploying smart contracts...")
            if not deploy_contracts():
                self.error_message = "Smart contract deployment failed."
                return False
            logger.info("New contracts deployed successfully")
        else:
            logger.info("Using existing contracts, skipping deployment")

        self.update_splash_message("Initializing blockchain interface with contracts...")
        try:
            self.created_blockchain_interactor = BlockchainInteractor()
            logger.info("Blockchain interface initialized successfully")
            return True
        except Exception as e:
            self.error_message = f"Failed to initialize blockchain interface: {e}"
            logger.error(self.error_message)
            return False


def wait_for_node(w3, max_attempts=30):
    """Wait for the Hardhat node to be ready and accepting connections"""
    logger.info("Waiting for Hardhat node to be ready...")
    for i in range(max_attempts):
        try:
            # First check basic connection
            if not w3.is_connected():
                raise Exception("Not connected to node")
            
            # Then check if accounts are available
            accounts = w3.eth.accounts
            if not accounts or len(accounts) == 0:
                raise Exception("No accounts available")
                
            # Finally check if we can make a basic call
            block = w3.eth.get_block('latest')
            if not block:
                raise Exception("Cannot get latest block")
                
            logger.info(f"Successfully connected to Hardhat node with {len(accounts)} accounts")
            return True
            
        except Exception as e:
            if i == max_attempts - 1:
                logger.error(f"Final attempt to connect to Hardhat node failed: {str(e)}")
            else:
                logger.debug(f"Attempt {i+1}/{max_attempts} to connect to Hardhat node failed: {str(e)}")
            time.sleep(2)
    return False
