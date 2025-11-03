import os
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

# Paths
IMAGE_DIR = 'Test cases'
OUTPUT_CSV = 'prediction/iqoth_bias_predictions.csv'

# Load model
model = tf.keras.models.load_model('model_training/lung_cancer_detector.keras')
class_names = ['cancer', 'normal']

# Collect image filenames
image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith('.png')]

# Run predictions
results = []
for fname in image_files:
    img_path = os.path.join(IMAGE_DIR, fname)
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)[0][0]
        label = class_names[1] if prediction > 0.5 else class_names[0]

        results.append({
            'filename': fname,
            'predicted_label': label,
            'confidence': prediction
        })

    except Exception as e:
        print(f"❌ Error processing {fname}: {e}")

# Save to CSV
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
print(f"✅ Predictions saved to {OUTPUT_CSV}")
