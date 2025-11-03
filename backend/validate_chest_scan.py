import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

# ✅ Load the chest vs non-chest binary classifier using an absolute path
try:
    model_path = os.path.join(os.getcwd(), 'model_training', 'chest_vs_nonchest_classifier.keras')
    model = tf.keras.models.load_model(model_path, compile=False)
    print("[INFO] Chest scan validator model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load chest classifier model: {e}")
    model = None

def is_chest_xray(img_path):
    """
    Validates whether the uploaded image is a chest X-ray or CT scan.
    Returns True if valid, False otherwise.
    """
    if model is None:
        print("[ERROR] Model not available for validation.")
        return False

    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)[0][0]  # Binary output
        return prediction < 0.5  # ✅ Corrected: True = chest, False = non-chest
    except Exception as e:
        print(f"[Validation Error] {e}")
        return False
