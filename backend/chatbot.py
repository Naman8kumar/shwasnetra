"""chatbot.py — unified multilingual AI assistant for ShwasNetra backend
Supports: Groq (primary), OpenAI (fallback), HuggingFace (backup)
"""

import os
import requests
from dotenv import load_dotenv
import logging

# Optional translation
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except Exception:
    GoogleTranslator = None
    DEEP_TRANSLATOR_AVAILABLE = False

# Load environment variables
load_dotenv()

logger = logging.getLogger("shwasnetra_chatbot")
logger.setLevel(logging.INFO)

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """
You are **ShwasNetra AI Assistant** — a trusted, multilingual, medically informed companion
specializing in **lung health and X-ray/CT scan analysis**.

You:
- Explain AI predictions and imaging in simple human terms.
- Help users understand lung cancer risks, prevention, screening.
- Provide educational information — never direct diagnoses.
- Maintain empathy, cultural sensitivity, and professional tone.
- Always encourage consultation with certified medical professionals.

If the question is unrelated to health, respond briefly but politely.
"""

# ----------------------------------------
# Helpers
# ----------------------------------------

def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text safely using deep_translator if available."""
    if not text or src_lang == tgt_lang:
        return text
    if not DEEP_TRANSLATOR_AVAILABLE:
        return text
    try:
        translator = GoogleTranslator(source=src_lang, target=tgt_lang)
        return translator.translate(text)
    except Exception as e:
        logger.warning(f"Translation failed {src_lang}->{tgt_lang}: {e}")
        return text

# ----------------------------------------
# Core Chat Function
# ----------------------------------------

def ask_chatbot(messages: list, lang: str = "en") -> str:
    """
    Chat with ShwasNetra AI assistant using the full conversation history.
    - messages: list of dicts [{"role": "user"|"assistant", "content": "..."}]
    - lang: language code for user
    """

    lang = str(lang).split("-")[0].lower() or "en"

    # Compose full "messages" for API: always start with system prompt
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        if msg["role"] == "user":
            api_messages.append({
                "role": "user",
                "content": translate_text(msg["content"], src_lang=lang, tgt_lang="en")
            })
        else:
            # Do not translate assistant (already in English internally), or you can store both versions if needed
            api_messages.append({
                "role": "assistant",
                "content": msg["content"]
            })

    # ----------- Primary: Groq ----------
    if GROQ_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": GROQ_MODEL,
                "messages": api_messages,
                "temperature": 0.6,
                "max_tokens": 600
            }
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json=payload, timeout=30
            )
            if resp.status_code == 200:
                js = resp.json()
                ai_text = js.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if ai_text:
                    # Translate back to user lang if needed
                    return translate_text(ai_text, src_lang="en", tgt_lang=lang)
        except Exception as e:
            logger.warning(f"Groq error: {e}")

    # ----------- Fallback: OpenAI ----------
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            resp = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=api_messages,
                temperature=0.6,
                max_tokens=600
            )
            ai_text = resp["choices"][0]["message"]["content"].strip()
            return translate_text(ai_text, src_lang="en", tgt_lang=lang)
        except Exception as e:
            logger.warning(f"OpenAI fallback failed: {e}")

    # ----------- Final fallback: HuggingFace ----------
    if HUGGINGFACE_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            # For huggingface, send flat text history (or adapt to model requirements)
            history_text = ""
            for msg in messages:
                prefix = "User:" if msg["role"]=="user" else "Assistant:"
                history_text += f"{prefix} {translate_text(msg['content'], src_lang=lang, tgt_lang='en')}\n"
            payload = {"inputs": history_text + "Assistant:", "parameters": {"max_new_tokens": 250}}
            hf_resp = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers=headers,
                json=payload,
                timeout=30
            )
            if hf_resp.status_code == 200:
                out = hf_resp.json()
                if isinstance(out, list) and len(out) > 0 and "generated_text" in out[0]:
                    ai_text = out[0]["generated_text"].strip()
                elif isinstance(out, dict) and "generated_text" in out:
                    ai_text = out["generated_text"].strip()
                else:
                    ai_text = str(out)
                return translate_text(ai_text, src_lang="en", tgt_lang=lang)
        except Exception as e:
            logger.warning(f"HuggingFace fallback failed: {e}")

    # ----------- Ultimate fallback ----------
    return translate_text(
        "I'm temporarily offline. Please try again later or check your network connection.",
        src_lang="en",
        tgt_lang=lang,
    )

# ----------------------------------------
# CLI test mode
# ----------------------------------------
if __name__ == "__main__":
    print("🩺 ShwasNetra AI Assistant (CLI mode)\n")
    history = [
        {"role": "assistant", "content": "👋 Hello! I'm here to help you understand lung scans and health insights. How can I assist you today?"}
    ]
    while True:
        try:
            q = input("You: ").strip()
            if not q:
                continue
            if q.lower() in ("exit", "quit"):
                break
            history.append({"role": "user", "content": q})
            reply = ask_chatbot(history, lang="en")
            print(f"AI: {reply}\n")
            history.append({"role": "assistant", "content": reply})
        except KeyboardInterrupt:
            print("\nExiting...")
            break
