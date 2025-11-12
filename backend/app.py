import os
import io
import json
import traceback
import binascii
import hashlib
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import tensorflow as tf
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import logging
import sys

# -------------------------
# Logging
# -------------------------
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------
# Flask App + CORS
# -------------------------
app = Flask(__name__)

# allow production frontend + local dev origins
CORS(app, resources={r"/*": {"origins": [
    "https://shwasnetra.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8083",
    "http://127.0.0.1:8083"
]}}, supports_credentials=True)

# limit upload size to 50 MB
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

# -------------------------
# Paths & Config
# -------------------------
# Use backend dir as base so paths are consistent on Render
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static", "heatmaps")
MODEL_DIR = os.path.join(BASE_DIR, "model_training")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Encryption (default as requested)
ENCRYPTION_PASSWORD = b"shwasnetra2025"
PBKDF2_ITERS = 200_000

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.2-70b-versatile").strip()
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()

CLASS_NAMES = ["Normal", "Benign", "Malignant", "Unchest"]
CHEST_FILTER_THRESHOLD = 0.5  # threshold for chest filter model

# -------------------------
# Model Loading
# -------------------------
def load_model_safe(path):
    try:
        if not os.path.exists(path):
            app.logger.info(f"[model] not found: {path}")
            return None
        app.logger.info(f"[model] loading: {path}")
        model = tf.keras.models.load_model(path)
        app.logger.info(f"[model] loaded: {path} input_shape={getattr(model, 'input_shape', None)}")
        return model
    except Exception as e:
        app.logger.exception(f"[model] failed to load {path}: {e}")
        return None

CHEST_MODEL_PATH = os.path.join(MODEL_DIR, "chest_filter_model.keras")
MAIN_MODEL_PATH = os.path.join(MODEL_DIR, "lung_cancer_detector_mobilenetv2_full.keras")

CHEST_FILTER_MODEL = load_model_safe(CHEST_MODEL_PATH)
MAIN_MODEL = load_model_safe(MAIN_MODEL_PATH)

# sensible defaults; may be overridden by loaded model shapes
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

app.logger.info(f"CHEST_INPUT_SIZE={CHEST_INPUT_SIZE} MAIN_INPUT_SIZE={MAIN_INPUT_SIZE} "
                f"CHEST_MODEL_LOADED={bool(CHEST_FILTER_MODEL)} MAIN_MODEL_LOADED={bool(MAIN_MODEL)}")

# -------------------------
# AES Decryption
# -------------------------
def derive_key(password: bytes, salt: bytes, iters=PBKDF2_ITERS):
    return hashlib.pbkdf2_hmac("sha256", password, salt, iters, dklen=32)

def decrypt_aes_gcm_blob(blob: bytes, salt_hex: Optional[str], nonce_hex: Optional[str]) -> Optional[bytes]:
    """
    Expect frontend to send salt & nonce as hex strings (form fields or headers).
    If you use a different packaging/schema, adjust accordingly.
    """
    try:
        if not salt_hex or not nonce_hex:
            app.logger.warning("[decrypt] missing salt or nonce")
            return None
        salt = binascii.unhexlify(salt_hex)
        nonce = binascii.unhexlify(nonce_hex)
        key = derive_key(ENCRYPTION_PASSWORD, salt)
        aesgcm = AESGCM(key)
        # AESGCM expects ciphertext+tag combined.
        return aesgcm.decrypt(nonce, blob, None)
    except Exception as e:
        app.logger.exception(f"[decrypt] failed: {e}")
        return None

# -------------------------
# Preprocessing & Prediction Helpers
# -------------------------
def preprocess_image_bytes(image_bytes: bytes, size=(224,224)):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(size)
        arr = np.array(img).astype(np.float32) / 255.0
        return np.expand_dims(arr, 0)
    except Exception as e:
        app.logger.exception(f"[preprocess] {e}")
        return None

