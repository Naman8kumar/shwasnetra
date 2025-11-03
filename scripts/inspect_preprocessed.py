import os
import numpy as np
import matplotlib.pyplot as plt

# Path to the folder where preprocess_luna16.py saved output
PREPROCESSED_PATH = r"E:\Shwasnetra\preprocessed_luna16"

def load_and_visualize(file_path):
    data = np.load(file_path)
    print(f"Loaded: {file_path}")
    print(f"Shape: {data.shape}")
    
    # Show a few slices from the middle
    mid = data.shape[0] // 2
    plt.figure(figsize=(10, 4))
    for i, offset in enumerate([-2, 0, 2]):
        plt.subplot(1, 3, i+1)
        plt.imshow(data[mid + offset], cmap='gray')
        plt.title(f"Slice {mid + offset}")
        plt.axis('off')
    plt.show()

def main():
    files = [f for f in os.listdir(PREPROCESSED_PATH) if f.endswith('.npy')]
    if not files:
        print("No .npy files found.")
        return

    # Inspect the first file
    first_file = os.path.join(PREPROCESSED_PATH, files[0])
    load_and_visualize(first_file)

if __name__ == "__main__":
    main()
