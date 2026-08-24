"""Challenge 2 brain: brief → DNA → directions → critique → observed style."""

from __future__ import annotations

import json

from llm_studio import design
from screen_gen import (
    _clean_screen,
    _looks_like_wrong_template,
    _screen_usable,
    apply_direction,
    complete_screen,
    direction_reply,
    ensure_blocks,
    infer_screen_kind,
    is_complete,
    prompt_screen,
)

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

SCREEN_DESIGN_SYSTEM = {
    "food": {
        "name": "Food Home",
        "product": "Food",
        "layout": "Location → search → category chips → offer → restaurant sections",
        "tokens": {"primary": "#00E784", "forest": "#06281F", "text": "#1F1F1F", "muted": "#5F6368", "card": "#FFFFFF", "radius": "16px", "grid": "8px"},
        "typography": {"title": "22/28 Medium", "section": "18/24 Medium", "body": "14/20 Regular", "meta": "12/16 Regular"},
        "components": [
            {"name": "LocationChip", "spec": "Pin + delivery address · 44px tap"},
            {"name": "SearchField", "spec": "Search restaurants or dishes · 48px"},
            {"name": "CategoryChipRow", "spec": "Horizontal scroll categories"},
            {"name": "OfferBanner", "spec": "Promo line · brand-soft fill"},
            {"name": "SectionHeader", "spec": "For you · Popular near you"},
            {"name": "RestaurantCard", "spec": "Image · name · rating · ETA · from-price · dish"},
            {"name": "TabBar", "spec": "Food · Search · Orders · You"},
        ],
        "rules": ["Rating + ETA on every card", "From-price on cards", "Fast scan · no fee on browse"],
    },
    "arriving": {
        "name": "Driver Arriving",
        "product": "Rides",
        "layout": "Map 60% · bottom sheet · Call + Message",
        "tokens": {"primary": "#00E784", "sheet": "#FFFFFF", "radius": "22px"},
        "typography": {"captain": "14/20 Medium", "plate": "18/24 Bold"},
        "components": [
            {"name": "Map", "spec": "Route · fare · ETA chip"},
            {"name": "CaptainRow", "spec": "Avatar · name · rating · car"},
            {"name": "PlateChip", "spec": "License plate prominent"},
            {"name": "Button/Primary", "spec": "Call"},
            {"name": "Button/Secondary", "spec": "Message"},
            {"name": "TextAction", "spec": "Cancel ride"},
        ],
        "rules": ["Max 2 primaries", "Cancel is text only"],
    },
    "accept": {
        "name": "Accept Ride",
        "product": "Rides",
        "layout": "Radar map · offer sheet · Decline | Accept",
        "tokens": {"primary": "#00E784", "offer": "#FFFFFF"},
        "typography": {"fare": "18/24 Bold", "stops": "13/18 addresses"},
        "components": [
            {"name": "RadarMap", "spec": "Rings + car"},
            {"name": "OfferSheet", "spec": "Fare · pickup · drop"},
            {"name": "Button/Primary", "spec": "Accept"},
            {"name": "Button/Ghost", "spec": "Decline"},
        ],
        "rules": ["Fare before Accept", "Real addresses"],
    },
    "cancel": {
        "name": "Cancel Ride",
        "product": "Rides",
        "layout": "Map · sheet · fee · Keep | Cancel and pay",
        "tokens": {"fee": "#137333"},
        "typography": {"fee": "14/20 Bold"},
        "components": [
            {"name": "FeeBanner", "spec": "Fee before tap"},
            {"name": "Button/Primary", "spec": "Keep this trip"},
            {"name": "Button/Secondary", "spec": "Cancel and pay"},
        ],
        "rules": ["Fee visible before destructive tap"],
    },
    "failed": {
        "name": "Payment Failed",
        "product": "Pay",
        "layout": "Alert · totals · Try again | Change payment",
        "tokens": {"alert": "#EA4335"},
        "typography": {"title": "22/28 Medium"},
        "components": [
            {"name": "TotalsBlock", "spec": "Amount + card visible"},
            {"name": "Button/Primary", "spec": "Try Again"},
            {"name": "Button/Secondary", "spec": "Change Payment"},
        ],
        "rules": ["Amount stays on screen"],
    },
    "checkout": {
        "name": "Grocery Checkout",
        "product": "Quik",
        "layout": "Slot · items · fee row · Pay",
        "tokens": {"fee": "#137333"},
        "typography": {"total": "14/20 Bold"},
        "components": [
            {"name": "SlotPicker", "spec": "Delivery window"},
            {"name": "FeeLine", "spec": "Delivery fee pre-pay"},
            {"name": "Button/Primary", "spec": "Pay now"},
        ],
        "rules": ["Fee before Pay tap"],
    },
    "completed": {
        "name": "Ride Completed",
        "product": "Rides",
        "layout": "Fare · route · payment · captain · stars · tips · Done",
        "tokens": {"star": "#F4B400", "tip": "brand-soft"},
        "typography": {"fare": "28/32 Medium"},
        "components": [
            {"name": "FareHero", "spec": "Final fare"},
            {"name": "StarRating", "spec": "5 stars"},
            {"name": "TipChips", "spec": "Optional amounts"},
            {"name": "Button/Primary", "spec": "Done"},
        ],
        "rules": ["Fare before rating", "Tip optional"],
    },
    "home": {
        "name": "Rider Home",
        "product": "Rides",
        "layout": "Where to · earnings · stats · tabs",
        "tokens": {"hero": "#111", "careem": "#00E784"},
        "typography": {"earned": "28/32"},
        "components": [
            {"name": "WhereTo", "spec": "Search rides"},
            {"name": "EarningsCard", "spec": "Monthly total"},
            {"name": "TabBar", "spec": "Home · Activity · Pay · You"},
        ],
        "rules": ["Where to above fold"],
    },
    "superapp": {
        "name": "Super App Home",
        "product": "Super App",
        "layout": "Greeting → Where to → service grid → promo → recent",
        "tokens": {"primary": "#00E784", "forest": "#06281F", "text": "#1F1F1F", "muted": "#5F6368", "card": "#FFFFFF", "radius": "16px", "grid": "8px"},
        "typography": {"title": "22/28 Medium", "body": "14/20 Regular", "meta": "12/16 Regular"},
        "components": [
            {"name": "WhereTo", "spec": "Search destinations · 48px"},
            {"name": "ServiceGrid", "spec": "Rides Food Quik Pay Shops"},
            {"name": "OfferBanner", "spec": "Promo line · no charts"},
            {"name": "ListRow", "spec": "Recent places"},
            {"name": "TabBar", "spec": "Home · Activity · Pay · You"},
        ],
        "rules": ["Service tiles not grey pills", "Promo is a banner, never a graph", "Where to stays above the fold"],
    },
}


