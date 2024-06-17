import json
import time
import os
import psycopg2
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
from helpers import store_event
import constants

load_dotenv()

def connect_to_mainnet():
    try:
        # Connect to the Polygon or Base Mainnet node
        web3 = Web3(Web3.HTTPProvider(constants.polygon_url + os.getenv('INFURA_API_KEY')))

        if not web3.is_connected():
            raise Exception("Failed to connect to the blockchain node")
        
        # Apply PoA middleware if connected to a PoA network
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return web3

    except ValueError as e:
        print(f"Error connecting to the blockchain node: {e}") 

def open_connection_to_psql():
    
    connection_string = os.getenv('PSQL_CONNECTION_STRING')
    db_connection = psycopg2.connect(connection_string)
    db_connection_cursor = db_connection.cursor()

    return db_connection, db_connection_cursor

def get_latest_blocks(contract_address, web3):
    latest_block = web3.eth.block_number
    current_time = time.time()
    time_limit = current_time - 720 # last 12 minutes
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

    web3 = connect_to_mainnet()
    db_connection, db_connection_cursor = open_connection_to_psql()
    contract_address_check_sum = web3.to_checksum_address(constants.contract_address)
    contract = web3.eth.contract(address=contract_address_check_sum, abi=constants.contract_abi["result"])
    blocks = get_latest_blocks(contract_address_check_sum, web3)
    from_block, to_block = get_from_to_blocks(blocks)    
    filter_params = {
        "fromBlock": from_block,
        "toBlock": to_block,
        "address": contract_address_check_sum,
        "topics": [Web3.keccak(text=constants.event_signature).hex()]
    }

    try:
        events = web3.eth.get_logs(filter_params)
        print(f"Number of events found: {len(events)}")
        for event in events:    
            decoded_event = contract.events.UserOperationEvent().process_log(event)              
            block = web3.eth.get_block(event['blockNumber'])
            event_json = json.loads(web3.to_json(decoded_event))
            event_json["timestamp"] = block['timestamp']
            transaction = web3.eth.get_transaction(event_json["transactionHash"])
            event_json["fromAddress"] = transaction['from']
            store_event(event_json, db_connection, db_connection_cursor)


    except ValueError as e:
        print(f"Error fetching logs: {e}")

get_user_operations()
