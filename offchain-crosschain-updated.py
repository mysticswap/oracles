import time
import os
import requests
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables from .env file
load_dotenv()

# Set up web3 connections for both chains
source_w3 = Web3(Web3.HTTPProvider(os.getenv('SOURCE_RPC_URL')))
target_w3 = Web3(Web3.HTTPProvider(os.getenv('TARGET_RPC_URL')))

# Source Oracle ABI (for reading price)
SOURCE_ORACLE_ABI = [
    {
        "inputs": [],
        "name": "latestAnswer",
        "outputs": [{"internalType": "int256", "name": "", "type": "int256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Target Oracle ABI (for transmitting price)
TARGET_ORACLE_ABI = [
    {
        "inputs": [{"internalType": "int192", "name": "value", "type": "int192"}],
        "name": "transmit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def get_source_oracle_price():
    # Set up the contract
    source_contract_address = os.getenv('SOURCE_ORACLE_ADDRESS')
    source_contract = source_w3.eth.contract(address=source_contract_address, abi=SOURCE_ORACLE_ABI)
    
    # Get the price and decimals
    price = source_contract.functions.latestAnswer().call()
    decimals = source_contract.functions.decimals().call()
    
    # Convert to float
    normalized_price = float(price) / (10 ** decimals)
    print('norm price',normalized_price)
    return normalized_price

def transmit_value(value):
    # Set up the contract
    contract_address = os.getenv('TARGET_ORACLE_ADDRESS')
    contract = target_w3.eth.contract(address=contract_address, abi=TARGET_ORACLE_ABI)
    
    # Get the account from the private key
    account = Account.from_key(os.getenv('PRIVATE_KEY'))
    
    # Build the transaction
    decimals = contract.functions.decimals().call()

    # Convert the float value to int192
    # Adjust decimals as needed for your target oracle
    int192_value = int(value * 10**decimals)  

    transaction = contract.functions.transmit(int192_value).build_transaction({
        'from': account.address,
        'nonce': target_w3.eth.get_transaction_count(account.address),
        'gasPrice': target_w3.eth.gas_price,
    })
    
    # Sign the transaction
    signed_txn = account.sign_transaction(transaction)
    
    # Send the transaction
    tx_hash = target_w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Wait for the transaction receipt
    tx_receipt = target_w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Transaction successful. Hash: {tx_hash.hex()}")
    return tx_receipt

def main():
    
    interval = int(os.getenv('UPDATE_INTERVAL', 3600))  # Default to 1 hour if not set
    
    while True:
        try:
            print(f"Fetching price data at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            price = get_source_oracle_price()
            print(f"Current price from source oracle: {price}")
            
            print("Transmitting value to target oracle")
            receipt = transmit_value(price)
            print(f"Transaction mined in block {receipt['blockNumber']}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        
        print(f"Sleeping for {interval} seconds...")
        time.sleep(interval)

if __name__ == "__main__":
    print('price updater is live')
    main()