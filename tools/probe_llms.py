"""Probe Gemini and Groq without printing secrets."""

from __future__ import annotations

import tomllib
from pathlib import Path

import requests

SECRETS = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
data = tomllib.loads(SECRETS.read_text(encoding="utf-8"))
gkey = data.get("GEMINI_API_KEY", "")
groq = data.get("GROQ_API_KEY", "")

for model in ("gemini-3.6-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    try:
        r = requests.post(
            url,
            json={"contents": [{"parts": [{"text": 'Reply JSON only: {"ok":true}'}]}]},
            headers={"Content-Type": "application/json", "x-goog-api-key": gkey},
            timeout=25,
        )
        print("GEMINI", model, r.status_code, r.text[:140].replace("\n", " "))
        if r.status_code == 200:
            break
    except Exception as exc:
        print("GEMINI", model, type(exc).__name__)

try:
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": "openai/gpt-oss-20b",
            "messages": [{"role": "user", "content": 'Reply JSON only: {"ok":true}'}],
            "temperature": 0.2,
        },
        headers={"Authorization": f"Bearer {groq}", "Content-Type": "application/json"},
        timeout=25,
    )
    print("GROQ", r.status_code, r.text[:140].replace("\n", " "))
except Exception as exc:
    print("GROQ", type(exc).__name__)
