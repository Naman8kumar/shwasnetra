import os
import random

# Path to preprocessed CT scan .npy files
PREPROCESSED_DIR = "E:/Shwasnetra/preprocessed_luna16"
OUTPUT_FILE = "E:/Shwasnetra/validation/sampled_ids.txt"

# Get all .npy files
all_files = [f for f in os.listdir(PREPROCESSED_DIR) if f.endswith(".npy")]

# Randomly pick 50
selected = random.sample(all_files, 50)

# Remove .npy extension before saving
selected_ids = [f.replace(".npy", "") for f in selected]

# Save
with open(OUTPUT_FILE, "w") as f:
    for sid in selected_ids:
        f.write(sid + "\n")

print(f"✅ Saved 50 random scan IDs to {OUTPUT_FILE}")
