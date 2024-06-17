def store_event(event, db_connection, db_connection_cursor):
    query = """
        INSERT INTO public.blockchain_tracker (user_op_hash,sender,paymaster,nonce,success,actual_gas_cost,actual_gas_used,event_name,transaction_index,transaction_hash,address,from_address,block_hash,block_number,timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
        ON CONFLICT (user_op_hash, transaction_hash) DO NOTHING;
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
        event['fromAddress'],
        event['blockHash'],
        event['blockNumber'],
        event['timestamp']
    )

    try:
        db_connection_cursor.execute(query, values)
        db_connection.commit()
    except Exception as e:
        db_connection.rollback()