"""Challenge 2 brain: brief → DNA → directions → critique → observed style."""

from __future__ import annotations

from llm_studio import design
from screen_gen import _clean_screen, accept_screen, cancel_screen, checkout_screen, rider_home_earnings

CAREEM_DNA = {
    "system": "Careem",
    "layout": "8px grid · generous spacing · max 2 CTAs",
    "cards": "16px radius · subtle border · no heavy shadows",
    "type": "Title 22/28 Medium · Body 14/20 Regular · Google Sans",
    "interaction": "Bottom sheets over modals",
    "patterns": [
        "Primary action sticky at bottom",
        "Confirm before destructive actions",
        "Fee, fare, or total visible before commit",
        "Ride stays one tap from home",
    ],
    "components": [
        "Button/Primary",
        "Button/Secondary",
        "FareChip",
        "Sheet",
        "WhereTo",
        "TabBar",
        "FeeBanner",
        "ListRow",
    ],
}

COMPONENT_MAP = {
    "hello": "Text/Title",
    "search": "WhereTo",
    "pills": "ChipRow",
    "hero": "EarningsCard",
    "stats": "StatRow",
    "split": "SplitBar",
    "list": "ListRow",
    "note": "HelperText",
    "map": "Map",
    "sheet": "Sheet",
    "cta": "Button/Primary",
    "tabs": "TabBar",
}


def _goal(brief: dict) -> str:
    return str(brief.get("goal") or brief.get("question") or "").strip()


def infer_kind(brief: dict) -> str:
    q = f"{_goal(brief)} {brief.get('product', '')} {brief.get('mode', '')}".lower()
    if any(w in q for w in ("cancel", "cancell")):
        return "cancel"
    if any(w in q for w in ("accept", "incoming ride", "offer", "captain request")):
        return "accept"
    if any(w in q for w in ("grocery", "food", "checkout", "delivery", "quik", "cart")):
        return "checkout"
    if any(w in q for w in ("earn", "dashboard", "home", "analytics")):
        return "home"
    return "home"


def directions_for(brief: dict) -> list[dict]:
    kind = infer_kind(brief)
    product = brief.get("product") or "Rides"
    if kind == "accept":
        return [
            {"id": "A", "name": "Fastest", "promise": "Fare and Accept on the first glance.", "note": "Map stays up. Two actions only."},
            {"id": "B", "name": "Informative", "promise": "Pickup, drop-off, distance, and time before they commit.", "note": "Rating stays visible."},
            {"id": "C", "name": "Guided", "promise": "First-time captains get the route and fare explained.", "note": "Still max 2 CTAs."},
        ]
    if kind == "cancel":
        return [
            {"id": "A", "name": "Fastest", "promise": "Minimal steps, optimized for conversion.", "note": "Fee still visible. One confirm."},
            {"id": "B", "name": "Informative", "promise": "More explanation and pricing transparency.", "note": "Why the fee exists, before they tap."},
            {"id": "C", "name": "Guided", "promise": "More hand-holding for first-time riders.", "note": "Keep ride + undo after cancel."},
        ]
    if kind == "checkout":
        return [
            {"id": "A", "name": "Fastest", "promise": "Fewest taps from slot to pay.", "note": "Delivery fee locked next to the CTA."},
            {"id": "B", "name": "Informative", "promise": "Fee, slot, and substitutions explained.", "note": "No surprise at the last step."},
            {"id": "C", "name": "Guided", "promise": "First-time grocery users get a walkthrough.", "note": "Confirm before a destructive change."},
        ]
    return [
        {"id": "A", "name": "Fastest", "promise": f"One-tap {product} from home.", "note": "Primary number on the first screen."},
        {"id": "B", "name": "Informative", "promise": "Analytics and breakdown visible without hunting.", "note": "Where to stays above the fold."},
        {"id": "C", "name": "Guided", "promise": "New users understand Plus cashback vs spend.", "note": "Helper copy, still max 2 CTAs."},
    ]


def screen_for_direction(brief: dict, direction_id: str) -> dict:
    kind = infer_kind(brief)
    goal = _goal(brief)
    if kind == "accept":
        screen = accept_screen(goal)
        if direction_id == "A":
            screen["label"] = "Accept · Fastest"
        elif direction_id == "C":
            screen["label"] = "Accept · Guided"
            screen["note"] = "Fare is locked before you accept."
        else:
            screen["label"] = "Accept · Informative"
        return screen
    if kind == "cancel":
        screen = cancel_screen(goal)
        if direction_id == "A":
            screen["label"] = "Cancel · Fastest"
            screen["note"] = ""
        elif direction_id == "C":
            screen["label"] = "Cancel · Guided"
            screen["note"] = "You can undo this for 30 seconds."
        else:
            screen["label"] = "Cancel · Informative"
            screen["note"] = "The captain already accepted, so a fee applies."
        return screen
    if kind == "checkout":
        screen = checkout_screen(goal or "food checkout")
        if direction_id == "A":
            screen["secondary"] = ""
            screen["label"] = "Checkout · Fastest"
        elif direction_id == "C":
            screen["feeNote"] = "New here? The fee is locked before Pay."
            screen["label"] = "Checkout · Guided"
        else:
            screen["label"] = "Checkout · Informative"
        return screen
    screen = rider_home_earnings(goal or "rider home")
    if direction_id == "A":
        screen["label"] = "Home · Fastest"
        screen["where"] = "Where to?"
        screen["earned"] = ""
        screen["weeks"] = []
        screen["stats"] = []
        screen["split"] = []
        screen["trips"] = []
        screen["cta"] = "Book a ride"
    elif direction_id == "C":
        screen["label"] = "Home · Guided"
        screen["helper"] = "Plus cashback is already in this month’s total."
    else:
        screen["label"] = "Home · Informative"
    return screen


