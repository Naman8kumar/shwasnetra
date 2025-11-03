import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# MobileNetV2 base with imagenet weights
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze pretrained layers initially

# Add classifier head
inputs = tf.keras.Input(shape=(224, 224, 3))
x = base_model(inputs, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
outputs = tf.keras.layers.Dense(3, activation='softmax')(x)  # 3 classes: Bengin, Malignant, Normal

model = tf.keras.Model(inputs, outputs)

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

print(model.summary())

# Updated paths based on your directory listing:
train_data_dir = 'E:/Shwasnetra/backend/model_training/dataset/chest'  # Use this for training (contains three folders)
val_data_dir = 'E:/Shwasnetra/backend/model_training/dataset/chest'    # You should split part of this for validation or create separate val folder

# Data generators
train_datagen = ImageDataGenerator(rescale=1./255, horizontal_flip=True, rotation_range=20, validation_split=0.2)  # Use train-validation split
val_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

# Use subset parameter to split dataset
train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='sparse',
    subset='training'  # Use 80% for training
)

val_generator = val_datagen.flow_from_directory(
    val_data_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='sparse',
    subset='validation'  # Use 20% for validation
)

# Train head first - frozen base
model.fit(train_generator,
          epochs=10,
          validation_data=val_generator)

# Unfreeze some layers for fine tuning
base_model.trainable = True
for layer in base_model.layers[:-20]:
    layer.trainable = False

model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.fit(train_generator,
          epochs=10,
          validation_data=val_generator)

# Save trained model
model.save('model_training/lung_cancer_detector_mobilenetv2.keras')
print("Model saved as lung_cancer_detector_mobilenetv2.keras")
