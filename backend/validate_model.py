import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.metrics import classification_report

model = load_model('model_training/lung_cancer_detector.keras')

validation_dir = 'validation'
class_names = ['cancer', 'normal']
X, y_true = [], []

for label in class_names:
    folder = os.path.join(validation_dir, label)
    for img_name in os.listdir(folder):
        img_path = os.path.join(folder, img_name)
        try:
            img = load_img(img_path, target_size=(224, 224))
            img_array = img_to_array(img) / 255.0
            X.append(img_array)
            y_true.append(0 if label == 'cancer' else 1)
        except Exception as e:
            print(f"Error loading {img_name}: {e}")

X = np.array(X)
y_true = np.array(y_true)
y_pred_probs = model.predict(X).flatten()
y_pred = [1 if p > 0.5 else 0 for p in y_pred_probs]

# Print detailed classification report
print(classification_report(y_true, y_pred, target_names=class_names))
