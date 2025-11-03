import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

from bias_testing.monitoring_logger import log_misclassification

# === Utilities ===

def load_and_preprocess(image_path):
    img = load_img(image_path, target_size=(224, 224), color_mode='rgb')
    img_array = img_to_array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

def get_true_label(image_path):
    # Assumes label in filename: e.g., lung_1_23_cancer.png
    return 1 if "cancer" in image_path.lower() else 0

def get_gender(image_path):
    parts = os.path.basename(image_path).split("_")
    return "male" if parts[1] == "1" else "female"

def get_age_group(image_path):
    parts = os.path.basename(image_path).split("_")
    age = int(parts[2])
    if age < 30:
        return "young"
    elif age < 60:
        return "middle"
    else:
        return "senior"

# === Load model ===
model = load_model("model_training/lung_cancer_detector.keras")

# === Run inference with logging ===
image_folder = "data/iqoth/val"
image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(".png")]

for image_path in image_paths:
    img = load_and_preprocess(image_path)
    pred_prob = model.predict(img)[0][0]
    pred = int(pred_prob >= 0.5)
    true_label = get_true_label(image_path)
    confidence = float(pred_prob)

    gender = get_gender(image_path)
    age_group = get_age_group(image_path)

    if pred != true_label:
        log_misclassification(
            image_path=image_path,
            pred=pred,
            true=true_label,
            confidence=confidence,
            metadata={"gender": gender, "age_group": age_group}
        )
