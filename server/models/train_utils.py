import torch
import torch.nn.functional as F
from tqdm import tqdm  # Import tqdm

def train(model, data, optimizer, train_labels, EPOCHS, threshold=0.5):
    # A simple fixed binary threshold is used for classification
    accuracies = []

    # Add tqdm for epoch progress
    for epoch in tqdm(range(EPOCHS), desc="Training", unit="epoch"):
        model.train()
        optimizer.zero_grad()
        out = model(data.x, data.edge_index, data.edge_attr)
        loss = F.binary_cross_entropy(out, train_labels)
        loss.backward()
        optimizer.step()

        # Apply fixed binary thresholding for prediction (e.g., 0.5)
        preds = (out > threshold).float()  # Apply threshold (if > 0.5, class 1, else class 0)
        correct = (preds == train_labels).sum().item()
        accuracy = correct / len(train_labels)
        accuracies.append(accuracy)

    avg_accuracy = sum(accuracies) / len(accuracies)  # Average accuracy over all epochs
    print(f"Training complete! Average accuracy: {avg_accuracy:.4f}")
