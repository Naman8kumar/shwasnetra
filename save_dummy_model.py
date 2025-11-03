import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# Dummy CNN Model
model = models.Sequential([
    layers.Input(shape=(224, 224, 3)),
    layers.Conv2D(16, (3, 3), activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train on dummy data
X_dummy = np.random.rand(5, 224, 224, 3)
y_dummy = np.random.randint(0, 2, 5)
model.fit(X_dummy, y_dummy, epochs=1)

# Save the model inside backend/model_training/
model.save('backend/model_training/lung_cancer_detector.keras')
