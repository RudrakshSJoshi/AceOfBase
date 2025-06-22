import sqlite3

# Function to query data from SQLite database
def query_address_from_db(db_name, table_name, address_column, address):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Query to find the records matching the address
        query = f"SELECT * FROM {table_name} WHERE {address_column} = ?"
        print(f"Executing query: {query} with address: {address}")
        
        # Execute the query with the address parameter
        cursor.execute(query, (address,))
        
        # Fetch all results
        result = cursor.fetchall()
        conn.close()
        
        print(f"Query completed successfully.")
        return result
    
    except Exception as e:
        print(f"Error while querying database {db_name}, table {table_name}: {e}")
        return []

# Function to save results to a text file
def save_results_to_file(filename, address, context, direction, results):
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f"Results for address: {address} ({context} - {direction})\n")
            if results:
                for row in results:
                    file.write(f"{row}\n")
            else:
                file.write("No results found.\n")
            file.write("\n" + "="*50 + "\n\n")
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error while saving results to file: {e}")

# Main function to search for address in the database and save results to a text file
def find_addresses_for_given_address(address):
    try:
        filename = "address_search_results.txt"
        
        # Open the file and write the header
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Searching for address: {address}\n")
            file.write("="*50 + "\n\n")

        # Transactions table
        print("\nSent FROM / TO in transactions:")
        trans_results = query_address_from_db('data.db', 'transactions', 'FROM_ADDRESS', address)
        save_results_to_file(filename, address, "transaction", "FROM", trans_results)

        trans_results_to = query_address_from_db('data.db', 'transactions', 'TO_ADDRESS', address)
        save_results_to_file(filename, address, "transaction", "TO", trans_results_to)

        # Dex swaps table
        print("\nSent FROM / TO in dex_swaps:")
        dex_results = query_address_from_db('data.db', 'dex_swaps', 'ORIGIN_FROM_ADDRESS', address)
        save_results_to_file(filename, address, "dex swap", "FROM", dex_results)

        dex_results_to = query_address_from_db('data.db', 'dex_swaps', 'ORIGIN_TO_ADDRESS', address)
        save_results_to_file(filename, address, "dex swap", "TO", dex_results_to)

        # NFT transfers table
        print("\nSent FROM / TO in nft_transfers:")
        nft_results = query_address_from_db('data.db', 'nft_transfers', 'NFT_FROM_ADDRESS', address)
        save_results_to_file(filename, address, "nft transfer", "FROM", nft_results)

        nft_results_to = query_address_from_db('data.db', 'nft_transfers', 'NFT_TO_ADDRESS', address)
        save_results_to_file(filename, address, "nft transfer", "TO", nft_results_to)

        # Tokens table (single table for all token transfers)
        print("\nSent FROM / TO in token transfers:")
        token_results = query_address_from_db('data.db', 'token_transfers', 'ORIGIN_FROM_ADDRESS', address)
        save_results_to_file(filename, address, "token transfer", "FROM", token_results)

        token_results_to = query_address_from_db('data.db', 'token_transfers', 'ORIGIN_TO_ADDRESS', address)
        save_results_to_file(filename, address, "token transfer", "TO", token_results_to)

    except Exception as e:
        print(f"Error while searching for address {address}: {e}")

# Example usage
address = "0xffd090eb6169f29890c08d5fb8f9bf1040e3bc21"
find_addresses_for_given_address(address)
