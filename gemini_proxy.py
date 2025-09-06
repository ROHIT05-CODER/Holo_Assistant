# gemini_proxy.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests

app = Flask(__name__, static_folder=".")
CORS(app)

# ✅ Gemini API Key (set in Render Environment Variables)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    raise ValueError("❌ Please set GEMINI_API_KEY as an environment variable in Render.")

# ✅ Use latest Gemini endpoint (2.5)
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "gemini-2.5-pro:generateContent?key=" + GEMINI_KEY
)

# === Gemini Proxy API ===
@app.route("/api/gemini", methods=["POST"])
def proxy_gemini():
    data = request.get_json() or {}
    text = data.get("text", "")
    lang = data.get("lang", "en")

    prompt = f'{"தமிழில் சுருக்கமான பதில்:" if lang=="ta" else "Answer shortly:"} {text}'
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        print("➡️ Sending to Gemini:", body)  # Debug log
        resp = requests.post(GEMINI_URL, json=body, timeout=15)
        resp.raise_for_status()
        response_json = resp.json()
        print("⬅️ Gemini Response:", response_json)  # Debug log
        return jsonify(response_json)
    except Exception as e:
        print("❌ Gemini Error:", str(e))
        return jsonify({"error": str(e)}), 500

# === Serve Static Files (HTML, JSON, MP4, etc.) ===
@app.route("/")
def serve_index():
    return send_from_directory(".", "holo_assistant.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)

# === Health Check ===
@app.route("/health")
def health():
    return "✅ Holo Assistant server running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
