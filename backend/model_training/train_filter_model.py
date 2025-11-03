import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os, shutil
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# ✅ Paths
# -----------------------------------------------------------
DATASET_DIR = "model_training/dataset"
TRAIN_DIR = "model_training/dataset/train_split"
VAL_DIR = "model_training/dataset/val_split"

# Clean old splits (to prevent stale files)
if os.path.exists(TRAIN_DIR):
    shutil.rmtree(TRAIN_DIR)
if os.path.exists(VAL_DIR):
    shutil.rmtree(VAL_DIR)

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VAL_DIR, exist_ok=True)

# -----------------------------------------------------------
# ✅ Collect images recursively
# -----------------------------------------------------------
def collect_images(folder_name):
    """Recursively find all images inside a folder (any subfolder)."""
    exts = ('.png', '.jpg', '.jpeg', '.bmp')
    folder_path = os.path.join(DATASET_DIR, folder_name)
    all_images = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith(exts):
                all_images.append(os.path.join(root, f))
    return all_images


# -----------------------------------------------------------
# ✅ Prepare dataset split
# -----------------------------------------------------------
def prepare_split():
    chest_images = collect_images("chest")
    unchest_folder = "unchest"

    if not os.path.exists(os.path.join(DATASET_DIR, unchest_folder)):
        for alt in ["nonchest", "notchest", "others"]:
            if os.path.exists(os.path.join(DATASET_DIR, alt)):
                unchest_folder = alt
                break

    unchest_images = collect_images(unchest_folder)

    if len(chest_images) == 0:
        raise ValueError(f"No chest images found in {DATASET_DIR}/chest")
    if len(unchest_images) == 0:
        raise ValueError(f"No unchest images found in {DATASET_DIR}/{unchest_folder}")

    chest_train, chest_val = train_test_split(chest_images, test_size=0.2, random_state=42)
    unchest_train, unchest_val = train_test_split(unchest_images, test_size=0.2, random_state=42)

    # Copy to split folders
    for cls, (train_list, val_list) in {
        "chest": (chest_train, chest_val),
        "unchest": (unchest_train, unchest_val)
    }.items():
        os.makedirs(os.path.join(TRAIN_DIR, cls), exist_ok=True)
        os.makedirs(os.path.join(VAL_DIR, cls), exist_ok=True)
        for src in train_list:
            try:
                shutil.copy(src, os.path.join(TRAIN_DIR, cls))
            except Exception as e:
                print(f"⚠️ Skipped {src}: {e}")
        for src in val_list:
            try:
                shutil.copy(src, os.path.join(VAL_DIR, cls))
            except Exception as e:
                print(f"⚠️ Skipped {src}: {e}")

prepare_split()

# -----------------------------------------------------------
# ✅ Image Generators with Augmentation
# -----------------------------------------------------------
train_datagen = ImageDataGenerator(
    rescale=1.0/255.0,
    rotation_range=8,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True
)

val_datagen = ImageDataGenerator(rescale=1.0/255.0)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(128, 128),
    batch_size=16,
    class_mode="binary"
)

val_gen = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=(128, 128),
    batch_size=16,
    class_mode="binary"
)

print("\n✅ Class indices mapping:")
print(train_gen.class_indices)
# Expect: {'chest': 0, 'unchest': 1}

# -----------------------------------------------------------
# ✅ Build Model
# -----------------------------------------------------------
base_model = tf.keras.applications.MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(128, 128, 3)
)
base_model.trainable = False  # freeze base

x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
x = tf.keras.layers.Dense(64, activation="relu")(x)
x = tf.keras.layers.Dropout(0.3)(x)
out = tf.keras.layers.Dense(1, activation="sigmoid")(x)

model = tf.keras.Model(inputs=base_model.input, outputs=out)
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# -----------------------------------------------------------
# ✅ Train Model
# -----------------------------------------------------------
EPOCHS = 10
history = model.fit(train_gen, validation_data=val_gen, epochs=EPOCHS)

# -----------------------------------------------------------
# ✅ Plot and Save
# -----------------------------------------------------------
plt.figure(figsize=(8,4))
plt.subplot(1,2,1)
plt.plot(history.history["accuracy"], label="train_acc")
plt.plot(history.history["val_accuracy"], label="val_acc")
plt.title("Accuracy")
plt.legend()

plt.subplot(1,2,2)
plt.plot(history.history["loss"], label="train_loss")
plt.plot(history.history["val_loss"], label="val_loss")
plt.title("Loss")
plt.legend()

plt.tight_layout()
plt.savefig("model_training/filter_training_metrics.png")
print("\n📊 Saved training metrics plot to model_training/filter_training_metrics.png")

# -----------------------------------------------------------
# ✅ Save Model
# -----------------------------------------------------------
SAVE_PATH = "model_training/chest_filter_model.keras"
model.save(SAVE_PATH)
print(f"\n✅ Chest filter model trained and saved at {SAVE_PATH}")

# -----------------------------------------------------------
# ✅ Test quick sample batch
# -----------------------------------------------------------
sample_imgs, sample_labels = next(val_gen)
preds = model.predict(sample_imgs)
print("\n🔍 Sample predictions:")
for i in range(min(5, len(preds))):
    print(f"True: {sample_labels[i]:.0f}, Predicted sigmoid: {preds[i][0]:.3f}")
