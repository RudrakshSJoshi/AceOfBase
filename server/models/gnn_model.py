import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, GATConv
from torch_geometric.utils import add_self_loops

class EnhancedFraudGNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, heads=4):
        super(EnhancedFraudGNN, self).__init__()

        # First layer: SAGEConv
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        
        # Second layer: GATConv (Adding attention mechanism)
        self.conv2 = GATConv(hidden_channels, hidden_channels, heads=heads, concat=True)
        
        # Third layer: Another SAGEConv
        self.conv3 = SAGEConv(hidden_channels * heads, hidden_channels)
        
        # Fourth layer: Another GATConv for attention aggregation
        self.conv4 = GATConv(hidden_channels, out_channels, heads=1, concat=False)

    def forward(self, x, edge_index, edge_attr=None):
        # Add self-loops to the graph
        edge_index, _ = add_self_loops(edge_index, num_nodes=x.size(0))

        # First layer: SAGEConv
        x = self.conv1(x, edge_index)
        x = F.leaky_relu(x, negative_slope=0.01)

        # Second layer: GATConv with attention mechanism
        x = self.conv2(x, edge_index)
        x = F.leaky_relu(x, negative_slope=0.01)

        # Third layer: Another SAGEConv
        x = self.conv3(x, edge_index)
        x = F.leaky_relu(x, negative_slope=0.01)

        # Fourth layer: GATConv for final attention aggregation
        x = self.conv4(x, edge_index)

        # Apply sigmoid to get values between 0 and 1 (for binary classification)
        return torch.sigmoid(x).squeeze()