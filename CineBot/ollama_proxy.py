"""Password-protected local gateway between Render and local Ollama."""
import hmac
import os
import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request

load_dotenv()
TOKEN = os.getenv("OLLAMA_PROXY_TOKEN", "")
OLLAMA_BASE = os.getenv("OLLAMA_LOCAL_BASE", "http://127.0.0.1:11434").rstrip("/")
PORT = int(os.getenv("OLLAMA_PROXY_PORT", "11435"))
app = Flask(__name__)

@app.before_request
def require_token():
    supplied = request.headers.get("Authorization", "")
    if not TOKEN or not hmac.compare_digest(supplied, f"Bearer {TOKEN}"):
        return jsonify({"error": "Unauthorized"}), 401

@app.get("/api/tags")
def tags():
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=10)
        return Response(r.content, status=r.status_code,
                        content_type=r.headers.get("Content-Type", "application/json"))
    except requests.RequestException as exc:
        return jsonify({"error": f"Local Ollama unavailable: {type(exc).__name__}"}), 502

@app.post("/api/chat")
def chat():
    try:
        r = requests.post(f"{OLLAMA_BASE}/api/chat",
                          json=request.get_json(silent=True) or {}, timeout=240)
        return Response(r.content, status=r.status_code,
                        content_type=r.headers.get("Content-Type", "application/json"))
    except requests.RequestException as exc:
        return jsonify({"error": f"Local Ollama unavailable: {type(exc).__name__}"}), 502

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Set OLLAMA_PROXY_TOKEN in your local .env first.")
    print(f"Gateway listening on 127.0.0.1:{PORT}; do not expose Ollama port 11434.")
    app.run(host="127.0.0.1", port=PORT, debug=False)
