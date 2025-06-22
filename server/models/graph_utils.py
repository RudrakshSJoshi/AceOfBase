# graph_utils.py
import sqlite3
import torch
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
from torch_geometric.data import Data

# Function to count 'f' in the first 6 characters of an address
def count_f_in_address(address):
    if address is None:
        return 0
    return address[:6].count('f')

# Function to convert timestamp to numerical value
def convert_timestamp(timestamp):
    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z").timestamp()
    except:
        return 0

# Function to calculate timestamp differences
def calculate_timestamp_differences(timestamps):
    timestamps = sorted([convert_timestamp(ts) for ts in timestamps if ts])
    if len(timestamps) < 2:
        return [0, 0, 0]
    differences = np.diff(timestamps)
    return [np.min(differences), np.mean(differences), np.max(differences)]

# Function to query address from database
def query_address_from_db(db_name, table_name, address_column, address):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name} WHERE {address_column} = ?"
        cursor.execute(query, (address,))
        result = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return [dict(zip(column_names, row)) for row in result]
    except Exception as e:
        print(f"Error while querying database {db_name}, table {table_name}: {e}")
        return []

# Function to find addresses associated with a given address
def find_addresses_for_given_address(address):
    results = {}
    try:
        results['transactions'] = {
            'FROM': query_address_from_db('data.db', 'transactions', 'FROM_ADDRESS', address),
            'TO': query_address_from_db('data.db', 'transactions', 'TO_ADDRESS', address)
        }
        results['dex_swaps'] = {
            'FROM': query_address_from_db('data.db', 'dex_swaps', 'ORIGIN_FROM_ADDRESS', address),
            'TO': query_address_from_db('data.db', 'dex_swaps', 'ORIGIN_TO_ADDRESS', address)
        }
        results['nft_transfers'] = {
            'FROM': query_address_from_db('data.db', 'nft_transfers', 'NFT_FROM_ADDRESS', address),
            'TO': query_address_from_db('data.db', 'nft_transfers', 'NFT_TO_ADDRESS', address)
        }
        results['token_transfers'] = {
            'FROM': query_address_from_db('data.db', 'token_transfers', 'ORIGIN_FROM_ADDRESS', address),
            'TO': query_address_from_db('data.db', 'token_transfers', 'ORIGIN_TO_ADDRESS', address)
        }
    except Exception as e:
        print(f"Error while searching for address {address}: {e}")
        return {}
    return results

# Function to load data from a dataset and construct graph
# Function to load data from a dataset and construct graph
def load_graph_data(df, db_name):
    counter = 0
    print("Loading graph data...")
    conn = sqlite3.connect(db_name)
    edges = []
    edge_features = []
    node_map = {}  # Maps address to node_index
    node_index = 0  # Tracks the current node index
    node_features = {}  # Stores features for each node
    timestamp_data = {category: [] for category in ['transactions', 'dex_swaps', 'nft_transfers', 'token_transfers']}
    node_degrees = {}  # To track if a node has at least one edge
    
    addresses = set(df['ADDRESS'])
    
    # First pass: collect all nodes that appear in edges
    for address in tqdm(addresses, desc="Processing addresses", unit="address"):
        counter += 1
        results = find_addresses_for_given_address(address)
        
        for category, directions in results.items():
            for direction, transactions in directions.items():
                for row in transactions:
                    src = row.get('FROM_ADDRESS') or row.get('ORIGIN_FROM_ADDRESS') or row.get('NFT_FROM_ADDRESS')
                    dst = row.get('TO_ADDRESS') or row.get('ORIGIN_TO_ADDRESS') or row.get('NFT_TO_ADDRESS')
                    
                    # Mark nodes as having edges
                    if src is not None:
                        node_degrees[src] = node_degrees.get(src, 0) + 1
                    if dst is not None:
                        node_degrees[dst] = node_degrees.get(dst, 0) + 1
    
    # Second pass: only process nodes that have at least one edge
    valid_nodes = set(node_degrees.keys())
    
    # Reset tracking variables
    node_map = {}
    node_index = 0
    node_features = {}
    edges = []
    edge_features = []
    
    for address in tqdm(addresses, desc="Building graph", unit="address"):
        if address not in valid_nodes:
            continue
            
        results = find_addresses_for_given_address(address)
        
        for category, directions in results.items():
            for direction, transactions in directions.items():
                for row in transactions:
                    src = row.get('FROM_ADDRESS') or row.get('ORIGIN_FROM_ADDRESS') or row.get('NFT_FROM_ADDRESS')
                    dst = row.get('TO_ADDRESS') or row.get('ORIGIN_TO_ADDRESS') or row.get('NFT_TO_ADDRESS')
                    
                    # Skip if either node isn't in our valid set
                    if src not in valid_nodes or dst not in valid_nodes:
                        continue
                        
                    value = float(row.get('VALUE_PRECISE', 0) or row.get('AMOUNT_PRECISE', 0) or 0)
                    timestamp = convert_timestamp(row['BLOCK_TIMESTAMP'])
                    timestamp_data[category].append(timestamp)
                    
                    # Handle source node
                    if src not in node_map:
                        node_map[src] = node_index
                        f_count_src = count_f_in_address(src)
                        node_features[node_index] = [0, 0, f_count_src*100]
                        node_index += 1

                    # Handle destination node
                    if dst not in node_map:
                        node_map[dst] = node_index
                        f_count_dst = count_f_in_address(dst)
                        node_features[node_index] = [0, 0, f_count_dst*100]
                        node_index += 1
                    
                    edges.append((node_map[src], node_map[dst]))
                    edge_features.append([value, timestamp])
                    
                    node_features[node_map[src]][0] += 1  # Out-degree count for src
                    node_features[node_map[dst]][1] += 1  # In-degree count for dst
    
    conn.close()
    
    # Calculate timestamp differences for each category
    extra_features = []
    for category in ['transactions', 'dex_swaps', 'nft_transfers', 'token_transfers']:
        extra_features.extend(calculate_timestamp_differences(timestamp_data[category]))
    
    if not edges:  # If no edges were found
        print("Warning: No edges found in the dataset!")
        return None, None
    
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    edge_attr = torch.tensor(edge_features, dtype=torch.float)
    x = torch.tensor(list(node_features.values()), dtype=torch.float)  # Node features
    
    # Append extra timestamp features to node features
    x = torch.cat([x, torch.tensor(extra_features * len(x), dtype=torch.float).view(len(x), -1)], dim=1)
    
    print(f"Graph data loaded successfully! Nodes: {len(node_map)}, Edges: {len(edges)}")
    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr), node_map