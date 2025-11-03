import os
import numpy as np
import SimpleITK as sitk
from tqdm import tqdm

# INPUT path
LUNA16_SUBSET_PATH = r"E:\Shwasnetra\LUNA16\subset0"

# OUTPUT path for .npy files
OUTPUT_DIR = r"E:\Shwasnetra\preprocessed_luna16"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Standard voxel spacing
TARGET_SPACING = [1.0, 1.0, 1.0]

def load_itk_image(filename):
    itkimage = sitk.ReadImage(filename)
    img_array = sitk.GetArrayFromImage(itkimage)
    origin = np.array(itkimage.GetOrigin())
    spacing = np.array(itkimage.GetSpacing())
    return img_array, origin, spacing, itkimage

def resample_image(itk_image, new_spacing=[1.0, 1.0, 1.0]):
    original_spacing = itk_image.GetSpacing()
    original_size = itk_image.GetSize()

    new_size = [
        int(round(original_size[i] * (original_spacing[i] / new_spacing[i])))
        for i in range(3)
    ]

    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(new_spacing)
    resample.SetSize(new_size)
    resample.SetInterpolator(sitk.sitkLinear)
    resample.SetOutputOrigin(itk_image.GetOrigin())
    resample.SetOutputDirection(itk_image.GetDirection())

    return resample.Execute(itk_image)

def preprocess_and_save():
    files = [f for f in os.listdir(LUNA16_SUBSET_PATH) if f.endswith('.mhd')]
    print(f"Found {len(files)} .mhd files.")

    for f in tqdm(files, desc="Preprocessing"):
        filepath = os.path.join(LUNA16_SUBSET_PATH, f)
        try:
            img_array, origin, spacing, itk_image = load_itk_image(filepath)

            # Resample
            resampled_itk = resample_image(itk_image, TARGET_SPACING)
            resampled_array = sitk.GetArrayFromImage(resampled_itk)

            # Normalize HU values
            clipped = np.clip(resampled_array, -1000, 400)

            # Save .npy
            filename = os.path.splitext(f)[0] + ".npy"
            np.save(os.path.join(OUTPUT_DIR, filename), clipped)

        except Exception as e:
            print(f"Error processing {f}: {e}")

if __name__ == "__main__":
    preprocess_and_save()