def safe_predict_with_model(model, x):
    try:
        if model is None:
            return None
        preds = model.predict(x, verbose=0)
        return np.squeeze(np.asarray(preds))
    except Exception as e:
        app.logger.exception(f"[predict] failed: {e}")
        return None

def format_probability_array(arr):
    try:
        a = np.asarray(arr)
        if a.ndim == 0:
            return 0, float(a)
        idx = int(np.argmax(a))
        conf = float(np.max(a))
        return idx, conf
    except Exception as e:
        app.logger.exception(f"[format_prob] {e}")
        return 0, 0.0

# -------------------------
# Chatbot Function (Grok/OpenAI)
# -------------------------
def query_llm(prompt: str, history: Optional[list] = None):
    messages = [{"role":"system","content":"You are ShwasAI, a medically-safe, empathetic assistant for lung health."}]
    if history:
        for h in history[-6:]:
            if "user" in h: messages.append({"role":"user","content":h["user"]})
            if "bot" in h: messages.append({"role":"assistant","content":h["bot"]})
    messages.append({"role":"user","content":prompt})

    if GROQ_API_KEY:
        try:
            payload = {"model": GROQ_MODEL, "messages": messages, "temperature": 0.5, "max_tokens": 400}
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            app.logger.warning(f"[groq] {e}")

    if OPENAI_KEY:
        try:
            payload = {"model":"gpt-4o-mini","messages":messages,"temperature":0.5,"max_tokens":400}
            headers = {"Authorization": f"Bearer {OPENAI_KEY}","Content-Type":"application/json"}
            r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=20)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            app.logger.warning(f"[openai] {e}")

    return "I'm currently offline — please try again later."

# -------------------------
# Routes
# -------------------------
@app.get("/health")
def health():
    """
    Lightweight health endpoint for Render and monitoring.
    """
    return jsonify(status="ok", service="shwasnetra-backend"), 200

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "ok",
        "main_model_loaded": bool(MAIN_MODEL),
        "chest_model_loaded": bool(CHEST_FILTER_MODEL),
        "chest_input": CHEST_INPUT_SIZE,
        "main_input": MAIN_INPUT_SIZE
    })

