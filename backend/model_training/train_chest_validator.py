import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import os

DATA_DIR = "dataset"
OUTPUT_MODEL = "chest_vs_nonchest_classifier.keras"

# Data generator with augmentation for robustness
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=15,
    zoom_range=0.1,
    shear_range=0.1,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3]
)

train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(224, 224),
    batch_size=16,
    class_mode='binary',
    subset='training'
)

val_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(224, 224),
    batch_size=16,
    class_mode='binary',
    subset='validation'
)

base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze initial layers

# Classifier head: average pool + dropout (regularization!) + dense
x = GlobalAveragePooling2D()(base_model.output)
x = Dropout(0.3)(x)  # REGULARIZATION
x = Dense(1, activation='sigmoid')(x)
model = Model(base_model.input, x)

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Callbacks for best performance
callbacks = [
    EarlyStopping(monitor="val_loss", patience=7, restore_best_weights=True, verbose=1),
    ModelCheckpoint(OUTPUT_MODEL, monitor="val_loss", save_best_only=True, verbose=1)
]

# Train longer, but safely
history = model.fit(
    train_gen, 
    validation_data=val_gen, 
    epochs=50,
    callbacks=callbacks
)

# Optionally unfreeze for fine-tuning if val accuracy plateaus
base_model.trainable = True
model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss='binary_crossentropy', metrics=['accuracy'])
history_finetune = model.fit(train_gen, validation_data=val_gen, epochs=10, callbacks=callbacks)

model.save(OUTPUT_MODEL)
print(f"✅ Saved improved classifier to {OUTPUT_MODEL}")
