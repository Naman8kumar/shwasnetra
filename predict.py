import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# Load the trained model
model = tf.keras.models.load_model('model_training/lung_cancer_model.h5')

# Class names
class_names = ['cancer', 'normal']

def predict_image(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return

    img_array = image.img_to_array(img) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]
    if prediction > 0.5:
        result = class_names[1]  # normal
    else:
        result = class_names[0]  # cancer

    print(f"✅ Prediction: {result} (Confidence: {prediction:.2f})")

if __name__ == '__main__':
    test_image_path = 'sample_test/test1.png'  # ✅ Replace with your image name if different
    predict_image(test_image_path)
