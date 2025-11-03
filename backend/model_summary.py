import tensorflow as tf

model_path = 'model_training/lung_cancer_detector.keras'
model = tf.keras.models.load_model(model_path)

model.summary()
