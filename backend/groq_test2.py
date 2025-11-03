import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

data = {
    "model": "llama-3.1-8b-instant",
    "messages": [
        {"role": "system", "content": "You are ShwasNetra AI, a helpful medical assistant."},
        {"role": "user", "content": "Who are you?"}
    ],
    "temperature": 0.6,
    "max_tokens": 200
}

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    },
    data=json.dumps(data)
)

print(f"Status: {response.status_code}")
try:
    resp_json = response.json()
    print(json.dumps(resp_json, indent=2))
except Exception:
    print("Raw Response:", response.text)
