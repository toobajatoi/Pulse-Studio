"""Gemini first, Groq fallback. Always returns JSON a phone can render."""

from __future__ import annotations

import json
import os
import re
import tomllib
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
SECRETS = ROOT / ".streamlit" / "secrets.toml"
GEMINI_MODEL = "gemini-3.6-flash"
GROQ_MODEL = "openai/gpt-oss-20b"

SYSTEM = """You are Careem Studio, a senior product designer.
Design real Careem screens (Rides, Food, Quik, Pay, Plus, Captain, Delivery).
Reply with JSON only. No markdown. No HTML.

Schema:
{
  "reply": "2-4 short sentences, like ChatGPT, explaining the screen",
  "intent": "snake_case_name",
  "screen": {
    "kind": "generic",
    "label": "Home · Dubai",
    "rtl": false,
    "blocks": [
      {"type":"hello","kicker":"Good evening, Tooba","title":"Home"},
      {"type":"search","text":"Where to?"},
      {"type":"pills","items":["Ride","Food","Pay"]},
      {"type":"hero","label":"August earnings","value":"AED 186.40","meta":"+12% vs July","bars":[42,68,51,88]},
      {"type":"stats","items":[{"n":"18","l":"Trips"},{"n":"AED 1,248","l":"Spent"}]},
      {"type":"split","items":[{"n":"Rides","p":72},{"n":"Food","p":19}]},
      {"type":"list","title":"Recent","items":[{"t":"Dubai Mall","s":"Today · AED 24.50"}]},
      {"type":"note","text":"Optional helper"},
      {"type":"map"},
      {"type":"sheet","title":"Cancel this ride?","sub":"Dubai → Marina","fee":"AED 8 if you cancel now","feeNote":"Captain already accepted.","primary":"Keep this trip","secondary":"Cancel and pay AED 8"},
      {"type":"cta","text":"Book Ride","style":"primary"},
      {"type":"tabs","items":["Home","Activity","Pay","You"]}
    ]
  }
}

Rules:
- ALWAYS include a complete screen that matches the prompt. Never omit the screen.
- Riders are passengers. Captains are drivers. Rider "earnings" means spend + Plus cashback unless the prompt says captain or driver.
- Home/dashboard: max 6 blocks. Checkout: max 6.
- Accept-ride, in-trip, and cancel screens MUST be map + one sheet only. Put fare, pickup, drop-off, and both CTAs inside the sheet. Never stack hello, stats, hero, and sheet — the phone cannot scroll.
- Pickup and drop-off MUST be real street addresses (e.g. "Dubai Mall, Financial Centre Rd"), never the word "Pickup" or a lone pin.
- Always write the screen in English. The product has its own EN/AR toggle. Do not switch language unless the user only asked to change copy inside a field.
- Careem light UI. Realistic UAE/KSA/Egypt copy and currency when relevant.
- If the user asks Arabic, set rtl true and write Arabic copy.
- Follow-ups edit the last screen instead of starting over.
- Fee, fare, or earnings stay visible. No dark patterns.
- Keep labels short.
- You co-design with a human. Adapt hard to their Design DNA. Mention what you adapted.
- Also return:
  "critic": {"score": 90, "note": "one sentence vs Careem DNA + their style"},
  "choices": [
    {"id":"learn","label":"Learn this style"},
    {"id":"compact","label":"Make it more compact"},
    {"id":"clear","label":"Show the number sooner"}
  ]
- Give 2-3 choices that steer style, not a new product.
- If DNA says compact, fewer words, tighter blocks. If comfortable, more air and helper copy.
- If DNA says numbers-first, put fare/fee/earnings in the first hero or sheet."""


def _keys() -> dict:
    keys = {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", ""),
        "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", ""),
    }
    if keys["GEMINI_API_KEY"] and keys["GROQ_API_KEY"]:
        return keys
    if SECRETS.exists():
        local = tomllib.loads(SECRETS.read_text(encoding="utf-8"))
        keys["GEMINI_API_KEY"] = keys["GEMINI_API_KEY"] or str(local.get("GEMINI_API_KEY") or "")
        keys["GROQ_API_KEY"] = keys["GROQ_API_KEY"] or str(local.get("GROQ_API_KEY") or "")
    return keys


def _timeout() -> int:
    try:
        return max(6, int(os.environ.get("LLM_TIMEOUT", "32")))
    except ValueError:
        return 32


def _parse(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I)
    match = re.search(r"\{.*\}", cleaned, re.S)
    if not match:
        raise ValueError("no json")
    return json.loads(match.group(0))


def _gemini(prompt: str) -> str:
    key = _keys()["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM}\n\n{prompt}"}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048, "responseMimeType": "application/json"},
    }
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        timeout=_timeout(),
    )
    response.raise_for_status()
    parts = response.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def _groq(prompt: str) -> str:
    key = _keys()["GROQ_API_KEY"]
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": GROQ_MODEL,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt},
            ],
        },
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        timeout=_timeout(),
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def design(question: str, history: list | None = None, dna: dict | None = None) -> tuple[dict, str]:
    prior = ""
    if history:
        bits = []
        for row in history[-8:]:
            role = row.get("role", "user")
            bits.append(f"{role}: {row.get('content', '')}")
        prior = "Recent chat:\n" + "\n".join(bits) + "\n\n"
    style = json.dumps(dna or {}, ensure_ascii=False)
    prompt = f"{prior}Design DNA (adapt to this human): {style}\nDesigner: {question}\nReturn the JSON schema now."
    errors = []
    for name, fn in (("Gemini · 3.6 flash", _gemini), ("Groq · gpt-oss-20b", _groq)):
        try:
            data = _parse(fn(prompt))
            if not isinstance(data, dict) or not data.get("screen"):
                raise ValueError("missing screen")
            data["reply"] = str(data.get("reply") or "Here is the screen.")
            data["intent"] = str(data.get("intent") or "screen")
            return data, name
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    raise RuntimeError(" | ".join(errors))
