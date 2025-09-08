import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env if available
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow all origins for frontend access

# Get API Key from environment
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("❌ Please set GEMINI_API_KEY as an environment variable.")

# Gemini 2.5 endpoint (you can change model if needed)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_KEY}"

@app.route("/")
def home():
    return jsonify({
        "status": "✅ Gemini Proxy Running",
        "endpoint": "/api/gemini"
    })

@app.route("/api/gemini", methods=["POST"])
def call_gemini():
    try:
        data = request.get_json()
        text = data.get("text", "")
        lang = data.get("lang", "en")
        context = data.get("context", [])

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Build context prompt
        context_str = ""
        if context and isinstance(context, list):
            context_str = "\n\nHere is some product info:\n"
            for c in context[:5]:
                item = c.get("item", "")
                tamil = c.get("tamil_name", "")
                price = c.get("price", "")
                unit = c.get("unit", "")
                context_str += f"- {item} ({tamil}) : ₹{price}/{unit}\n"

        # Final prompt
        prompt = f"User asked in {lang}: {text}\n{context_str}\nAnswer shortly and clearly."

        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        resp = requests.post(GEMINI_URL, json=payload)
        resp.raise_for_status()

        result = resp.json()

        # Extract reply text
        reply = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "No reply")
        )

        return jsonify({"reply": reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"❌ Gemini API request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"❌ Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