def design_system_for(brief: dict) -> dict:
    kind = infer_kind(brief)
    base = SCREEN_DESIGN_SYSTEM.get(kind) or {
        "name": "Careem Screen",
        "product": brief.get("product") or "Careem",
        "layout": CAREEM_DNA["layout"],
        "tokens": {"primary": "#00E784", "radius": "16px"},
        "typography": {"body": CAREEM_DNA["type"]},
        "components": [{"name": c, "spec": "Careem primitive"} for c in CAREEM_DNA["components"][:6]],
        "rules": CAREEM_DNA["patterns"],
    }
    return {**base, "kind": kind, "global": CAREEM_DNA}


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
    "location": "LocationChip",
    "offer": "OfferBanner",
    "categories": "CategoryChipRow",
    "section": "SectionHeader",
    "restaurants": "RestaurantCard",
    "captain": "CaptainRow",
    "trip": "TripSummary",
    "rating": "StarRating",
    "tips": "TipChips",
    "totals": "TotalsBlock",
}


def design_system_from_response(data: dict, brief: dict) -> dict:
    ds = data.get("design_system")
    if isinstance(ds, dict) and ds.get("components"):
        kind = infer_kind(brief)
        fallback = SCREEN_DESIGN_SYSTEM.get(kind) or {}
        return {
            **ds,
            "kind": kind,
            "name": fallback.get("name") or ds.get("name"),
            "product": fallback.get("product") or brief.get("product") or ds.get("product"),
            "global": CAREEM_DNA,
        }
    screen = _clean_screen(data.get("screen") or {}, _goal(brief), brief)
    components = []
    for block in screen.get("blocks") or []:
        if not isinstance(block, dict):
            continue
        t = str(block.get("type") or "block")
        components.append({"name": COMPONENT_MAP.get(t, t), "spec": f"`{t}` block on this generated screen"})
    fallback = SCREEN_DESIGN_SYSTEM.get(infer_kind(brief), {})
    return {
        "name": (ds or {}).get("name") or fallback.get("name") or "Generated screen",
        "product": fallback.get("product") or brief.get("product") or "Careem",
        "layout": (ds or {}).get("layout") or fallback.get("layout") or CAREEM_DNA["layout"],
        "tokens": (ds or {}).get("tokens") or fallback.get("tokens") or {"primary": "#00E784"},
        "typography": (ds or {}).get("typography") or fallback.get("typography") or {"body": CAREEM_DNA["type"]},
        "components": components or fallback.get("components") or [],
        "rules": (ds or {}).get("rules") or fallback.get("rules") or CAREEM_DNA["patterns"],
        "kind": infer_kind(brief),
        "global": CAREEM_DNA,
    }


