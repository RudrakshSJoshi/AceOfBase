import os
import csv
import sqlite3

# Increase the maximum field size limit
csv.field_size_limit(10000000)  # Set to a larger value (e.g., 1,000,000 bytes)

# Function to read data from a CSV and create a table in SQLite
def create_table_from_csv(db_name, table_name, csv_file_path):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        print(f"Creating table {table_name} in {db_name} from CSV: {csv_file_path}")
        
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            headers = reader.fieldnames
            
            # Create table dynamically using CSV headers as column names
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{header} TEXT' for header in headers])});"
            print(f"Executing SQL: {create_table_query}")
            cursor.execute(create_table_query)
            
            # Insert data into the table
            insert_query = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({', '.join(['?'] * len(headers))});"
            print(f"Preparing insert query: {insert_query}")
            
            for row in reader:
                cursor.execute(insert_query, [row[header] for header in headers])
        
        conn.commit()
        conn.close()
        print(f"Table {table_name} created and data inserted successfully!")
    
    except Exception as e:
        print(f"Error while creating table from CSV {csv_file_path}: {e}")

# Function to create index on specific columns
def create_index(db_name, table_name, column_names):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        print(f"Creating index for columns {column_names} in table {table_name}")
        
        # Create index for each column
        for column in column_names:
            index_name = f"{table_name}_{column}_idx"
            print(f"Executing SQL: CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column});")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column});")
        
        conn.commit()
        conn.close()
        print(f"Indexes created for columns {column_names} in table {table_name}")
    
    except Exception as e:
        print(f"Error while creating index in table {table_name}: {e}")

# Function to process all CSV files in the directory for token transfers (with a single table)
def create_tokens_table_from_directory(db_name, table_name, directory_path):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        print(f"Processing token transfer CSV files in directory: {directory_path}")
        
        # Process each CSV file in the directory
        for filename in os.listdir(directory_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(directory_path, filename)
                
                print(f"Processing file: {filename}")
                
                # Create table for the CSV file (if it doesn't exist)
                create_table_from_csv(db_name, table_name, file_path)
        
        # Create indexes on commonly queried columns (e.g., FROM_ADDRESS and TO_ADDRESS)
        create_index(db_name, table_name, ['ORIGIN_FROM_ADDRESS', 'ORIGIN_TO_ADDRESS'])
        
        conn.close()
        print(f"Token transfer data from directory {directory_path} has been added to {table_name} table")
    
    except Exception as e:
        print(f"Error while creating tokens table: {e}")

# Function to create all tables from CSV files into one database
def create_single_db_from_csv():
    try:
        if os.path.exists('data.db'):
            print("Database 'data.db' already exists. Exiting without creating the database.")
            return  # Exit the function if the database already exists
        
        print("Starting database creation...")
        
        # Directories for CSV files
        transactions_file = 'Data/transactions.csv'
        dex_swaps_file = 'Data/dex_swaps.csv'
        nft_transfers_file = 'Data/nft_transfers.csv'
        token_transfers_dir = 'Data/token transfers'
        
        print("Creating SQLite database with multiple tables from CSV files...")
        
        # Create a single SQLite database and insert data into tables
        db_name = 'data.db'  # Single database for all data
        
        # Create and populate the tables with CSV data
        create_table_from_csv(db_name, 'transactions', transactions_file)
        create_index(db_name, 'transactions', ['FROM_ADDRESS', 'TO_ADDRESS'])

        create_table_from_csv(db_name, 'dex_swaps', dex_swaps_file)
        create_index(db_name, 'dex_swaps', ['ORIGIN_FROM_ADDRESS', 'ORIGIN_TO_ADDRESS'])

        create_table_from_csv(db_name, 'nft_transfers', nft_transfers_file)
        create_index(db_name, 'nft_transfers', ['NFT_FROM_ADDRESS', 'NFT_TO_ADDRESS'])

        # Create the tokens table by reading all files from the 'token transfers' directory
        create_tokens_table_from_directory(db_name, 'token_transfers', token_transfers_dir)
        
        print("Database creation completed successfully.")
    
    except Exception as e:
        print(f"Error while creating the database: {e}")

# Function to query data from SQLite database
def query_address_from_db(db_name, table_name, address_column, address):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        query = f"SELECT * FROM {table_name} WHERE {address_column} = ?"
        print(f"Executing query: {query} with address: {address}")
        
        cursor.execute(query, (address,))
        
        result = cursor.fetchall()
        conn.close()
        
        print(f"Query completed successfully.")
        return result
    
    except Exception as e:
        print(f"Error while querying database {db_name}, table {table_name}: {e}")
        return []

# Main function to search for address in the database
def find_addresses_for_given_address(address):
    try:
        print(f"Searching for the address: {address}")
        
        # Transactions table
        print("\nSent FROM / TO in transactions:")
        trans_results = query_address_from_db('data.db', 'transactions', 'FROM_ADDRESS', address)
        for row in trans_results:
            print(row)

        # Dex swaps table
        print("\nSent FROM / TO in dex_swaps:")
        dex_results = query_address_from_db('data.db', 'dex_swaps', 'ORIGIN_FROM_ADDRESS', address)
        for row in dex_results:
            print(row)

        # NFT transfers table
        print("\nSent FROM / TO in nft_transfers:")
        nft_results = query_address_from_db('data.db', 'nft_transfers', 'NFT_FROM_ADDRESS', address)
        for row in nft_results:
            print(row)

        # Tokens table (single table for all token transfers)
        print("\nSent FROM / TO in token transfers:")
        token_results = query_address_from_db('data.db', 'token_transfers', 'ORIGIN_FROM_ADDRESS', address)
        for row in token_results:
            print(row)

    except Exception as e:
        print(f"Error while searching for address {address}: {e}")