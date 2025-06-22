import requests
import pandas as pd
import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, GATConv
from torch_geometric.utils import add_self_loops
from tqdm import tqdm
import numpy as np
from models.graph_utils import load_graph_data
from datetime import datetime

# Corrected Model definition with proper dimensions
class EnhancedFraudGNN(torch.nn.Module):
    def __init__(self, in_channels=15, hidden_channels=512, out_channels=1, heads=4):
        super(EnhancedFraudGNN, self).__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = GATConv(hidden_channels, hidden_channels, heads=heads, concat=True)
        self.conv3 = SAGEConv(hidden_channels * heads, hidden_channels)
        self.conv4 = GATConv(hidden_channels, out_channels, heads=1, concat=False)

    def forward(self, x, edge_index, edge_attr=None):
        edge_index, _ = add_self_loops(edge_index, num_nodes=x.size(0))
        x = self.conv1(x, edge_index)
        x = F.leaky_relu(x, negative_slope=0.01)
        x = self.conv2(x, edge_index)
        x = F.leaky_relu(x, negative_slope=0.01)
        x = self.conv3(x, edge_index)
        x = F.leaky_relu(x, negative_slope=0.01)
        x = self.conv4(x, edge_index)
        return torch.sigmoid(x).squeeze()

# Configuration
API_KEY = os.getenv("BASESCAN_API_KEY")
BASESCAN_API_URL = "https://api.basescan.org/api"
MODEL_PATH = "fraud_gnn_final.pth"

def load_model():
    """Load the trained GNN model with correct architecture"""
    # Using the dimensions we discovered from the error messages
    model = EnhancedFraudGNN(in_channels=15, hidden_channels=512, out_channels=1, heads=4)
    
    # Load the state dict
    state_dict = torch.load(MODEL_PATH)
    
    # Handle potential CUDA/CPU device mismatch
    if not torch.cuda.is_available():
        state_dict = {k: v.to('cpu') for k, v in state_dict.items()}
    
    model.load_state_dict(state_dict)
    model.eval()
    return model

def fetch_all_transactions(address):
    """Fetch all transaction types for an address"""
    tx_types = [
        "txlist",        # Normal transactions
        "tokentx",       # Token transfers
        "nfttx",         # NFT transfers
        "txlistinternal" # Internal transactions
    ]
    
    all_transactions = []
    
    for tx_type in tx_types:
        print(f"Fetching {tx_type} transactions...")
        page = 1
        while True:
            params = {
                "module": "account",
                "action": tx_type,
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": page,
                "offset": 10000,
                "sort": "asc",
                "apikey": API_KEY
            }
            
            response = requests.get(BASESCAN_API_URL, params=params)
            data = response.json()
            
            if data["status"] != "1":
                break
                
            transactions = data["result"]
            if not transactions:
                break
                
            # Add transaction type to each record
            for tx in transactions:
                tx['tx_type'] = tx_type
                
            all_transactions.extend(transactions)
            page += 1
            
    return all_transactions

def preprocess_transactions(transactions, address):
    """Convert raw transactions into features for the model"""
    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Basic feature engineering
    features = {
        'ADDRESS': address,
        'TOTAL_TX': len(df),
        'TOTAL_VALUE': df['value'].astype(float).sum() / 1e18,
        'AVG_VALUE': df['value'].astype(float).mean() / 1e18,
        'UNIQUE_TO_ADDRESSES': len(df['to'].unique()),
        'UNIQUE_FROM_ADDRESSES': len(df['from'].unique()),
        'CONTRACT_CREATIONS': sum(df['to'].isna()),
        'FAILED_TX': sum(int(tx.get('isError', 0)) for tx in transactions),
        'FIRST_TX_TIMESTAMP': min(int(tx['timeStamp']) for tx in transactions),
        'LAST_TX_TIMESTAMP': max(int(tx['timeStamp']) for tx in transactions),
        'TOKEN_TX': sum(1 for tx in transactions if tx['tx_type'] == 'tokentx'),
        'NFT_TX': sum(1 for tx in transactions if tx['tx_type'] == 'nfttx'),
        'INTERNAL_TX': sum(1 for tx in transactions if tx['tx_type'] == 'txlistinternal')
    }
    
    return pd.DataFrame([features])

def generate_fraud_score(address):
    """Complete pipeline to generate fraud score for an address"""
    # Step 1: Fetch all transaction data
    print(f"Fetching transaction data for {address}...")
    transactions = fetch_all_transactions(address)
    
    if not transactions:
        return {
            'address': address,
            'risk_score': 0.0,
            'risk_category': 'LOW',
            'message': 'No transactions found'
        }
    
    # Step 2: Preprocess data
    print("Preprocessing transaction data...")
    test_df = preprocess_transactions(transactions, address)
    
    # Step 3: Load model and generate prediction
    print("Loading model and generating prediction...")
    model = load_model()
    
    # Create graph data (you'll need to adjust this based on your graph_utils implementation)
    test_data, test_node_map = load_graph_data(test_df, 'data.db')
    
    with torch.no_grad():
        predictions = model(test_data.x, test_data.edge_index, test_data.edge_attr)
        if address in test_node_map:
            node_idx = test_node_map[address]
            score = predictions[node_idx].item() if isinstance(predictions[node_idx], torch.Tensor) else float(predictions[node_idx])
        else:
            score = 0.0
    
    # Step 4: Interpret score
    if score >= 0.8:
        risk_category = "HIGH"
    elif score >= 0.5:
        risk_category = "MEDIUM"
    else:
        risk_category = "LOW"
    
    return {
        'address': address,
        'risk_score': float(score),
        'risk_category': risk_category,
        'transaction_count': len(transactions),
        'last_updated': datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Example usage
    ADDRESS = "0xf6d861cfe2c17fa2362742605be9bb1dad279035"
    
    result = generate_fraud_score(ADDRESS)
    print("\nFraud Risk Assessment:")
    print(f"Address: {result['address']}")
    print(f"Risk Score: {result['risk_score']:.4f}")
    print(f"Risk Category: {result['risk_category']}")
    print(f"Transaction Count: {result['transaction_count']}")
    print(f"Last Updated: {result['last_updated']}")