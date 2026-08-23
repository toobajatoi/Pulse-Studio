"""Local Ask Canvas model. No LLM required."""

from __future__ import annotations

from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "models" / "ask_model.joblib"

ANSWERS = {
    "cancel_fee": "Show the fee on the matching screen, not only after Cancel. Public ride reviews and our notes both cluster on surprise cancellation charges — riders need the rule before they tap.",
    "fare": "Lock an all-in fare before Book and keep the chip visible in-trip. Reviews fail when the map number is not the price they pay.",
    "wait": "Replace the spinner with named stages and nearby cars. Wait anxiety shows up as 'the app froze' in both the Uber review set and our dummy notes.",
    "pickup": "Let riders nudge the pin without restarting matching. Wrong pickup is a top theme in the public reviews and our Dubai mall notes.",
    "safety": "Share trip and plate stay on the happy path. Safety complaints in the public set are about being left stranded — don't hide controls.",
    "payment": "Name the money state: pending, failed, paid. 'You were not charged' must be visible. Refund and double-charge reviews are common.",
    "app": "Ride stays one tap from open. Home fails when promos and other products bury Where to.",
    "locale": "Ship EN and AR as first-class. Test RTL chip sides, Arabic expansion on the primary button, and Egypt large text before handoff.",
    "other": "Keep one primary action, Careem components only, and test Arabic expansion before you ship.",
}

HINTS = {
    "locale": ("arabic", "rtl", "urdu", "egypt", "large text", "bilingual", "chip flipped", "right to left"),
    "cancel_fee": ("cancel fee", "cancellation", "hide the fee", "fee before", "charged when they cancel", "free cancel"),
    "payment": ("payment", "wallet", "refund", "card failed", "was i charged", "double charge", "pending"),
    "wait": ("spinner", "finding a captain", "matching", "eta", "wait", "froze", "nearby cars"),
    "pickup": ("pickup", "pin", "drop-off", "address", "wrong street", "nudge"),
    "safety": ("share trip", "women preferred", "safety", "plate", "stranded", "trusted"),
    "fare": ("fare jumped", "price", "surge", "expensive", "estimate", "promo", "lock the price", "all-in fare", "fare chip"),
    "app": ("home screen", "otp", "onboarding", "too many", "where to", "promo wall", "sit above"),
}

_bundle = None


def load():
    global _bundle
    if _bundle is None:
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def _route(question: str, bundle: dict) -> tuple[str, float, str]:
    q = question.lower()
    for topic, keys in HINTS.items():
        if any(k in q for k in keys):
            return topic, 0.97, "rule"
    topic = bundle["classifier"].predict([question])[0]
    confidence = float(max(bundle["classifier"].predict_proba([question])[0]))
    return topic, confidence, "model"


def ask(question: str) -> dict:
    bundle = load()
    topic, confidence, routed = _route(question, bundle)
    vec = bundle["retriever_vec"].transform([question])
    _, idx = bundle["retriever_nn"].kneighbors(vec)
    ranked = []
    source_rank = {"careem_dummy": 0, "uber_public": 1, "synth_designer": 2}
    for i in idx[0]:
        row = bundle["corpus"][int(i)]
        ranked.append(
            (
                0 if row["topic"] == topic else 1,
                source_rank.get(row["source"], 3),
                {
                    "text": str(row["text"])[:180],
                    "source": row["source"],
                    "topic": row["topic"],
                },
            )
        )
    ranked.sort(key=lambda item: (item[0], item[1]))
    evidence = []
    for _, _, item in ranked:
        if item not in evidence:
            evidence.append(item)
        if len(evidence) == 3:
            break
    return {
        "topic": topic,
        "confidence": round(confidence, 2),
        "routed": routed,
        "answer": ANSWERS.get(topic, ANSWERS["other"]),
        "evidence": evidence,
        "model": "tfidf-logreg + knn",
        "accuracy": bundle.get("accuracy"),
        "dataset": bundle.get("dataset"),
    }