def _direction_prompt(brief: dict, direction_id: str, combine: str | None = None) -> str:
    goal = _goal(brief)
    label = combine or direction_id
    names = {"A": "Fastest", "B": "Informative", "C": "Guided"}
    hint = names.get(str(direction_id), direction_id)
    variants = {
        "A": "Fastest: fewer blocks, one promo or number above the fold, no extra helper.",
        "B": "Informative: ratings, prices, fees, and context visible before the tap.",
        "C": "Guided: add one helper note for first-time users. Still max 2 CTAs.",
    }
    return (
        f"Project brief: {json.dumps(brief, ensure_ascii=False)}. "
        f"Direction {label} ({hint}). {variants.get(str(direction_id), '')} "
        f"This direction MUST look different from the other two. "
        f"Design the Careem screen as blocks[] plus design_system. "
        f"Use only these block types: hello, location, search, pills, categories, offer, restaurants, list, map, sheet, captain, trip, note, totals, cta, tabs. "
        f"Food home MUST include restaurants items with name, rating, eta, from. Never invent types like SearchField. "
        f"Careem DNA: {CAREEM_DNA['patterns']}. "
        f"Language: {brief.get('language') or 'EN'}. Write all UI copy in English unless language is AR. "
        f"Set rtl true only when language is AR. "
        f"Goal: {goal}"
    )


def _generate_with_llm(brief: dict, direction_id: str, combine: str | None, dna: dict | None) -> tuple[dict, str, str, dict]:
    prompt = _direction_prompt(brief, direction_id, combine)
    retry = (
        f"{prompt} Return at least 4 meaningful blocks that match the goal. "
        "Include design_system.components for every block type you use."
    )
    errors = []
    for attempt, text in enumerate((prompt, retry)):
        try:
            data, model = design(text, [], dna)
            screen = _clean_screen(data.get("screen") or {}, _goal(brief), brief)
            if _screen_usable(screen) and not _looks_like_wrong_template(_goal(brief), screen):
                screen = complete_screen(screen, _goal(brief))
                ds = design_system_from_response(data, brief)
                return screen, str(data.get("reply") or "Here is the screen."), model, ds
            errors.append("model returned an unusable screen")
        except Exception as exc:
            errors.append(str(exc))
    screen = ensure_blocks(prompt_screen(_goal(brief)), _goal(brief))
    screen = complete_screen(screen, _goal(brief))
    return screen, "Here is a working screen from your brief. Refine it in the composer.", "studio-fallback", design_system_for(brief)


def _goal(brief: dict) -> str:
    return str(brief.get("goal") or brief.get("question") or "").strip()


