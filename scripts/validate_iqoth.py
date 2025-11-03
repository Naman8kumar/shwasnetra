import os
import torch
from torchvision import transforms
from PIL import Image
from torch.utils.data import DataLoader, Dataset

# Import the same model you used in training
from train_luna16 import Simple3DCNN

DATA_DIR = "E:/Shwasnetra/The IQ-OTHNCCD lung cancer dataset"
MODEL_PATH = "shwasnetra_luna16_model.pth"

LABEL_MAP = {
    'normal': 0,
    'benign': 1,
    'malignant': 1,
}

class IQOTHDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.transform = transform
        self.samples = []
        for label_name, label in LABEL_MAP.items():
            class_dir = os.path.join(root_dir, label_name)
            for file in os.listdir(class_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.samples.append((os.path.join(class_dir, file), label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        image_path, label = self.samples[idx]
        image = Image.open(image_path).convert("L")
        if self.transform:
            image = self.transform(image)
        image = image.unsqueeze(0)  # shape: (1, H, W)
        image = torch.nn.functional.interpolate(image.unsqueeze(0), size=(128, 128, 128), mode="trilinear", align_corners=False)
        return image.squeeze(0), torch.tensor(label, dtype=torch.float32)

transform = transforms.Compose([
    transforms.Resize((128, 128)),  # Resize 2D first
    transforms.ToTensor(),
])

dataset = IQOTHDataset(DATA_DIR, transform=transform)
loader = DataLoader(dataset, batch_size=4, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = Simple3DCNN().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

correct = 0
total = 0

with torch.no_grad():
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device).unsqueeze(1)
        outputs = model(images)
        preds = (outputs > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.size(0)

accuracy = correct / total
print(f"✅ External Validation Accuracy on IQ-OTH/NCCD: {accuracy:.4f}")