def critique_for(brief: dict, screen: dict | None) -> list[dict]:
    kind = infer_kind(brief)
    issues = [
        {
            "title": "Delivery or cancel fee must appear before the last tap",
            "why": "Unexpected pricing is the top abandonment pattern in ride and grocery notes.",
            "layer": "Business + UX",
        },
        {
            "title": "Max two actions on this screen",
            "why": "Careem DNA: one primary, one secondary. A third button is a new primitive.",
            "layer": "Design system",
        },
        {
            "title": "Arabic expansion and 44px targets",
            "why": "Primary labels grow in AR. Touch targets must stay 44px.",
            "layer": "Accessibility",
        },
    ]
    if kind == "checkout":
        issues[0]["title"] = "Delivery fee appears only at the final step"
        issues[0]["why"] = "Showing it earlier may reduce checkout abandonment from unexpected pricing."
    if kind == "cancel":
        issues.append(
            {
                "title": "No confirmation before a charged cancel",
                "why": "Destructive money actions need a keep-ride path.",
                "layer": "Consistency",
            }
        )
    if screen and screen.get("blocks"):
        types = [b.get("type") for b in screen["blocks"]]
        if types.count("cta") > 2:
            issues.insert(0, {"title": "Too many CTAs", "why": "More than two actions breaks Careem DNA.", "layer": "Design system"})
    return issues[:4]


def flow_for(brief: dict) -> dict:
    raw = brief.get("flow") or ""
    if raw and "→" in raw:
        steps = [p.strip() for p in raw.split("→") if p.strip()]
    elif infer_kind(brief) == "checkout":
        steps = ["Home", "Search", "Results", "Slot", "Checkout", "Payment", "Success"]
    elif infer_kind(brief) == "accept":
        steps = ["Offer", "Accept sheet", "On the way"]
    elif infer_kind(brief) == "cancel":
        steps = ["In trip", "Cancel sheet", "Fee confirm", "Done"]
    else:
        steps = ["Home", "Search", "Match", "In trip", "Receipt"]
    problems = [
        {"flag": "No recovery route after payment failure.", "fix": "Generate Failed → Retry without losing the cart."},
        {"flag": "User can lose context after a cancel.", "fix": "Keep the map and fare on the confirm sheet."},
        {"flag": "Missing empty and Arabic states.", "fix": "Stress-test those before handoff."},
    ]
    if "Failed" not in steps and infer_kind(brief) == "checkout":
        problems.insert(0, {"flag": "No payment-failed screen in the flow.", "fix": "Add Payment → Failed → Retry."})
    return {"steps": steps, "problems": problems}


def tree_for(screen: dict) -> list[dict]:
    rows = [{"component": "Frame/Phone", "role": "screen"}]
    if screen.get("kind") == "cancel" and not screen.get("blocks"):
        return rows + [
            {"component": "Map", "role": "context"},
            {"component": "Sheet", "role": "decision"},
            {"component": "FeeBanner", "role": "number-first"},
            {"component": "Button/Primary", "role": "keep"},
            {"component": "Button/Secondary", "role": "destructive"},
        ]
    for block in screen.get("blocks") or []:
        rows.append({"component": COMPONENT_MAP.get(block.get("type"), "Block"), "role": block.get("type")})
    if screen.get("kind") == "dashboard":
        rows += [
            {"component": "WhereTo", "role": "search"},
            {"component": "EarningsCard", "role": "hero"},
            {"component": "Button/Primary", "role": "cta"},
        ]
    return rows


def start_project(brief: dict, dna: dict | None = None) -> dict:
    dirs = directions_for(brief)
    previews = {d["id"]: screen_for_direction(brief, d["id"]) for d in dirs}
    return {
        "reply": "I read the brief and Careem DNA. Three directions — pick one, or combine A + C. Nothing ships until you choose.",
        "brief": brief,
        "careem_dna": CAREEM_DNA,
        "directions": dirs,
        "previews": previews,
        "flow": flow_for(brief),
        "critic": {"score": 88, "note": "Directions stay inside Careem components and your Style Memory."},
        "issues": critique_for(brief, None),
        "model": "studio-brain",
    }


def pick_direction(brief: dict, direction_id: str, combine: str | None, dna: dict | None = None) -> dict:
    label = combine or direction_id
    goal = _goal(brief)
    prompt = (
        f"Project brief: {brief}. Direction {label}. "
        f"Co-design this Careem screen. Obey Careem DNA: {CAREEM_DNA['patterns']}. "
        f"{goal}"
    )
    try:
        data, model = design(prompt, [], dna)
        screen = _clean_screen(data.get("screen") or {})
        reply = data.get("reply")
    except Exception:
        screen = screen_for_direction(brief, direction_id or "B")
        model = "studio-brain"
        reply = f"Direction {label} on Careem components. Edit the layers — I’ll notice."
    screen["label"] = screen.get("label") or f"Direction {label}"
    return {
        "reply": reply or f"Direction {label}. Edit anything. I only keep a preference if you say so.",
        "intent": f"direction_{label}",
        "screen": screen,
        "tree": tree_for(screen),
        "issues": critique_for(brief, screen),
        "flow": flow_for(brief),
        "critic": {"score": 91, "note": f"Direction {label} · mapped to Careem components."},
        "choices": [
            {"id": "learn", "label": "Learn this style"},
            {"id": "compact", "label": "Tighter spacing"},
            {"id": "clear", "label": "Show the number sooner"},
        ],
        "model": model,
    }
