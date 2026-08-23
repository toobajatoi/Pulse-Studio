import json
from screen_gen import converse

prompts = [
    "Make me a screen for Home dashboard for careem riders that should have analytics of their montly earnings",
    "Food checkout when the card fails and the rider does not know if they were charged",
    "Captain profile after a 1-star rating with plate large enough at night",
]
for q in prompts:
    data = converse(q, [])
    screen = data.get("screen") or {}
    print("---")
    print(data.get("model"), data.get("intent"))
    print((data.get("reply") or "")[:120])
    print("kind", screen.get("kind"), "blocks", len(screen.get("blocks") or []), "label", screen.get("label"))
    if screen.get("blocks"):
        print("types", [b.get("type") for b in screen["blocks"]])
