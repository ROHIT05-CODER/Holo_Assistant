from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Gemini API Key (from .env)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("❌ Please set GEMINI_API_KEY in .env file")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=" + GEMINI_KEY
)


@app.route("/api/gemini", methods=["POST"])
def proxy_gemini():
    data = request.get_json() or {}
    text = data.get("text", "")
    lang = data.get("lang", "en")

    prompt = f'{"தமிழில் சுருக்கமான பதில்:" if lang=="ta" else "Answer shortly:"} {text}'
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        print("➡️ Sending to Gemini:", body)   # Debug log
        resp = requests.post(GEMINI_URL, json=body, timeout=15)
        print("⬅️ Gemini Response:", resp.text) # Debug log
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        print("❌ Gemini Error:", str(e))       # Debug log
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ Gemini Proxy Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
