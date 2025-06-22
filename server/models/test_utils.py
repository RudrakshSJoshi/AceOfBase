from models.graph_utils import load_graph_data
import pandas as pd
import torch
from tqdm import tqdm  # Correct import
import numpy as np

def test(model, threshold=0.5):
    # Load test dataset and construct graph
    test_df = pd.read_csv('Data/test_addresses.csv')
    test_data, test_node_map = load_graph_data(test_df, 'data.db')

    # Predict using trained model
    model.eval()
    test_results = []
    with torch.no_grad():
        predictions = model(test_data.x, test_data.edge_index, test_data.edge_attr)
        for address in tqdm(test_df['ADDRESS'], desc="Predicting", unit="address"):
            if address in test_node_map:
                node_idx = test_node_map[address]
                pred = predictions[node_idx].item() if isinstance(predictions[node_idx], torch.Tensor) else float(predictions[node_idx])
            else:
                pred = 0
            test_results.append([address, 1 if (float(pred) >= float(threshold)) else 0])

    # Save predictions
    output_df = pd.DataFrame(test_results, columns=['ADDRESS', 'PRED'])
    output_df.to_csv('GNN_test_output.csv', index=False)