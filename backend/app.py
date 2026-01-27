import os
import io
import json
import sys
import logging
import binascii
import hashlib
from datetime import datetime
from typing import Optional

# 1. Load Environment Variables
from dotenv import load_dotenv
load_dotenv()

# 2. Flask & Server Imports
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

# 3. Image & ML Imports
from PIL import Image
import numpy as np
import tensorflow as tf
import requests

# 4. Security Imports
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 5. PDF Generation Imports
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -------------------------
# Flask App Setup
# -------------------------
app = Flask(__name__)

# Enable CORS for Frontend (Ports 5173 for Vite, 8083 for your custom port)
CORS(app, resources={r"/*": {"origins": [
    "https://shwasnetra.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8083",
    "http://127.0.0.1:8083"
]}}, supports_credentials=True)

# Limit upload size to 50 MB
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024 

# -------------------------
# Paths & Configuration
# -------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static", "heatmaps")
MODEL_DIR = os.path.join(BASE_DIR, "model_training")

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Security Constants
ENCRYPTION_PASSWORD = b"shwasnetra2025"
PBKDF2_ITERS = 200_000

# AI API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.2-70b-versatile").strip()
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# ML Constants
CLASS_NAMES = ["Normal", "Benign", "Malignant", "Unchest"]
CHEST_FILTER_THRESHOLD = 0.95  # Threshold for rejecting non-chest images

# -------------------------
# Model Loading Helper
# -------------------------
def load_model_safe(path):
    try:
        if not os.path.exists(path):
            app.logger.error(f"[model] File not found: {path}")
            return None
        app.logger.info(f"[model] Loading: {path}")
        model = tf.keras.models.load_model(path)
        app.logger.info(f"[model] Successfully loaded: {path}")
        return model
    except Exception as e:
        app.logger.exception(f"[model] Failed to load {path}: {e}")
        return None

# Load Models Globaly
CHEST_MODEL_PATH = os.path.join(MODEL_DIR, "chest_filter_model.keras")
MAIN_MODEL_PATH = os.path.join(MODEL_DIR, "lung_cancer_detector_mobilenetv2_full.keras")

CHEST_FILTER_MODEL = load_model_safe(CHEST_MODEL_PATH)
MAIN_MODEL = load_model_safe(MAIN_MODEL_PATH)

# Define Input Sizes (Defaults, will try to read from model)
CHEST_INPUT_SIZE = (128, 128)
MAIN_INPUT_SIZE = (224, 224)

try:
    if CHEST_FILTER_MODEL and hasattr(CHEST_FILTER_MODEL, "input_shape"):
        s = CHEST_FILTER_MODEL.input_shape
        if s and len(s) >= 4:
            CHEST_INPUT_SIZE = (int(s[1]), int(s[2]))
    if MAIN_MODEL and hasattr(MAIN_MODEL, "input_shape"):
        s = MAIN_MODEL.input_shape
        if s and len(s) >= 4:
            MAIN_INPUT_SIZE = (int(s[1]), int(s[2]))
except Exception:
    pass

app.logger.info(f"CONFIG: Chest Size={CHEST_INPUT_SIZE} | Main Size={MAIN_INPUT_SIZE}")

# -------------------------
# AES Decryption Logic
# -------------------------
def derive_key(password: bytes, salt: bytes, iters=PBKDF2_ITERS):
    return hashlib.pbkdf2_hmac("sha256", password, salt, iters, dklen=32)

def decrypt_aes_gcm_blob(blob: bytes, salt_hex: Optional[str], nonce_hex: Optional[str]) -> Optional[bytes]:
    try:
        if not salt_hex or not nonce_hex:
            app.logger.warning("[decrypt] Missing salt or nonce headers")
            return None
        salt = binascii.unhexlify(salt_hex)
        nonce = binascii.unhexlify(nonce_hex)
        key = derive_key(ENCRYPTION_PASSWORD, salt)
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, blob, None)
    except Exception as e:
        app.logger.error(f"[decrypt] Decryption failed: {e}")
        return None

# -------------------------
# Image Preprocessing
# -------------------------
def preprocess_image_bytes(image_bytes: bytes, size=(224,224)):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(size)
        arr = np.array(img).astype(np.float32) / 255.0
        return np.expand_dims(arr, 0)
    except Exception as e:
        app.logger.error(f"[preprocess] Error: {e}")
        return None

def safe_predict_with_model(model, x):
    try:
        if model is None: return None
        preds = model.predict(x, verbose=0)
        return np.squeeze(np.asarray(preds))
    except Exception as e:
        app.logger.error(f"[predict] Inference failed: {e}")
        return None

def format_probability_array(arr):
    try:
        a = np.asarray(arr)
        if a.ndim == 0: return 0, float(a)
        idx = int(np.argmax(a))
        conf = float(np.max(a))
        return idx, conf
    except Exception:
        return 0, 0.0

