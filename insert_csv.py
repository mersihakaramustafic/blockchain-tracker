import csv
import psycopg2
import os
from dotenv import load_dotenv
import constants

load_dotenv()

csv_file_path = './ERC4337.csv'
data = []

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    header = next(reader) 
    for row in reader:
        data.append(row)

connection_string = os.getenv('CONNECTION_STRING')
db_connection = psycopg2.connect(connection_string)
db_connection_cursor = db_connection.cursor()

table_name = constants.table_name
columns = ', '.join(header)
placeholders = ', '.join(['%s'] * len(header))
insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

try:
    for row in data:
        db_connection_cursor.execute(insert_query, row)

    db_connection.commit()  
    
except Exception as e:
    db_connection.rollback() 
    print(f"An error occurred: {e}")

finally:
    db_connection_cursor.close()
    db_connection.close()