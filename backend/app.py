import os
import io
import sys
import logging
import binascii
import hashlib
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from PIL import Image
import numpy as np
import tensorflow as tf
import requests

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --------------------------------------------------
# Flask App
# --------------------------------------------------
app = Flask(__name__)

# ✅ PRODUCTION CORS FIX (Important for Vercel + Render)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static", "heatmaps")
MODEL_DIR = os.path.join(BASE_DIR, "model_training")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# --------------------------------------------------
# Security Config
# --------------------------------------------------
ENCRYPTION_PASSWORD = b"shwasnetra2025"
PBKDF2_ITERS = 200_000

# --------------------------------------------------
# AI Keys
# --------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.2-70b-versatile").strip()

# --------------------------------------------------
# ML Config
# --------------------------------------------------
CLASS_NAMES = ["Normal", "Benign", "Malignant", "Unchest"]
CHEST_FILTER_THRESHOLD = 0.95

# --------------------------------------------------
# Load Models
# --------------------------------------------------
def load_model_safe(path):
    try:
        if not os.path.exists(path):
            logging.warning(f"Model not found: {path}")
            return None
        logging.info(f"Loading model: {path}")
        return tf.keras.models.load_model(path)
    except Exception as e:
        logging.exception(f"Model load failed: {e}")
        return None


CHEST_MODEL_PATH = os.path.join(MODEL_DIR, "chest_filter_model.keras")
MAIN_MODEL_PATH = os.path.join(MODEL_DIR, "lung_cancer_detector_mobilenetv2_full.keras")

CHEST_FILTER_MODEL = load_model_safe(CHEST_MODEL_PATH)
MAIN_MODEL = load_model_safe(MAIN_MODEL_PATH)

CHEST_INPUT_SIZE = (128, 128)
MAIN_INPUT_SIZE = (224, 224)

# --------------------------------------------------
# AES Decryption
# --------------------------------------------------
def derive_key(password: bytes, salt: bytes, iters=PBKDF2_ITERS):
    return hashlib.pbkdf2_hmac("sha256", password, salt, iters, dklen=32)


def decrypt_aes_gcm_blob(blob: bytes, salt_hex: Optional[str], nonce_hex: Optional[str]):
    try:
        if not salt_hex or not nonce_hex:
            return None
        salt = binascii.unhexlify(salt_hex)
        nonce = binascii.unhexlify(nonce_hex)
        key = derive_key(ENCRYPTION_PASSWORD, salt)
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, blob, None)
    except Exception:
        return None

# --------------------------------------------------
# Preprocessing
# --------------------------------------------------
def preprocess_image_bytes(image_bytes: bytes, size=(224, 224)):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(size)
    arr = np.array(img).astype(np.float32) / 255.0
    return np.expand_dims(arr, 0)


def safe_predict(model, x):
    if model is None:
        return None
    preds = model.predict(x, verbose=0)
    return np.squeeze(np.asarray(preds))


# --------------------------------------------------
# Health Route
# --------------------------------------------------
@app.get("/health")
def health():
    return jsonify(status="ok", service="shwasnetra-backend")

# --------------------------------------------------
# Predict Route
# --------------------------------------------------
@app.route("/predict", methods=["POST", "OPTIONS"])
def predict():

    if request.method == "OPTIONS":
        return "", 200

    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        f = request.files["file"]
        encrypted = f.read()

        salt = request.form.get("salt") or request.headers.get("X-SHWASNETRA-SALT")
        nonce = request.form.get("nonce") or request.headers.get("X-SHWASNETRA-NONCE")

        decrypted = decrypt_aes_gcm_blob(encrypted, salt, nonce)
        if decrypted is None:
            return jsonify({"error": "Decryption failed"}), 400

        filename = secure_filename(f.filename or "scan.png")
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as out:
            out.write(decrypted)

        # Chest filter
        if CHEST_FILTER_MODEL:
            x_chest = preprocess_image_bytes(decrypted, CHEST_INPUT_SIZE)
            chest_score = float(np.squeeze(safe_predict(CHEST_FILTER_MODEL, x_chest)))
            if chest_score > CHEST_FILTER_THRESHOLD:
                return jsonify({
                    "status": "rejected",
                    "message": "Non-chest image detected"
                }), 200

        # Main model
        if MAIN_MODEL:
            x_main = preprocess_image_bytes(decrypted, MAIN_INPUT_SIZE)
            preds = safe_predict(MAIN_MODEL, x_main)
            idx = int(np.argmax(preds))
            conf = float(np.max(preds))
            label = CLASS_NAMES[idx]
        else:
            label = "Unknown"
            conf = 0.0

        # Save heatmap placeholder
        gradcam_name = f"gradcam_{filename}"
        gradcam_path = os.path.join(STATIC_FOLDER, gradcam_name)

        with open(gradcam_path, "wb") as out:
            out.write(decrypted)

        return jsonify({
            "status": "success",
            "prediction": label,
            "confidence": round(conf * 100, 2),
            "gradcam": gradcam_name
        })

    except Exception as e:
        logging.exception("Predict error")
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# Chat Route (405 FIX HERE)
# --------------------------------------------------
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():

    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json() or {}
        message = data.get("message", "").strip()
        history = data.get("history", [])

        if not message:
            return jsonify({"error": "Empty message"}), 400

        if not GROQ_API_KEY:
            return jsonify({"reply": "AI service not configured."})

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are ShwasAI, a medical assistant."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.5,
            "max_tokens": 400
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=15
        )

        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            return jsonify({"reply": reply})

        return jsonify({"reply": "AI service unavailable."})

    except Exception as e:
        logging.exception("Chat error")
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# Static
# --------------------------------------------------
@app.route("/static/heatmaps/<path:filename>")
def serve_heatmap(filename):
    return send_from_directory(STATIC_FOLDER, filename)

# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logging.info(f"Starting ShwasNetra Backend on port {port}")
    app.run(host="0.0.0.0", port=port)