# -------------------------
# Chatbot Logic
# -------------------------
def query_llm(prompt: str, history: Optional[list] = None):
    messages = [{"role":"system","content":"You are ShwasAI, a medically-safe assistant for lung health."}]
    if history:
        for h in history[-6:]:
            if "user" in h: messages.append({"role":"user","content":h["user"]})
            if "bot" in h: messages.append({"role":"assistant","content":h["bot"]})
    messages.append({"role":"user","content":prompt})

    # Try Groq First
    if GROQ_API_KEY:
        try:
            payload = {"model": GROQ_MODEL, "messages": messages, "temperature": 0.5, "max_tokens": 400}
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            app.logger.warning(f"[Groq] Error: {e}")

    return "I'm currently offline or busy. Please try again later."

# -------------------------
# API Routes
# -------------------------
@app.get("/health")
def health():
    return jsonify(status="ok", service="shwasnetra-backend"), 200

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "models": {
            "chest_filter": bool(CHEST_FILTER_MODEL),
            "cancer_detector": bool(MAIN_MODEL)
        }
    })

@app.route("/predict", methods=["POST"])
@cross_origin()
def predict():
    try:
        # 1. Extract Data
        encrypted = None
        if "file" in request.files:
            f = request.files["file"]
            encrypted = f.read()
            salt = request.form.get("salt") or request.headers.get("X-SHWASNETRA-SALT")
            nonce = request.form.get("nonce") or request.headers.get("X-SHWASNETRA-NONCE")
            filename = secure_filename(f.filename or "upload.png")
        else:
            return jsonify({"error": "No file part"}), 400

        # 2. Decrypt
        decrypted = decrypt_aes_gcm_blob(encrypted, salt, nonce)
        if decrypted is None:
            return jsonify({"error": "Decryption failed. Integrity check failed."}), 400

        # Save decrypted file (optional, for debugging/records)
        fpath = os.path.join(UPLOAD_FOLDER, filename)
        with open(fpath, "wb") as out:
            out.write(decrypted)

        # ---------------------------------------------------------
        # 3. CRITICAL: CHEST FILTER LOGIC (THE FIX)
        # ---------------------------------------------------------
        if CHEST_FILTER_MODEL:
            x_chest = preprocess_image_bytes(decrypted, size=CHEST_INPUT_SIZE)
            chest_pred = safe_predict_with_model(CHEST_FILTER_MODEL, x_chest)
            
            try:
                chest_prob = float(np.squeeze(chest_pred))
            except:
                chest_prob = 0.0
            
            app.logger.info(f"DEBUG: Chest Filter Score: {chest_prob}")

            # === FIX APPLIED HERE ===
            # REJECT if Score is HIGH (> 0.5). 
            # This handles models where 1.0 = Non-Chest and 0.0 = Chest.
            if chest_prob > CHEST_FILTER_THRESHOLD:
                app.logger.warning(f"REJECTED: Non-chest image detected (Score: {chest_prob})")
                return jsonify({
                    "status": "rejected", 
                    "message": f"Security Alert: Image rejected. This appears to be a Non-Chest image (Confidence: {chest_prob*100:.2f}%)."
                }), 200

        # ---------------------------------------------------------
        # 4. Main Cancer Detection
        # ---------------------------------------------------------
        if MAIN_MODEL:
            x_main = preprocess_image_bytes(decrypted, size=MAIN_INPUT_SIZE)
            arr_main = safe_predict_with_model(MAIN_MODEL, x_main)
            
            if arr_main is None:
                return jsonify({"error": "Main model failed"}), 500
                
            idx, conf = format_probability_array(arr_main)
            label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else "Unknown"
        else:
            label, conf = "Unknown", 0.0

        # 5. Generate Grad-CAM Placeholder
        gradcam_file = f"gradcam_{filename}"
        gradcam_path = os.path.join(STATIC_FOLDER, gradcam_file)
        # Simply saving original as placeholder
        with open(fpath, "rb") as src, open(gradcam_path, "wb") as dst:
            dst.write(src.read())

        return jsonify({
            "status": "success",
            "prediction": label,
            "confidence": round(conf * 100, 2),
            "gradcam": gradcam_file,
            "message": f"Analysis Complete: {label}"
        }), 200

    except Exception as e:
        app.logger.exception("Predict Error")
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
@cross_origin()
def chat():
    try:
        data = request.get_json() or {}
        msg = data.get("message", "").strip()
        history = data.get("history", [])
        if not msg: return jsonify({"error": "Empty message"}), 400
        reply = query_llm(msg, history)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/static/heatmaps/<path:filename>", methods=["GET"])
def serve_heatmap(filename):
    return send_from_directory(STATIC_FOLDER, filename)

@app.route("/download_report", methods=["POST"])
@cross_origin()
def download_report():
    try:
        data = request.get_json(force=True)
        patient = data.get("patient", {})
        result = data.get("result", {})
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height-50, "ShwasNetra Diagnostic Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, height-100, f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}")
        c.drawString(50, height-120, f"Patient Age: {patient.get('age','N/A')}")
        c.drawString(50, height-140, f"Prediction: {result.get('result','N/A')}")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    # Ensure Port matches your Logs (8000)
    port = int(os.getenv("PORT", 8000))
    app.logger.info(f"🚀 Starting ShwasNetra Backend on Port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)