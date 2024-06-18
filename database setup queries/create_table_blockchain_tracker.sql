CREATE TABLE blockchain_tracker(
id SERIAL PRIMARY KEY,
user_op_hash text not null, 
sender text NOT NULL, 
paymaster text,
nonce INTEGER,
success bool,
actual_gas_cost decimal,
actual_gas_used decimal,
event_name text not null,
transaction_index text not null,
transaction_hash text not null,
address text not null,
from_address text not null,
block_hash text not null,
block_number INTEGER not null,
timestamp INTEGER,
UNIQUE (user_op_hash, transaction_hash)
);