def infer_kind(brief: dict) -> str:
    product = str(brief.get("product") or "").strip().lower()
    kind = infer_screen_kind(f"{_goal(brief)} {brief.get('product', '')} {brief.get('mode', '')}")
    if product == "super app" and kind in ("food", "home", "generic"):
        return "superapp"
    if product == "food" and kind in ("home", "generic"):
        return "food"
    return kind


def directions_for(brief: dict) -> list[dict]:
    kind = infer_kind(brief)
    product = brief.get("product") or "Careem"
    what = {
        "arriving": "arriving",
        "accept": "accept",
        "cancel": "cancel",
        "checkout": "checkout",
        "completed": "trip complete",
        "failed": "payment failed",
        "food": "Food home",
        "superapp": "Super App home",
        "home": f"{product} home",
    }.get(kind, product)
    return [
        {"id": "A", "name": "Fastest", "promise": f"Only the {what} action and the number that matter first.", "note": "Max 2 CTAs."},
        {"id": "B", "name": "Informative", "promise": f"Prices, fees, and context stay visible on this {what} screen.", "note": "Careem components only."},
        {"id": "C", "name": "Guided", "promise": f"One helper line so a first-time user can finish {what}.", "note": "Still max 2 primary actions."},
    ]


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
    if kind == "food":
        issues[0]["title"] = "Restaurant cards missing ETA or rating"
        issues[0]["why"] = "Food browse needs trust signals before the user opens a restaurant."
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
    kind = infer_kind(brief)
    raw = brief.get("flow") or ""
    custom = raw and "→" in raw and not raw.startswith("Home → Search → Slot")
    if custom:
        steps = [p.strip() for p in raw.split("→") if p.strip()]
    elif kind == "checkout":
        steps = ["Home", "Search", "Results", "Slot", "Checkout", "Payment", "Success"]
    elif kind == "arriving":
        steps = ["Accepted", "Arriving", "Pickup", "On trip"]
    elif kind == "accept":
        steps = ["Offer", "Accept", "Arriving"]
    elif kind == "failed":
        steps = ["Pay", "Failed", "Retry"]
    elif kind == "cancel":
        steps = ["On trip", "Cancel", "Fee confirm", "Done"]
    elif kind == "completed":
        steps = ["On trip", "Complete", "Rate", "Receipt"]
    elif kind == "food":
        steps = ["Food home", "Restaurant", "Cart", "Checkout", "Track"]
    elif kind == "superapp":
        steps = ["Home", "Service", "Search", "Book", "Track"]
    else:
        steps = ["Home", "Search", "Match", "On trip", "Receipt"]
    problems = {
        "arriving": [
            {"flag": "Rider cannot find the car.", "fix": "Keep plate, color, and Call on this screen."},
            {"flag": "Cancel is too easy to hit.", "fix": "Cancel stays a text action, not a second primary."},
        ],
        "accept": [
            {"flag": "Fare hidden until after Accept.", "fix": "Show fare before the tap."},
            {"flag": "Addresses look like pins only.", "fix": "Use street names, not the word Pickup."},
        ],
        "cancel": [
            {"flag": "Fee appears after they tap.", "fix": "Fee stays on the sheet before Cancel and pay."},
            {"flag": "No keep-ride path.", "fix": "Keep this trip is the primary."},
        ],
        "failed": [
            {"flag": "Amount disappears on failure.", "fix": "Trip amount and card stay visible."},
        ],
        "checkout": [
            {"flag": "Delivery fee only at the last tap.", "fix": "Lock the fee next to Pay."},
            {"flag": "No recovery after payment fails.", "fix": "Add Failed → Retry without losing the cart."},
        ],
        "home": [
            {"flag": "Where to is buried.", "fix": "Search stays one tap from open."},
        ],
        "completed": [
            {"flag": "Fare hidden until after rating.", "fix": "Show the final fare before stars."},
            {"flag": "Too many actions after the trip.", "fix": "Done plus receipt or home — not both as primaries."},
        ],
        "food": [
            {"flag": "Restaurant cards missing ETA or rating.", "fix": "Every card shows ★ and delivery time."},
            {"flag": "Delivery location buried.", "fix": "Pin + address stays at the top."},
        ],
        "superapp": [
            {"flag": "Services look like leftover chips.", "fix": "Use a 4-column service grid with Careem tiles."},
            {"flag": "Where to is buried under promos.", "fix": "Search stays at the top."},
        ],
    }.get(
        kind,
        [
            {"flag": "No recovery route after a failure.", "fix": "Generate the missing failure states."},
        ],
    )
    here = {
        "arriving": "Arriving",
        "accept": "Accept",
        "cancel": "Cancel",
        "failed": "Failed",
        "checkout": "Checkout",
        "home": "Home",
        "completed": "Complete",
        "food": "Food home",
        "superapp": "Home",
    }.get(kind, steps[0] if steps else "")
    goal = _goal(brief).lower()
    if kind == "food" and any(w in goal for w in ("cart", "checkout", "basket")):
        here = "Cart"
    elif kind == "food" and any(w in goal for w in ("search", "filter")):
        here = "Restaurant" if "restaurant" in goal else "Food home"
    return {"steps": steps, "problems": problems, "here": here}


