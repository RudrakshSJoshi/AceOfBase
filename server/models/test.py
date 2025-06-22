from csv_to_sql_preprocess import create_single_db_from_csv
import torch
import pandas as pd
from torch_geometric.data import Data
from models.gnn_model import EnhancedFraudGNN
from models.graph_utils import load_graph_data
from models.train_utils import train
from models.test_utils import test

create_single_db_from_csv()

# Load datasets
train_df = pd.read_csv('Data/train_addresses.csv')
data, node_map = load_graph_data(train_df, 'data.db')

train_labels = torch.full((len(node_map),), 0.5)
for _, row in train_df.iterrows():
    if row['ADDRESS'] in node_map:
        train_labels[node_map[row['ADDRESS']]] = row['LABEL']

# Model and optimizer
hidden_units = 512
model = EnhancedFraudGNN(in_channels=15, hidden_channels=hidden_units, out_channels=1)
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)

# Train the model
train(model, data, optimizer, train_labels, EPOCHS=100)

# Save model
torch.save(model.state_dict(), 'fraud_gnn_final.pth')
print("Model saved!")

test(model)