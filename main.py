from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
from datetime import datetime
from dotenv import load_dotenv
import os
import constants as c
import psycopg2
import time

# Load the .env file
load_dotenv()

# Connect to the Polygon or Base Mainnet node
web3 = Web3(Web3.HTTPProvider(c.polygon_url + os.getenv('API_KEY')))

# Check if connected
if not web3.is_connected():
    raise Exception("Failed to connect to the blockchain node")

# Apply PoA middleware if connected to a PoA network
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# EntryPoint contract address
contract_address = web3.to_checksum_address(c.contract_address)

# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=c.contract_abi["result"])

# PostgreSQL connection string
connection_string = os.getenv('CONNECTION_STRING')

# Define the event signature
event_signature = c.event_signature
event_signature_hash = Web3.keccak(text=event_signature).hex()


# Function to handle new events
def store_event(event, conn, cur):
    query = """
        INSERT INTO public.blockchain_tracker (user_op_hash,sender,paymaster,nonce,success,actual_gas_cost,actual_gas_used,event_name,transaction_index,transaction_hash,address,block_hash,block_number,timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (event_name, transaction_hash) DO NOTHING;
    """
    values = (
        event['args']['userOpHash'],
        event['args']['sender'],
        event['args']['paymaster'],
        event['args']['nonce'],
        event['args']['success'],
        event['args']['actualGasCost'],
        event['args']['actualGasUsed'],
        event['event'],
        event['transactionIndex'],
        event['transactionHash'],
        event['address'],
        event['blockHash'],
        event['blockNumber'],
        event['timestamp']
    )

    try:
        cur.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()

# Connect to the PostgreSQL database
conn = psycopg2.connect(connection_string)
print("Successful connection")
cur = conn.cursor()


def get_latest_blocks(contract_address, web3):
    latest_block = web3.eth.block_number
    current_time = time.time()
    time_limit = current_time - 60 # last minute
    blocks = []

    for block_number in range(latest_block, 0, -1):
        block = web3.eth.get_block(block_number, full_transactions=True)
        block_time = block.timestamp

        if block_time < time_limit:
            break

        for tx in block.transactions:
            if tx.to and tx.to.lower() == contract_address.lower():
                blocks.append(block)
                break

    return blocks

def get_from_to_blocks(blocks_arr):

    from_block = min(block.number for block in blocks_arr)
    to_block = max(block.number for block in blocks_arr)

    return from_block, to_block


def get_user_operations():

    blocks = get_latest_blocks(c.contract_address, web3)
    from_block, to_block = get_from_to_blocks(blocks)    
    filter_params = {
        "fromBlock": from_block,
        "toBlock": to_block,
        "address": contract_address,
        "topics": [event_signature_hash]
    }

    try:
        events = web3.eth.get_logs(filter_params)
        print(f"Number of events found: {len(events)}")
        for event in events:
            # Decode the log data using the ABI of the contract       
            decoded_event = contract.events.UserOperationEvent().process_log(event)              
            block = web3.eth.get_block(event['blockNumber'])
            event_json = json.loads(web3.to_json(decoded_event))
            event_json["timestamp"] = block['timestamp']

            #store_event(event_json, conn, cur)


    except ValueError as e:
        print(f"Error fetching logs: {e}")

get_user_operations()