@app.route("/predict", methods=["POST"])
@cross_origin()
def predict():
    """
    Accepts either multipart form with:
      - file (uploaded blob)
      - salt (hex)
      - nonce (hex)
    OR raw application/octet-stream with salt & nonce passed as headers:
      X-SHAWASNETRA-SALT: <hex>
      X-SHAWASNETRA-NONCE: <hex>
    """
    try:
        # Support both multipart file and raw binary body
        encrypted = None
        salt = None
        nonce = None
        filename = None

        # If multipart form upload (recommended)
        if "file" in request.files:
            f = request.files["file"]
            encrypted = f.read()
            salt = request.form.get("salt") or request.headers.get("X-SHWASNETRA-SALT")
            nonce = request.form.get("nonce") or request.headers.get("X-SHWASNETRA-NONCE")
            filename = secure_filename(f.filename or f"upload_{datetime.utcnow().timestamp()}.png")
        else:
            # raw bytes case
            encrypted = request.get_data()
            salt = request.headers.get("X-SHWASNETRA-SALT") or request.args.get("salt")
            nonce = request.headers.get("X-SHWASNETRA-NONCE") or request.args.get("nonce")
            filename = f"upload_{int(datetime.utcnow().timestamp())}.png"

        if not encrypted:
            return jsonify({"error": "No payload received"}), 400

        # Attempt to decrypt
        decrypted = decrypt_aes_gcm_blob(encrypted, salt, nonce)
        if decrypted is None:
            # If decryption fails, return meaningful error
            return jsonify({"error": "Decryption failed - check salt/nonce or encryption scheme"}), 400

        # Persist decrypted upload for traceability
        fpath = os.path.join(UPLOAD_FOLDER, filename)
        with open(fpath, "wb") as out:
            out.write(decrypted)

        # Chest filter model (optional)
        if CHEST_FILTER_MODEL:
            x_chest = preprocess_image_bytes(decrypted, size=CHEST_INPUT_SIZE)
            if x_chest is None:
                return jsonify({"error": "Failed to preprocess chest image"}), 400
            chest_pred = safe_predict_with_model(CHEST_FILTER_MODEL, x_chest)
            try:
                chest_prob = float(np.squeeze(chest_pred))
            except Exception:
                chest_prob = 0.0
            # If model suggests NOT a chest x-ray (threshold logic as used earlier)
            if chest_prob < CHEST_FILTER_THRESHOLD:
                # NOTE: logic preserved from original but inverted threshold if desired adjust
                pass  # continue normally
            # If you instead want to reject when chest_prob indicates not-chest, adjust here.

        # Main prediction
        if MAIN_MODEL:
            x_main = preprocess_image_bytes(decrypted, size=MAIN_INPUT_SIZE)
            if x_main is None:
                return jsonify({"error": "Failed to preprocess main image"}), 400
            arr_main = safe_predict_with_model(MAIN_MODEL, x_main)
            if arr_main is None:
                return jsonify({"error": "Model inference failed"}), 500
            idx, conf = format_probability_array(arr_main)
            label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else "Unknown"
        else:
            # fallback dummy response if model not available
            label = "Unknown"
            conf = 0.0

        # Save a simple gradcam placeholder (actual Grad-CAM generation optional)
        try:
            gradcam_path = os.path.join(STATIC_FOLDER, f"gradcam_{filename}.png")
            Image.open(io.BytesIO(decrypted)).convert("RGB").save(gradcam_path)
            gradcam_file = os.path.basename(gradcam_path)
        except Exception as e:
            app.logger.exception("Failed to write gradcam placeholder")
            gradcam_file = None

        return jsonify({
            "status": "success",
            "prediction": label,
            "confidence": round(conf * 100, 2),
            "gradcam": gradcam_file,
            "message": f"AI Prediction: {label} ({conf * 100:.2f}%)"
        }), 200

    except Exception as e:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

@app.route("/chat", methods=["POST"])
@cross_origin()
def chat():
    try:
        data = request.get_json() or {}
        msg = data.get("message", "").strip()
        history = data.get("history", [])
        if not msg:
            return jsonify({"error": "Empty message"}), 400
        reply = query_llm(msg, history)
        return jsonify({"reply": reply})
    except Exception as e:
        app.logger.exception("Chat failed")
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
        ai_explanation = data.get("ai_explanation", "")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height-60, "🫁 ShwasNetra AI Diagnostic Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, height-100, f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        y = height-140
        c.drawString(50, y, f"Age: {patient.get('age','N/A')}  Gender: {patient.get('gender','N/A')}")
        y -= 20
        c.drawString(50, y, f"Smoking: {patient.get('smoking','N/A')}  Cough: {patient.get('cough','N/A')}")
        y -= 30
        c.drawString(50, y, f"Result: {result.get('result','N/A')}  Confidence: {result.get('confidence','N/A')}%")
        y -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "AI Explanation:")
        y -= 20
        c.setFont("Helvetica", 11)
        text = c.beginText(60, y)
        for line in ai_explanation.splitlines():
            text.textLine(line)
        c.drawText(text)
        c.showPage()
        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="ShwasNetra_Report.pdf", mimetype="application/pdf")
    except Exception:
        app.logger.exception("Report generation failed")
        return jsonify({"error": "Report generation failed"}), 500

# -------------------------
# Run Server (for local dev)
# -------------------------
if __name__ == "__main__":
    # Local debug mode uses the injected PORT env when present
    port = int(os.getenv("PORT", 8000))
    app.logger.info(f"Starting ShwasNetra Backend (LOCAL) | PORT={port} | CHEST_MODEL={bool(CHEST_FILTER_MODEL)} MAIN_MODEL={bool(MAIN_MODEL)}")
    app.run(host="0.0.0.0", port=port, debug=True)
