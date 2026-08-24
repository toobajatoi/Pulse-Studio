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
OPENROUTER_MODELS = [
    os.environ.get("OPENROUTER_MODEL") or "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemini-2.5-pro",
]
GEMINI_MODELS = [
    os.environ.get("GEMINI_MODEL") or "gemini-3.1-pro-preview",
    "gemini-3.6-flash",
]
GROQ_MODELS = [
    os.environ.get("GROQ_MODEL") or "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]

SYSTEM = """You are Careem Studio, a senior product designer.
Design real Careem screens that look production-ready, not wireframes.
Reply with JSON only. No markdown. No HTML.

Schema:
{
  "reply": "2-4 short sentences explaining what you designed",
  "intent": "snake_case_name",
  "design_system": {
    "name": "Food Home",
    "product": "Food",
    "layout": "One line describing structure",
    "tokens": {"primary": "#00E784", "text": "#1F1F1F", "radius": "16px"},
    "typography": {"title": "22/28 Medium", "body": "14/20 Regular"},
    "components": [{"name": "SearchField", "spec": "What it does on this screen"}],
    "rules": ["Max 2 CTAs", "Fee before pay when relevant"]
  },
  "screen": {
    "kind": "generic",
    "label": "Food · Dubai",
    "rtl": false,
    "blocks": []
  }
}

Block types — compose ONLY what the brief needs (5-10 blocks typical):
- hello: {kicker, title}  strings only
- location: {text}  string
- search: {text}  string
- pills or categories: {items:["Rides","Food"]}  items MUST be strings, never objects
- offer: {text}  string promo, never a chart
- section: {title}  string
- restaurants: {title, items:[{name, rating, eta, from, dish, tag}]}  every card needs name, rating, eta, from
- hero: {label, value, meta, bars?} ONLY earnings dashboards
- stats / split: ONLY earnings dashboards
- list: {title, items:[{t,s}]}  t and s are strings
- map: {}
- sheet: {title, sub, fee?, feeNote?, primary, secondary?}  all strings
- captain: {name, rating, car, plate}  all strings
- trip: {pickup, dest, fare, duration, distance, method}  duration like "24 min", distance like "12 km"
- rating: {value: 5}
- tips: {items:["AED 5","AED 10","AED 15"]}  strings only
- totals: {rows:[{label,value}]}  strings
- note: {text}
- cta: {text, style?}  text is a short string like "Done" — never mix fare into the button
- tabs: {items:["Home","Activity","Pay","You"]}  strings only

Hard rules:
- items[] for pills/categories/tabs/tips is ALWAYS an array of strings. Never {name,icon} objects.
- Food home MUST include location, search, categories (string chips), offer, and restaurants cards with name+rating+eta+from. Never use SearchField or RestaurantCard as a type name.
- Super App home: hello, search "Where to?", pills ["Rides","Food","Quik","Pay","Shops","Plus","Bike","Box"], offer, list of recent places, tabs.
- Food search: search, categories as filter chips (strings), restaurants cards with rating+ETA+price. Do not use pills-as-objects.
- Ride completed: hello with fare, trip (pickup/dest/fare/duration/distance/method), captain, rating, tips, ONE cta "Done". No sheet. No Pay button on top of the fare.
- ALWAYS return blocks[] that fully match the user brief.
- NEVER paste the user's prompt as a title. Never return a lone Continue button.
- NEVER return an earnings dashboard unless the brief asks for earnings/monthly stats.
- Promos use offer text, never bar charts.
- Always write English. rtl false unless the user asked for Arabic.
- Realistic UAE copy and AED. Keep labels short. Max 2 CTAs.
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
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY") or os.environ.get("NVIDIA_API_KEY", ""),
    }
    if SECRETS.exists():
        local = tomllib.loads(SECRETS.read_text(encoding="utf-8"))
        keys["GEMINI_API_KEY"] = keys["GEMINI_API_KEY"] or str(local.get("GEMINI_API_KEY") or "")
        keys["GROQ_API_KEY"] = keys["GROQ_API_KEY"] or str(local.get("GROQ_API_KEY") or "")
        keys["OPENROUTER_API_KEY"] = (
            keys["OPENROUTER_API_KEY"]
            or str(local.get("OPENROUTER_API_KEY") or "")
            or str(local.get("NVIDIA_API_KEY") or "")
        )
    return keys


def _timeout() -> int:
    try:
        return max(12, int(os.environ.get("LLM_TIMEOUT", "48")))
    except ValueError:
        return 48


def _parse(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I)
    match = re.search(r"\{.*\}", cleaned, re.S)
    if not match:
        raise ValueError("no json")
    return json.loads(match.group(0))


def _gemini(prompt: str, model: str) -> str:
    key = _keys()["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": f"{SYSTEM}\n\n{prompt}"}]}],
        "generationConfig": {"temperature": 0.25, "maxOutputTokens": 4096, "responseMimeType": "application/json"},
    }
    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        timeout=_timeout(),
    )
    if response.status_code == 429:
        raise RuntimeError("Gemini quota exceeded")
    response.raise_for_status()
    parts = response.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def _openrouter(prompt: str, model: str) -> str:
    key = _keys()["OPENROUTER_API_KEY"]
    if not key:
        raise RuntimeError("OpenRouter key missing")
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8787",
        "X-Title": "Pulse Studio",
    }
    body = {
        "model": model,
        "temperature": 0.25,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        json={**body, "response_format": {"type": "json_object"}},
        headers=headers,
        timeout=_timeout(),
    )
    if response.status_code >= 400:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=body,
            headers=headers,
            timeout=_timeout(),
        )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _groq(prompt: str, model: str) -> str:
    key = _keys()["GROQ_API_KEY"]
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": model,
            "temperature": 0.25,
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
    prompt = f"{prior}Design DNA (adapt to this human): {style}\nDesigner: {question}\nReturn production-quality Careem JSON now. items[] must be strings."
    errors = []
    chain = []
    if _keys().get("OPENROUTER_API_KEY"):
        chain += [(f"NVIDIA · {model}", lambda p, m=model: _openrouter(p, m)) for model in OPENROUTER_MODELS]
    chain += [(f"Gemini · {model}", lambda p, m=model: _gemini(p, m)) for model in GEMINI_MODELS]
    chain += [(f"Groq · {model}", lambda p, m=model: _groq(p, m)) for model in GROQ_MODELS]
    skip_gemini = False
    for name, fn in chain:
        if skip_gemini and name.startswith("Gemini"):
            continue
        try:
            data = _parse(fn(prompt))
            if not isinstance(data, dict) or not data.get("screen"):
                raise ValueError("missing screen")
            data["reply"] = str(data.get("reply") or "Here is the screen.")
            data["intent"] = str(data.get("intent") or "screen")
            return data, name
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            if "quota exceeded" in str(exc).lower():
                skip_gemini = True
    raise RuntimeError(" | ".join(errors))