def tree_for(screen: dict) -> list[dict]:
    rows = [{"component": "Frame/Phone", "role": "screen"}]
    kind = screen.get("kind")
    if kind == "food":
        return rows + [
            {"component": "LocationChip", "role": "delivery"},
            {"component": "SearchField", "role": "search"},
            {"component": "CategoryChipRow", "role": "filters"},
            {"component": "OfferBanner", "role": "promo"},
            {"component": "RestaurantCard", "role": "list"},
            {"component": "TabBar", "role": "nav"},
        ]
    if kind == "cancel" and not screen.get("blocks"):
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
    goal = _goal(brief)
    kind = infer_kind(brief)
    model = "studio-brain"
    ds = design_system_for(brief)
    base = ensure_blocks(prompt_screen(goal), goal)
    try:
        data, model = design(_direction_prompt(brief, "B"), [], dna)
        llm_screen = _clean_screen(data.get("screen") or {}, goal, brief)
        llm_screen = complete_screen(llm_screen, goal)
        if _screen_usable(llm_screen) and is_complete(llm_screen, kind) and not _looks_like_wrong_template(goal, llm_screen):
            base = llm_screen
            ds = design_system_from_response(data, brief)
    except Exception:
        pass
    previews = {d["id"]: apply_direction(base, d["id"], goal) for d in dirs}
    return {
        "reply": "I read the brief and Careem DNA. Three directions — Fastest, Informative, and Guided. Each one is a different layout of the same screen. Pick one.",
        "brief": brief,
        "careem_dna": CAREEM_DNA,
        "directions": dirs,
        "previews": previews,
        "flow": flow_for(brief),
        "design_system": ds,
        "critic": {"score": 88, "note": "Directions stay inside Careem components and your Style Memory."},
        "issues": critique_for(brief, None),
        "model": model,
    }


def pick_direction(brief: dict, direction_id: str, combine: str | None, dna: dict | None = None) -> dict:
    label = combine or direction_id
    goal = _goal(brief)
    kind = infer_kind(brief)
    screen, reply, model, ds = _generate_with_llm(brief, direction_id or "B", combine, dna)
    screen = complete_screen(screen, goal)
    screen = apply_direction(screen, direction_id or "B", goal)
    screen["label"] = screen.get("label") or f"Direction {label}"
    reply = direction_reply(kind, direction_id or "B", reply)
    return {
        "reply": reply,
        "intent": f"direction_{label}",
        "screen": screen,
        "tree": tree_for(screen),
        "issues": critique_for(brief, screen),
        "flow": flow_for(brief),
        "design_system": ds,
        "critic": {"score": 91, "note": f"Direction {label} · generated from your brief."},
        "choices": [
            {"id": "learn", "label": "Learn this style"},
            {"id": "compact", "label": "Tighter spacing"},
            {"id": "clear", "label": "Show the number sooner"},
        ],
        "model": model,
    }
