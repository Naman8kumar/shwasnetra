import numpy as np
from PIL import Image
import io
from tensorflow.keras.models import load_model

# Load once at the top
model = load_model("model_training/lung_cancer_detector.keras")

def preprocess_image_bytes(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    return img

def predict_bulk_images(image_bytes, filename=""):
    img = preprocess_image_bytes(image_bytes)
    prob = model.predict(img)[0][0]
    label = "cancer" if prob >= 0.5 else "normal"
    return {
        "label": label,
        "confidence": float(prob)
    }
