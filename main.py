from web3 import Web3
import json
from web3.middleware import geth_poa_middleware
from datetime import datetime
from dotenv import load_dotenv
import os
import constants as c
import psycopg2

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

# Define the block number to query
block_number = c.block_number  # add from and to block

# Define the filter parameters
filter_params = {
    "fromBlock": block_number,
    "toBlock": block_number,
    "address": contract_address,
    "topics": [event_signature_hash]
}


# Function to handle new events
def handle_event(event, conn, cur):
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
        #'Transaction 123',
        event['address'],
        event['blockHash'],
        event['blockNumber'],
        datetime.strptime(event['timestamp'], '%m/%d/%y %H:%M:%S')
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

# Fetch logs for the specified block
try:
    events = web3.eth.get_logs(filter_params)
    # print(f"Number of events found: {len(events)}")

    # Decode and print event data
    for event in events:
        # Decode the log data using the ABI of the contract       
        decoded_event = contract.events.UserOperationEvent().process_log(event)  
        block = web3.eth.get_block(event['blockNumber'])
        timestamp = block['timestamp']
        dt_object = datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime('%m/%d/%y %H:%M:%S')
        event_json = json.loads(web3.to_json(decoded_event))
        event_json["timestamp"] = formatted_time
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(event_json, f, ensure_ascii=False, indent=4)
        handle_event(event_json, conn, cur)

except ValueError as e:
    print(f"Error fetching logs: {e}")