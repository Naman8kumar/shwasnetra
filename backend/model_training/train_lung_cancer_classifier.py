import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import numpy as np
from sklearn.utils.class_weight import compute_class_weight

# Constants - adjust paths and params as needed
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50
FINE_TUNE_EPOCHS = 30  # fine tune all layers after initial training

train_dir = "E:/Shwasnetra/backend/model_training/dataset/chest"

# Data augmentation plus validation split
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.15,
    horizontal_flip=True,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.15,
    fill_mode='nearest'
)

# Training data generator
train_generator = datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="training",
    shuffle=True
)

# Validation data generator
val_generator = datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="validation",
    shuffle=False
)

# Compute class weights for imbalance correction
labels = train_generator.classes
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(labels),
    y=labels
)
class_weights = dict(enumerate(class_weights))
print(f"Class weights: {class_weights}")

# Base model with frozen layers initially
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

# Add custom layers on top
model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(4, activation="softmax")
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Callbacks for early stopping and learning rate reduction
early_stopping = EarlyStopping(monitor='val_loss', patience=25, restore_best_weights=True, verbose=1)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', patience=7, factor=0.5, min_lr=1e-6, verbose=1)

# Phase 1: Train head only
model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=[early_stopping, reduce_lr],
    verbose=2
)

# Phase 2: Fine-tuning full base model
base_model.trainable = True  # Unfreeze all layers for fine-tuning

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

fine_tune_es = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1)
fine_tune_lr = ReduceLROnPlateau(monitor='val_loss', patience=7, factor=0.5, min_lr=1e-7, verbose=1)

model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=FINE_TUNE_EPOCHS,
    class_weight=class_weights,
    callbacks=[fine_tune_es, fine_tune_lr],
    verbose=2
)

# Save trained model for inference
model.save("lung_cancer_detector_mobilenetv2_full.keras")
print("Model training complete and saved as lung_cancer_detector_mobilenetv2_full.keras")
