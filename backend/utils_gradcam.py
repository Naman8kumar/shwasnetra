import tensorflow as tf
import numpy as np
import cv2
from tensorflow.keras.preprocessing import image

def generate_gradcam(
    model,
    img_path,
    output_path="gradcam.jpg",
    target_size=(224, 224),
    class_index=None,
    last_conv_layer_name=None,
    threshold_ratio=0.5,   # Less than default, to detect only true hot spots
    dot_radius=5           # Radius for red marks
):
    # 1. Load and preprocess image
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 2. Find last conv layer automatically if not provided
    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                last_conv_layer_name = layer.name
                break
    last_conv_layer = model.get_layer(last_conv_layer_name)

    # 3. Grad-CAM Model
    grad_model = tf.keras.models.Model([model.inputs], [last_conv_layer.output, model.output])

    # 4. Inference/class selection
    preds = model.predict(img_array)
    if class_index is None:
        class_index = np.argmax(preds[0])

    # 5. Get Grad-CAM heatmap
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        loss = predictions[:, class_index]
    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)

    # 6. Normalize & print debug info
    heatmap = np.maximum(heatmap, 0)
    min_heat, max_heat = np.min(heatmap), np.max(heatmap)
    print(f"Heatmap min/max: {min_heat:.4f} / {max_heat:.4f}")
    if max_heat != 0:
        heatmap /= max_heat

    # 7. Resize, scale to 0-255
    heatmap_resized = cv2.resize(heatmap, target_size)
    heatmap_scaled = np.uint8(255 * heatmap_resized)
    print(f"Heatmap_scaled min/max: {np.min(heatmap_scaled)} / {np.max(heatmap_scaled)}")

    # 8. Direct RED DOT logic
    thresh_value = int(threshold_ratio * np.max(heatmap_scaled))
    print(f"Dot threshold value: {thresh_value}")
    coords = np.column_stack(np.where(heatmap_scaled > thresh_value))
    print(f"Detected hot pixels: {coords.shape[0]}")

    # 9. Overlay
    original_img = cv2.imread(img_path)
    original_img = cv2.resize(original_img, target_size)
    overlay_img = original_img.copy()

    for y, x in coords:
        cv2.circle(overlay_img, (x, y), dot_radius, (0, 0, 255), -1)

    cv2.imwrite(output_path, overlay_img)
    return output_path
