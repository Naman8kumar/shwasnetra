import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from dataset_luna16 import Luna16Dataset
from model import ShwasNetra3D
import numpy as np
from collections import Counter

# Focal Loss definition
class FocalLoss(nn.Module):
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        self.ce = nn.CrossEntropyLoss(reduction='none')

    def forward(self, inputs, targets):
        ce_loss = self.ce(inputs, targets)
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * ((1 - pt) ** self.gamma) * ce_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load dataset
annotations_path = "luna16/annotations.csv"
dataset = Luna16Dataset(data_dir="preprocessed_luna16", annotations_path=annotations_path)

# Count label distribution
labels = [1 if scan_id in dataset.positive_ids else 0 for scan_id in dataset.scan_ids]
label_counts = Counter(labels)
print(f"📊 Label distribution: {label_counts}")

# Compute class weights for sampler
weights = [1.0 / label_counts[label] for label in labels]
sampler = WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)

# DataLoader
dataloader = DataLoader(dataset, batch_size=2, sampler=sampler)

# Initialize model
model = ShwasNetra3D().to(device)

# Loss, optimizer
criterion = FocalLoss(alpha=1.0, gamma=2.0)
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
num_epochs = 50  # You said you want 50
print(f"🚀 Starting training on {device} with {len(dataset)} samples...")

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for i, (inputs, labels) in enumerate(dataloader):
        inputs = inputs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)

        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

        if (i + 1) % 2 == 1:
            print(f"Epoch {epoch+1}, Batch {i+1}, Loss: {loss.item():.4f}")

    avg_loss = running_loss / len(dataloader)
    accuracy = 100 * correct / total
    print(f"✅ Epoch {epoch+1} completed. Avg Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")

# Save the model
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), "models/shwasnetra_luna16_model.pth")
print("✅ Model saved as models/shwasnetra_luna16_model.pth")
