"""Free LLM for Pulse. Returns short structured objects, not essays."""

from __future__ import annotations

import json
import re

import requests

from engine import analyze, generate_copy, generate_layouts

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
POLLINATIONS_URL = "https://text.pollinations.ai/v1/chat/completions"

SYSTEM = """You are a product designer. Reply with JSON only. No markdown.
Use only the notes. Short labels. No essays. No dark patterns."""


def notes_block(rows: list[dict], limit: int = 8) -> str:
    return "\n".join(
        f"{row['id']}|{row['city']}|{row['screen']}|{row['severity']}|{row['quote']}"
        for row in rows[:limit]
    )


def summarize_prompt(rows: list[dict]) -> str:
    return f"""Notes:
{notes_block(rows)}

JSON:
{{"themes":[{{"name":"","count":1,"severity":"high","quote":"","fix":""}}],"wins":[{{"change":""}}]}}
Max 3 themes. Max 3 wins. quote under 12 words. fix under 8 words. change under 8 words."""


def copy_prompt(rows: list[dict], screen: str, language: str) -> str:
    return f"""Write UI copy for {screen}. Language: {language}
Notes:
{notes_block(rows, 6)}

JSON:
{{"headline":"","helper":"","cta":"","empty":"","error":""}}
headline max 6 words. helper max 12 words. others max 8 words."""


def layout_prompt(rows: list[dict], screen: str) -> str:
    return f"""3 layouts for {screen}.
Notes:
{notes_block(rows, 6)}

JSON:
{{"layouts":[{{"name":"","structure":["","","",""]}}]}}
name max 4 words. each structure part max 5 words. exactly 3 layouts."""


def parse_json(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.S)
    if not match:
        raise ValueError("no json")
    return json.loads(match.group(0))


def complete(user_prompt: str, groq_key: str | None = None) -> tuple[dict, str]:
    key = (groq_key or "").strip()
    if key:
        raw = _chat(
            GROQ_URL,
            user_prompt,
            "openai/gpt-oss-20b",
            {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=60,
            json_mode=True,
        )
        return parse_json(raw), "Groq · gpt-oss-20b"
    raw = _chat(
        POLLINATIONS_URL,
        user_prompt,
        "openai-fast",
        {"User-Agent": "curl/8.0", "Content-Type": "application/json"},
        timeout=12,
        json_mode=False,
    )
    return parse_json(raw), "Pollinations"


def _chat(url: str, user_prompt: str, model: str, headers: dict, timeout: int, json_mode: bool) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    session = requests.Session()
    session.trust_env = False
    response = session.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def fallback_summary(rows: list[dict]) -> dict:
    themes = []
    for item in analyze(rows)[:3]:
        quote = item.quotes[0]["quote"] if item.quotes else ""
        themes.append(
            {
                "name": item.label,
                "count": item.count,
                "severity": item.top_severity,
                "quote": quote[:90],
                "fix": item.need,
            }
        )
    return {"themes": themes, "wins": [{"change": t["fix"]} for t in themes]}


def fallback_copy(rows: list[dict], language: str) -> dict:
    insight = analyze(rows)[0]
    lang = {"English": "English", "Arabic": "Arabic"}.get(language, "Both")
    variant = generate_copy(insight, "Careem default", lang).variants[0]
    return {
        "headline": variant["headline"],
        "helper": variant["helper"],
        "cta": variant["cta"],
        "empty": variant["empty"],
        "error": variant["error"],
    }


def fallback_layouts(rows: list[dict]) -> dict:
    insight = analyze(rows)[0]
    return {
        "layouts": [
            {"name": item["name"], "structure": item["structure"][:4]}
            for item in generate_layouts(insight)[:3]
        ]
    }


def run_job(kind: str, rows: list[dict], groq_key: str = "", language: str = "English", screen: str = "Ride") -> tuple[dict, str]:
    prompts = {
        "summary": summarize_prompt(rows),
        "copy": copy_prompt(rows, screen, language),
        "layouts": layout_prompt(rows, screen),
    }
    fallbacks = {
        "summary": fallback_summary,
        "copy": lambda r: fallback_copy(r, language),
        "layouts": fallback_layouts,
    }
    try:
        return complete(prompts[kind], groq_key)
    except Exception:
        return fallbacks[kind](rows), "Local"
