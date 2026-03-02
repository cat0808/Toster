import base64
import json
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent

AUDIO_EXT = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}
VIDEO_EXT = {".mp4", ".avi", ".mkv", ".mov", ".webm"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID", "")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET", "")

app = Flask(__name__)


def scan_files(extensions: set[str]) -> list[Path]:
    result: list[Path] = []
    for path in BASE_DIR.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions and "venv" not in path.parts and ".git" not in path.parts:
            result.append(path)
    return sorted(result)


def rel_list(paths: list[Path]) -> list[str]:
    return [str(p.relative_to(BASE_DIR)).replace("\\", "/") for p in paths]


def gigachat_token() -> str:
    import requests

    if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
        raise ValueError("Set GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET")

    basic = base64.b64encode(f"{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}".encode()).decode()
    response = requests.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers={
            "Authorization": f"Basic {basic}",
            "RqUID": "multimedia-web-rquid",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"scope": "GIGACHAT_API_PERS"},
        timeout=25,
        verify=False,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def gigachat_chat(token: str, prompt: str) -> str:
    import requests

    response = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=json.dumps(
            {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 600,
            }
        ),
        timeout=40,
        verify=False,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


@app.get("/")
def index():
    return render_template(
        "index.html",
        audio_files=rel_list(scan_files(AUDIO_EXT)),
        video_files=rel_list(scan_files(VIDEO_EXT)),
        image_files=rel_list(scan_files(IMAGE_EXT)),
    )


@app.get("/media/<path:filename>")
def media_file(filename: str):
    return send_from_directory(BASE_DIR, filename)


@app.post("/api/ai")
def ai_chat():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    try:
        token = gigachat_token()
        answer = gigachat_chat(token, prompt)
        return jsonify({"answer": answer})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
