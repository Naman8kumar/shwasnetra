import os
import numpy as np
import torch
from torch.utils.data import Dataset
import pandas as pd
import scipy.ndimage


class Luna16Dataset(Dataset):
    def __init__(self, data_dir, annotations_path, resize_to=(128, 128), normalize=True):
        self.data_dir = data_dir
        self.resize_to = resize_to
        self.normalize = normalize

        # Load annotation seriesuids for label 1
        self.positive_ids = set()
        df = pd.read_csv(annotations_path)
        self.positive_ids = set(df['seriesuid'].values)

        # Collect scan paths
        self.scan_ids = []
        for fname in os.listdir(data_dir):
            if fname.endswith('.npy'):
                self.scan_ids.append(fname[:-4])  # remove ".npy"

    def __len__(self):
        return len(self.scan_ids)

    def __getitem__(self, idx):
        scan_id = self.scan_ids[idx]
        scan_path = os.path.join(self.data_dir, scan_id + ".npy")
        volume = np.load(scan_path)  # shape: [D, H, W]

        # Resize to (128, 128) spatially
        if self.resize_to:
            d, h, w = volume.shape
            volume = scipy.ndimage.zoom(
                volume,
                zoom=(1, self.resize_to[0] / h, self.resize_to[1] / w),
                order=1
            )  # shape: [D, 128, 128]

        # Normalize to [0, 1]
        if self.normalize:
            volume = volume.astype(np.float32)
            volume = (volume - np.min(volume)) / (np.max(volume) - np.min(volume) + 1e-5)

        # Center crop or pad depth to 128
        d = volume.shape[0]
        target_d = 128
        if d > target_d:
            start = (d - target_d) // 2
            volume = volume[start:start + target_d]
        else:
            pad = (target_d - d) // 2
            volume = np.pad(volume, ((pad, target_d - d - pad), (0, 0), (0, 0)), mode='constant')

        # Final shape: [1, 128, 128, 128]
        volume = torch.tensor(volume).unsqueeze(0)  # add channel dim

        label = 1 if scan_id in self.positive_ids else 0
        return volume, label
