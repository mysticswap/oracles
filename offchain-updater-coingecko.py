import subprocess
import time
import os
import requests
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables from .env file
load_dotenv()

# Set up web3 connection
w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))

# Contract ABI (only the function we need)
ABI = [
    {
        "inputs": [{"internalType": "int192", "name": "value", "type": "int192"}],
        "name": "transmit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def get_coingecko_price(coin_id, vs_currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[coin_id][vs_currency]
    else:
        raise Exception(f"Failed to fetch price data: {response.status_code}")

def transmit_value(value):
    # Convert the float value to uint192
    uint192_value = int(value * 10**8)  # Assuming 18 decimal places
    
    # Set up the contract
    contract_address = os.getenv('CONTRACT_ADDRESS')
    contract = w3.eth.contract(address=contract_address, abi=ABI)
    
    # Get the account from the private key
    account = Account.from_key(os.getenv('PRIVATE_KEY'))
    
    # Build the transaction
    transaction = contract.functions.transmit(uint192_value).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        # 'gas': 200000,  # Adjust as needed
        'gasPrice': w3.eth.gas_price,
    })
    
    # Sign the transaction
    signed_txn = account.sign_transaction(transaction)
    
    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Wait for the transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"Transaction successful. Hash: {tx_hash.hex()}")
    return tx_receipt

# def run_forge_script(value):
#     # Convert the float value to uint192
#     uint192_value = int(value * 10**18)  # Assuming 18 decimal places
#     print(uint192_value)

#     # Run the Forge script
#     try:
#         result = subprocess.run(
#             ['forge', 'script', 'scripts/Offchain.s.sol:TransmitScript', 
#              '--sig', 'run(uint192)', str(uint192_value),
#              '--rpc-url', os.getenv('RPC_URL'), 
#              '--broadcast'],
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         print(result.stdout)
#     except subprocess.CalledProcessError as e:
#         print(f"An error occurred: {e}")
#         print(e.stdout)
#         print(e.stderr)

def main():
    interval = int(os.getenv('UPDATE_INTERVAL', 3600))  # Default to 5 minutes if not set
    coin_id = os.getenv('COIN_ID', 'ethereum')
    vs_currency = os.getenv('VS_CURRENCY', 'usd')
    
    while True:
        try:
            print(f"Fetching price data at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            price = get_coingecko_price(coin_id, vs_currency)
            print(f"Current price of {coin_id} in {vs_currency}: {price}")
            
            print("Transmitting value to smart contract")
            receipt = transmit_value(price)
            print(f"Transaction mined in block {receipt['blockNumber']}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        
        print(f"Sleeping for {interval} seconds...")
        time.sleep(interval)

if __name__ == "__main__":
    main()