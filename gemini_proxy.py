from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests
from dotenv import load_dotenv

# Load .env for local dev (Render dashboard handles env vars in production)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Gemini API Key
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("❌ Please set GEMINI_API_KEY in environment variables")

# Gemini model endpoint
MODEL_NAME = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GEMINI_KEY}"

@app.route("/api/gemini", methods=["POST"])
def proxy_gemini():
    """Proxy endpoint to call Google Gemini API"""
    data = request.get_json() or {}
    text = data.get("text", "")
    lang = data.get("lang", "en")

    # Prompt with language
    prompt = f'{"தமிழில் சுருக்கமாக பதில்:" if lang=="ta" else "Answer shortly:"} {text}'
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(GEMINI_URL, json=body, timeout=15)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return jsonify({"endpoint": "/api/gemini", "status": "✅ Gemini Proxy Running"})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
