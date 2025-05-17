import subprocess
import json
import time
import os
from web3 import Web3
import sys

# Import logger from off_chain configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from off_chain.configuration.log_load_setting import logger

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
        
        # Start the Hardhat node
        logger.info("Starting Hardhat node...")
        process = subprocess.Popen(
            ["npx", "hardhat", "node"],
            cwd=on_chain_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # Wait a bit for the node to start
        time.sleep(5)
        
        # Check if the process is still running
        if process.poll() is not None:
            stderr = process.stderr.read()
            logger.error(f"Hardhat node failed to start: {stderr}")
            return False
        
        logger.info("Hardhat node started successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error starting Hardhat node: {str(e)}")
        return False

def deploy_contracts():
    """Deploy contracts using Hardhat"""
    try:
        # Get the project root directory
        on_chain_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Run the deployment script
        logger.info("Deploying contracts with Hardhat...")
        result = subprocess.run(
            ["npx", "hardhat", "run", "scripts/deploy.js", "--network", "localhost"],
            cwd=on_chain_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Contract deployment failed: {result.stderr}")
            return False
        
        logger.info(f"Contract deployment output: {result.stdout}")
        return True
        
    except Exception as e:
        logger.error(f"Error deploying contracts: {str(e)}")
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

def main():
    try:
        # Start Hardhat node
        logger.info("Starting blockchain services...")
        if not start_hardhat_node():
            raise Exception("Failed to start and connect to Hardhat node")
        
        # Connect to Hardhat node
        logger.info("Connecting to Hardhat node...")
        max_attempts = 30
        w3 = None
        for i in range(max_attempts):
            try:
                w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
                if w3.is_connected():
                    break
            except Exception as e:
                if i == max_attempts - 1:
                    raise Exception(f"Failed to connect to Hardhat node: {str(e)}")
                time.sleep(1)
        
        # Wait for node to be fully ready
        if not wait_for_node(w3, max_attempts=30):
            raise Exception("Failed to connect to Hardhat node")
        
        # Deploy contracts
        logger.info("Deploying contracts...")
        if not deploy_contracts():
            raise Exception("Failed to deploy contracts")
        
        logger.info("Deployment completed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error during deployment: {str(e)}")
        return False

if __name__ == "__main__":
    main()
