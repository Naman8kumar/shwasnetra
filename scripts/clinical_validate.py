import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from train_luna16 import Simple3DCNN
import scipy.ndimage  # ✅ for resizing 3D volumes

# Load sampled IDs
with open("validation/sampled_ids.txt") as f:
    sample_ids = [line.strip() for line in f.readlines()]

PREPROCESSED_DIR = "preprocessed_luna16"
MODEL_PATH = "shwasnetra_luna16_model.pth"

def resize_volume(img, target_shape=(32, 64, 64)):
    # Resize a 3D numpy volume
    factors = [t / s for t, s in zip(target_shape, img.shape)]
    return scipy.ndimage.zoom(img, zoom=factors, order=1)  # linear interpolation

# Define Dataset
class LUNASampleDataset(Dataset):
    def __init__(self, ids):
        self.ids = ids

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        volume = np.load(os.path.join(PREPROCESSED_DIR, self.ids[idx] + ".npy"))
        volume = volume.astype(np.float32)
        volume = resize_volume(volume, target_shape=(32, 64, 64))  # ✅ resize to match model input
        volume = torch.tensor(volume).unsqueeze(0)  # shape: (1, D, H, W)
        return volume, self.ids[idx]

dataset = LUNASampleDataset(sample_ids)
loader = DataLoader(dataset, batch_size=1)

# Load model
model = Simple3DCNN()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

# Run predictions
results = []
with torch.no_grad():
    for volume, scan_id in loader:
        outputs = model(volume)
        prediction = torch.argmax(outputs, dim=1).item()
        results.append((scan_id[0], prediction))

# Save to file
os.makedirs("validation", exist_ok=True)
with open("validation/clinical_predictions.txt", "w") as f:
    for scan_id, pred in results:
        f.write(f"{scan_id},{pred}\n")

print("✅ Predictions saved to validation/clinical_predictions.txt")
