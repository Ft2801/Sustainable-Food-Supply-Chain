from web3 import Web3
import json
import time
import os

# Wait for Ganache and Truffle to be ready
time.sleep(10)

# Use environment variable to determine if running in Docker
GANACHE_HOST = os.getenv("GANACHE_HOST", "localhost")
w3 = Web3(Web3.HTTPProvider(f"http://{GANACHE_HOST}:8545"))
assert w3.is_connected(), "Error: Not connected to Ganache"

# Determine the correct path based on environment
CONTRACT_PATH = os.getenv("CONTRACT_PATH", "build/contracts/Counter.json")
with open(CONTRACT_PATH) as f:
    contract_json = json.load(f)

abi = contract_json["abi"]
networks = contract_json["networks"]
network_id = list(networks.keys())[0]  # Get the first deployed network
address = networks[network_id]["address"]

contract = w3.eth.contract(address=address, abi=abi)
account = w3.eth.accounts[0]
w3.eth.default_account = account

# Send transaction
print("Incrementing counter...")
tx_hash = contract.functions.increment().transact()
w3.eth.wait_for_transaction_receipt(tx_hash)

# Read counter value
count = contract.functions.getCount().call()
print(f"Counter value: {count}")
