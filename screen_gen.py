"""Turn a designer prompt into a chat reply + a real phone screen."""

from __future__ import annotations

import copy
import re

from ask_engine import ask
from llm_studio import design

MARKETS = {
    "uae": {"cur": "AED", "city": "Dubai", "name": "Tooba"},
    "ksa": {"cur": "SAR", "city": "Riyadh", "name": "Tooba"},
    "egy": {"cur": "EGP", "city": "Cairo", "name": "Tooba"},
}


def _market(text: str) -> str:
    q = text.lower()
    if "egypt" in q or "cairo" in q or "egp" in q:
        return "egy"
    if "ksa" in q or "riyadh" in q or "sar" in q:
        return "ksa"
    return "uae"


def _rtl(text: str) -> bool:
    q = text.lower()
    return any(w in q for w in ("arabic", "rtl", "عربي"))


def infer_screen_kind(text: str) -> str:
    q = (text or "").lower()
    if any(p in q for p in ("super app", "service grid", "services hub", "home hub", "service picker")):
        return "superapp"
    if any(
        p in q
        for p in (
            "driver arriving",
            "captain arriving",
            "arriving screen",
            "on the way",
            "pickup progress",
            "license plate",
            "estimated arrival",
            "vehicle details",
        )
    ):
        return "arriving"
    if any(p in q for p in ("accept ride", "accept this ride", "incoming ride", "ride request", "new request")):
        return "accept"
    if any(p in q for p in ("payment failed", "try again", "could not be processed", "payment fail")):
        return "failed"
    if any(
        p in q
        for p in (
            "ride completed",
            "ride complete",
            "trip completed",
            "trip complete",
            "trip summary",
            "final fare",
            "rate your",
            "rate the driver",
            "rate driver",
            "leave a tip",
            "optional tip",
            "trip receipt",
            "receipt screen",
            "rating experience",
            "how was your trip",
            "you've arrived",
            "ride finished",
        )
    ):
        return "completed"
    if any(p in q for p in ("food cart", "food checkout", "restaurant cart", "careem food cart")) or (
        "cart" in q and any(w in q for w in ("food", "restaurant", "burger", "dish"))
    ):
        return "food"
    if any(p in q for p in ("grocery", "quik cart", "quik checkout")) or (
        "checkout" in q and any(w in q for w in ("grocery", "quik", "slot"))
    ):
        return "checkout"
    if any(
        p in q
        for p in (
            "food home",
            "careem food",
            "discover what to eat",
            "restaurant recommendation",
            "food categor",
            "popular dishes",
            "restaurant card",
            "promo banner",
            "what to eat",
            "search restaurants",
        )
    ) or (
        "restaurant" in q
        and any(w in q for w in ("card", "eta", "categor", "promo", "banner", "rating", "pricing"))
    ) or (
        any(w in q for w in ("food home", "careem food", "what to eat", "cravings"))
        and not any(w in q for w in ("super app", "service grid", "checkout", "grocery cart", "quik cart", "delivery fee", "monthly earnings"))
    ):
        return "food"
    if any(p in q for p in ("monthly earnings", "rider home", "home dashboard", "earnings home")):
        return "home"
    if any(p in q for p in ("cancel this ride", "cancel ride screen", "cancellation", "cancel the ride?")) or q.strip().startswith("cancel"):
        return "cancel"
    return "generic"


def detect(question: str, history: list | None = None) -> str:
    q = question.lower()
    last = ""
    if history:
        for row in reversed(history):
            if row.get("intent"):
                last = row["intent"]
                break
    kind = infer_screen_kind(question)
    if kind == "arriving":
        return "arriving"
    if kind == "accept":
        return "accept"
    if kind == "cancel":
        return "cancel"
    if kind == "failed":
        return "failed"
    if kind == "completed":
        return "completed"
    if kind == "food":
        return "food_home"
    if kind == "checkout":
        return "checkout"
    if kind == "superapp":
        return "superapp"
    if kind == "home":
        if any(w in q for w in ("captain", "driver")) and "arriv" not in q:
            return "captain_earnings"
        return "rider_home_earnings"
    make = any(w in q for w in ("make", "create", "design", "build", "screen", "generate", "show me", "draw"))
    if any(w in q for w in ("food", "order", "restaurant")):
        return "food_home"
    if last and not make and any(w in q for w in ("arabic", "rtl", "egypt", "ksa", "larger", "bigger")):
        return last
    if make and kind != "generic":
        return kind if kind in {
            "arriving", "accept", "cancel", "failed", "checkout", "completed", "home", "food"
        } else "prompt_screen"
    return "advice" if not make else "prompt_screen"


def rider_home_earnings(question: str) -> dict:
    mk = MARKETS[_market(question)]
    rtl = _rtl(question)
    if rtl:
        return {
            "kind": "dashboard",
            "title": "الرئيسية",
            "label": f"Home · {mk['city']}",
            "rtl": True,
            "hello": f"مساء الخير، {mk['name']}",
            "where": "وين نروح؟",
            "month": "أرباح أغسطس",
            "earned": f"{mk['cur']} 186.40",
            "delta": "+12% من يوليو · كاش باك Plus",
            "weeks": [42, 68, 51, 88],
            "stats": [
                {"n": "18", "l": "مشاوير"},
                {"n": f"{mk['cur']} 1,248", "l": "مصروف"},
                {"n": f"{mk['cur']} 186", "l": "أرباح"},
            ],
            "split": [("مشاوير", 72), ("طعام", 19), ("كويك", 9)],
            "recent_title": "آخر المشاوير",
            "trips": [
                ("دبي مول", "اليوم · 24.50", mk["cur"]),
                ("المارينا", "أمس · 18.00", mk["cur"]),
                ("المطار", "22 أغسطس · 62.00", mk["cur"]),
            ],
            "tabs": ["الرئيسية", "نشاط", "دفع", "حسابك"],
        }
    return {
        "kind": "dashboard",
        "title": "Home",
        "label": f"Home · {mk['city']}",
        "rtl": False,
        "hello": f"Good evening, {mk['name']}",
        "where": "Where to?",
        "month": "August earnings",
        "earned": f"{mk['cur']} 186.40",
        "delta": "+12% vs July · Plus cashback",
        "weeks": [42, 68, 51, 88],
        "stats": [
            {"n": "18", "l": "Trips"},
            {"n": f"{mk['cur']} 1,248", "l": "Spent"},
            {"n": f"{mk['cur']} 186", "l": "Earned"},
        ],
        "split": [("Rides", 72), ("Food", 19), ("Quik", 9)],
        "recent_title": "Recent trips",
        "trips": [
            ("Dubai Mall", "Today · 24.50", mk["cur"]),
            ("Marina", "Yesterday · 18.00", mk["cur"]),
            ("Airport T3", "22 Aug · 62.00", mk["cur"]),
        ],
        "tabs": ["Home", "Activity", "Pay", "You"],
    }


def captain_earnings(question: str) -> dict:
    mk = MARKETS[_market(question)]
    return {
        "kind": "dashboard",
        "title": "Earnings",
        "label": f"Captain · {mk['city']}",
        "rtl": _rtl(question),
        "hello": "This week",
        "where": "",
        "month": "Monthly earnings",
        "earned": f"{mk['cur']} 4,820",
        "delta": "42 trips · 31h online",
        "weeks": [55, 72, 64, 90],
        "stats": [
            {"n": f"{mk['cur']} 4.8k", "l": "Net"},
            {"n": "96%", "l": "Acceptance"},
            {"n": "4.92", "l": "Rating"},
        ],
        "split": [("Rides", 81), ("Delivery", 19)],
        "recent_title": "Payouts",
        "trips": [
            ("Weekly payout", "Sun · 1,210", mk["cur"]),
            ("Tips", "Aug · 186", mk["cur"]),
            ("Peak bonus", "Fri · 95", mk["cur"]),
        ],
        "tabs": ["Home", "Earnings", "Account"],
    }


def failed_screen(question: str) -> dict:
    mk = MARKETS[_market(question)]
    return {
        "kind": "failed",
        "title": "Payment failed",
        "label": f"Failed · {mk['city']}",
        "amount": f"{mk['cur']} 25.00" if mk["cur"] == "AED" else f"{mk['cur']} 28" if mk["cur"] == "SAR" else f"{mk['cur']} 145",
        "method": "Visa **** 1234",
        "primary": "Try Again",
        "secondary": "Change Payment",
    }


def completed_screen(question: str) -> dict:
    mk = MARKETS[_market(question)]
    captains = {
        "Dubai": ("Yousef", "White Toyota Camry", "4.92"),
        "Riyadh": ("Fahad", "Grey Hyundai Elantra", "4.88"),
        "Cairo": ("Omar", "White Kia Rio", "4.95"),
    }
    routes = {
        "Dubai": ("Dubai Mall, Financial Centre Rd", "Marina Walk, JBR"),
        "Riyadh": ("Kingdom Centre, Olaya St", "King Abdullah Park"),
        "Cairo": ("City Stars, Nasr City", "Zamalek Bridge Rd"),
    }
    name, car, rating = captains.get(mk["city"], captains["Dubai"])
    pickup, dest = routes.get(mk["city"], routes["Dubai"])
    fare = f"{mk['cur']} 32.50" if mk["cur"] == "AED" else f"{mk['cur']} 34" if mk["cur"] == "SAR" else f"{mk['cur']} 168"
    tip5 = f"{mk['cur']} 5" if mk["cur"] == "AED" else f"{mk['cur']} 5"
    tip10 = f"{mk['cur']} 10" if mk["cur"] == "AED" else f"{mk['cur']} 10"
    tip15 = f"{mk['cur']} 15" if mk["cur"] == "AED" else f"{mk['cur']} 15"
    return {
        "kind": "completed",
        "title": "Trip complete",
        "label": f"Complete · {mk['city']}",
        "rtl": _rtl(question),
        "fare": fare,
        "distance": "12.4 km",
        "duration": "24 min",
        "pickup": pickup,
        "dest": dest,
        "method": "Careem Pay · Visa **** 1234",
        "captain": name,
        "car": car,
        "rating": rating,
        "tips": [tip5, tip10, tip15],
        "feedback": "",
        "primary": "Done",
        "secondary": "View receipt",
        "tertiary": "Home",
    }


def arriving_screen(question: str) -> dict:
    mk = MARKETS[_market(question)]
    captains = {"Dubai": ("Yousef", "RAK 48291"), "Riyadh": ("Fahad", "KSA 2201"), "Cairo": ("Omar", "CAI 908")}
    name, plate = captains.get(mk["city"], captains["Dubai"])
    dest = "Marina Walk, JBR" if mk["city"] == "Dubai" else "Olaya St" if mk["city"] == "Riyadh" else "Zamalek Bridge Rd"
    return {
        "kind": "arriving",
        "title": "Captain is arriving",
        "label": f"Arriving · {mk['city']}",
        "rtl": False,
        "captain": name,
        "rating": "4.92",
        "car": "White Toyota Camry",
        "plate": plate,
        "eta": "3 min",
        "progress": 68,
        "fare": f"{mk['cur']} 27.50" if mk["cur"] == "AED" else f"{mk['cur']} 28" if mk["cur"] == "SAR" else f"{mk['cur']} 145",
        "pickup": f"{mk['city']} Mall, Financial Centre Rd" if mk["city"] == "Dubai" else dest,
        "dest": dest,
        "primary": "Call",
        "secondary": "Message",
        "tertiary": "Cancel ride",
    }


def accept_screen(question: str) -> dict:
    mk = MARKETS[_market(question)]
    places = {
        "Dubai": {
            "pickup": "Dubai Mall, Financial Centre Rd",
            "pickupArea": "Downtown Dubai",
            "drop": "Marina Walk, JBR",
            "dropArea": "Dubai Marina",
            "rider": "Ahmed",
        },
        "Riyadh": {
            "pickup": "Kingdom Centre, Olaya St",
            "pickupArea": "Olaya",
            "drop": "King Abdullah Park",
            "dropArea": "Malaz",
            "rider": "Mohammed",
        },
        "Cairo": {
            "pickup": "City Stars, Nasr City",
            "pickupArea": "Nasr City",
            "drop": "Zamalek Bridge Rd",
            "dropArea": "Zamalek",
            "rider": "Omar",
        },
    }
    loc = places.get(mk["city"], places["Dubai"])
    return {
        "kind": "accept",
        "title": "Accept this ride?",
        "label": f"Accept · {mk['city']}",
        "rtl": False,
        "city": mk["city"],
        "rider": loc["rider"],
        "pay": "Careem Pay",
        "pickup": loc["pickup"],
        "pickupArea": loc["pickupArea"],
        "dest": loc["drop"],
        "dropArea": loc["dropArea"],
        "fare": f"{mk['cur']} 45.00" if mk["cur"] == "AED" else f"{mk['cur']} 48" if mk["cur"] == "SAR" else f"{mk['cur']} 220",
        "distance": "2.3 km",
        "eta": "8 min",
        "rating": "4.8",
        "primary": "Accept",
        "secondary": "Decline",
    }


def cancel_screen(question: str) -> dict:
    mk = MARKETS[_market(question)]
    return {
        "kind": "cancel",
        "title": "Cancel ride",
        "label": f"Cancel · {mk['city']}",
        "rtl": False,
        "city": mk["city"],
        "pickup": f"{mk['city']} Mall, Downtown",
        "dest": "Marina Walk, JBR" if mk["city"] == "Dubai" else "Olaya St" if mk["city"] == "Riyadh" else "Zamalek Bridge Rd",
        "fare": f"{mk['cur']} 27.50" if mk["cur"] == "AED" else f"{mk['cur']} 28" if mk["cur"] == "SAR" else f"{mk['cur']} 145",
        "fee": f"{mk['cur']} 8" if mk["cur"] == "AED" else f"{mk['cur']} 12" if mk["cur"] == "SAR" else f"{mk['cur']} 35",
    }


def checkout_screen(question: str) -> dict:
    mk = MARKETS[_market(question)]
    items = [
        {"t": "Oat milk 1L", "s": f"{mk['cur']} 12"},
        {"t": "Baby spinach", "s": f"{mk['cur']} 9"},
        {"t": "Eggs · 12", "s": f"{mk['cur']} 20"},
    ]
    slots = ["Today · 6–8 pm", "Tomorrow · 10–12"]
    sub, fee, total = f"{mk['cur']} 41", f"{mk['cur']} 9", f"{mk['cur']} 50"
    return {
        "kind": "checkout",
        "title": "Checkout",
        "label": f"Checkout · {mk['city']}",
        "rtl": _rtl(question),
        "store": "Quik",
        "location": "Marina Walk, JLT",
        "slot": slots[0],
        "slots": slots,
        "items": items,
        "sub": sub,
        "fee": fee,
        "feeNote": "Delivery fee · shown before you pay",
        "total": total,
        "primary": "Pay now",
        "secondary": "Change slot",
        "blocks": [
            {"type": "hello", "kicker": "Quik", "title": "Checkout"},
            {"type": "location", "text": "Marina Walk, JLT"},
            {"type": "list", "title": "Cart", "items": items},
            {"type": "categories", "items": slots},
            {
                "type": "totals",
                "rows": [
                    {"label": "Subtotal", "value": sub},
                    {"label": "Delivery", "value": fee},
                    {"label": "Total", "value": total},
                ],
            },
            {"type": "cta", "text": "Pay now"},
            {"type": "cta", "text": "Change slot", "style": "secondary"},
        ],
    }


def food_home(question: str) -> dict:
    mk = MARKETS[_market(question)]
    locs = {
        "Dubai": "Marina Walk, JBR",
        "Riyadh": "Olaya St, Al Malaz",
        "Cairo": "Zamalek Bridge Rd",
    }
    location = locs.get(mk["city"], locs["Dubai"])
    cur = mk["cur"]
    restaurants = [
        {"name": "Salt", "rating": "4.8", "eta": "25 min", "from": f"From {cur} 35", "dish": "Truffle fries", "tag": "30% off"},
        {"name": "Al Mallah", "rating": "4.7", "eta": "30 min", "from": f"From {cur} 18", "dish": "Falafel wrap", "tag": "Free delivery"},
        {"name": "Operation Falafel", "rating": "4.6", "eta": "35 min", "from": f"From {cur} 22", "dish": "Mixed grill", "tag": ""},
        {"name": "Pickl", "rating": "4.9", "eta": "28 min", "from": f"From {cur} 42", "dish": "Smash burger", "tag": "Popular"},
    ]
    return {
        "kind": "food",
        "title": "Food",
        "label": f"Food · {mk['city']}",
        "rtl": _rtl(question),
        "location": location,
        "search": "Search restaurants or dishes",
        "categories": ["Burgers", "Healthy", "Arabic", "Desserts", "Coffee", "Pizza"],
        "offer": "30% off · First Food order",
        "sections": [
            {"title": "For you", "items": restaurants[:2]},
            {"title": "Popular near you", "items": restaurants[2:]},
        ],
        "restaurants": restaurants,
        "tabs": ["Food", "Search", "Orders", "You"],
    }


def superapp_home(question: str) -> dict:
    mk = MARKETS[_market(question)]
    return {
        "kind": "superapp",
        "label": f"Careem · {mk['city']}",
        "rtl": _rtl(question),
        "blocks": [
            {"type": "hello", "kicker": "Good evening", "title": "Careem"},
            {"type": "search", "text": "Where to?"},
            {"type": "pills", "items": ["Rides", "Food", "Quik", "Pay", "Shops", "Plus", "Bike", "Box"]},
            {"type": "offer", "text": "Plus · 10% back on your next ride"},
            {
                "type": "list",
                "title": "Recent",
                "items": [
                    {"t": "Dubai Mall", "s": "Downtown"},
                    {"t": "Marina Walk", "s": "JBR"},
                    {"t": "Airport T3", "s": "Departures"},
                ],
            },
            {"type": "tabs", "items": ["Home", "Activity", "Pay", "You"]},
        ],
    }


REPLIES = {
    "rider_home_earnings": "Here’s a Careem rider home with this month’s earnings on the first screen — cashback earned, money spent, and a weekly chart. Where to stays one tap away.",
    "captain_earnings": "Captain earnings home: monthly net, hours, and the last payouts. Peak bonus stays visible so the number is trusted.",
    "arriving": "Captain arriving: name, rating, car, plate, and ETA on the map. Call or message first. Cancel stays secondary.",
    "accept": "Accept sheet on the map: pickup, drop-off, distance, time, and fare before they tap. Two actions only.",
    "cancel": "Cancel sheet with the fee before the tap. Riders see the rule while the map and fare stay on screen.",
    "failed": "Payment failed with the trip amount and card still visible. Try Again is the only primary.",
    "completed": "Trip complete: final fare, route summary, payment method, captain, stars, optional tip, and receipt or home.",
    "food_home": "Food home: delivery location, search, categories, offers, and restaurant cards with ratings, ETA, and pricing.",
    "superapp": "Super App home: Where to, service grid, a promo, and recent places — all Careem products in one tap.",
    "advice": None,
}


def _screen_usable(screen: dict | None) -> bool:
    if not isinstance(screen, dict) or not screen:
        return False
    kind = str(screen.get("kind") or "")
    if kind == "checkout":
        return is_complete(screen, kind)
    if kind in ("arriving", "accept", "cancel", "failed", "completed", "food", "superapp"):
        return is_complete(screen, kind) or bool(
            screen.get("fare") or screen.get("captain") or screen.get("amount") or screen.get("restaurants")
        )
    blocks = screen.get("blocks")
    if isinstance(blocks, list):
        known = [
            b
            for b in blocks
            if isinstance(b, dict) and _block_type(b.get("type") or b.get("name")) in KNOWN_BLOCK_TYPES
        ]
        if len(known) >= 4:
            return True
    return bool(screen.get("fare") or screen.get("captain") or screen.get("amount"))


def _looks_like_wrong_template(goal: str, screen: dict) -> bool:
    kind = infer_screen_kind(goal)
    if kind == "generic":
        return False
    if kind == "home":
        return False
    blocks = screen.get("blocks") or []
    block_types = [b.get("type") for b in blocks if isinstance(b, dict)]
    looks_like_home = screen.get("kind") in ("dashboard", "home") or (
        "hero" in block_types and "search" in block_types and "where" in str(screen).lower()
    )
    if kind != "home" and looks_like_home:
        return True
    if kind == "completed" and screen.get("earned"):
        return True
    if kind == "food" and looks_like_home:
        return True
    stub = blocks and len(blocks) <= 3 and all(b.get("type") in ("hello", "note", "cta") for b in blocks if isinstance(b, dict))
    if kind not in ("generic", "home") and stub:
        return True
    return screen.get("kind") not in (kind, "generic", None) and kind in {
        "arriving", "accept", "cancel", "failed", "checkout", "completed", "food"
    } and looks_like_home


def prompt_screen(question: str) -> dict:
    kind = infer_screen_kind(question)
    builders = {
        "arriving": arriving_screen,
        "accept": accept_screen,
        "cancel": cancel_screen,
        "failed": failed_screen,
        "checkout": checkout_screen,
        "completed": completed_screen,
        "food": food_home,
        "home": rider_home_earnings,
        "superapp": superapp_home,
    }
    if kind in builders:
        return builders[kind](question)
    title = (question or "Careem").split(".")[0].strip()[:48] or "Careem"
    return {
        "kind": "generic",
        "label": title[:32],
        "blocks": [
            {"type": "hello", "kicker": "Careem", "title": title},
            {"type": "note", "text": "Built from your brief when the model is offline."},
            {"type": "cta", "text": "Continue", "style": "primary"},
        ],
    }


def _block_types(screen: dict) -> set[str]:
    types = set()
    for b in screen.get("blocks") or []:
        if isinstance(b, dict):
            types.add(_block_type(b.get("type") or b.get("name")))
    return types


def _money_text(value) -> str:
    text = _as_label(value).strip()
    if text.lower() in {"", "-", "—", "–", "n/a", "na", "choose a slot"}:
        return ""
    return text


def _cart_rows(screen: dict) -> list:
    rows = []
    if isinstance(screen.get("items"), list):
        rows.extend(screen["items"])
    for block in screen.get("blocks") or []:
        if isinstance(block, dict) and _block_type(block.get("type")) == "list":
            rows.extend(block.get("items") or [])
    filled = []
    for row in rows:
        if isinstance(row, dict):
            label = _as_label(row.get("t") or row.get("name") or row.get("title") or row.get("label"))
        else:
            label = _as_label(row)
        if label.strip():
            filled.append(row)
    return filled


def is_complete(screen: dict | None, kind: str = "") -> bool:
    if not isinstance(screen, dict):
        return False
    kind = kind or str(screen.get("kind") or "")
    types = _block_types(screen)
    if kind == "food":
        has_cards = "restaurants" in types or bool(screen.get("restaurants"))
        return has_cards and bool(types & {"search", "categories", "location", "offer"})
    if kind == "arriving":
        return bool(types & {"captain", "map", "sheet"}) or bool(screen.get("captain"))
    if kind == "failed":
        return "cta" in types or bool(screen.get("primary"))
    if kind == "completed":
        return bool(_money_text(screen.get("fare"))) and bool(
            screen.get("pickup") or screen.get("dest") or screen.get("captain") or "trip" in types or "tips" in types
        )
    if kind == "superapp":
        return "pills" in types and "search" in types
    if kind == "checkout":
        has_items = len(_cart_rows(screen)) >= 2
        has_total = bool(
            _money_text(screen.get("total")) or _money_text(screen.get("fee")) or _money_text(screen.get("sub"))
        )
        if not has_total:
            for block in screen.get("blocks") or []:
                if not isinstance(block, dict) or _block_type(block.get("type")) != "totals":
                    continue
                for row in block.get("rows") or block.get("items") or []:
                    if isinstance(row, dict) and _money_text(row.get("value") or row.get("s")):
                        has_total = True
                        break
        has_pay = "cta" in types or bool(_as_label(screen.get("primary")).strip())
        return has_items and has_total and has_pay
    return len(types) >= 4


def complete_screen(screen: dict, goal: str = "") -> dict:
    kind = infer_screen_kind(goal) or str(screen.get("kind") or "generic")
    screen = dict(screen or {})
    if screen.get("_locked") or screen.get("_removed"):
        banned = set(screen.get("_removed") or [])
        screen["blocks"] = [
            b for b in (screen.get("blocks") or []) if isinstance(b, dict) and b.get("type") not in banned
        ]
        return screen
    if screen.get("kind") in (None, "", "generic"):
        screen["kind"] = kind
    tmpl = ensure_blocks(prompt_screen(goal or screen.get("label") or "Careem"), goal)
    if is_complete(screen, kind):
        return screen
    have = _block_types(screen)
    banned = set(screen.get("_removed") or [])
    merged = [b for b in (screen.get("blocks") or []) if isinstance(b, dict) and b.get("type") not in banned]
    for block in tmpl.get("blocks") or []:
        t = block.get("type")
        if t and t not in have and t not in banned:
            merged.append(block)
            have.add(t)
    screen["blocks"] = merged
    screen["kind"] = kind
    for key in (
        "location",
        "search",
        "categories",
        "offer",
        "restaurants",
        "captain",
        "amount",
        "method",
        "fare",
        "items",
        "slot",
        "sub",
        "fee",
        "total",
        "primary",
        "store",
        "feeNote",
        "pickup",
        "dest",
        "duration",
        "distance",
        "tips",
        "car",
        "rating",
    ):
        if key in banned:
            continue
        if key in ("slot", "slots", "categories") and banned & {"slot", "categories"}:
            continue
        if not screen.get(key) and tmpl.get(key):
            screen[key] = tmpl[key]
    return ensure_blocks(screen, goal)


def _trim_block(block: dict, n: int) -> dict:
    item = dict(block)
    if isinstance(item.get("items"), list):
        item["items"] = item["items"][:n]
    if isinstance(item.get("rows"), list):
        item["rows"] = item["rows"][:n]
    return item


def _guided_copy(kind: str, screen: dict) -> str:
    plate = str(screen.get("plate") or "").strip()
    copies = {
        "food": "We deliver to this pin. Change it if this is not home.",
        "checkout": "Delivery fee is shown here before you tap Pay.",
        "completed": "Tip is optional. Your captain only sees it if you add one.",
        "failed": "The amount stays on this screen until you retry or change the method.",
        "arriving": f"Walk to the pin.{f' Plate {plate}.' if plate else ''}",
        "accept": "Fare is locked on this sheet before you accept.",
        "cancel": "The fee is charged if you confirm cancel.",
        "superapp": "Pick a service, or search Where to.",
        "home": "Your primary number stays above the fold.",
    }
    return copies.get(kind) or "Read the numbers on this screen before you tap."


def _direction_fastest(blocks: list[dict]) -> list[dict]:
    types = {b.get("type") for b in blocks}
    drop = {"note", "tips"}
    if types & {"hello", "hero", "sheet", "totals"}:
        drop.add("trip")
        if "map" not in types:
            drop.add("captain")
    if "list" in types and "restaurants" not in types:
        drop.add("categories")
    if "restaurants" in types:
        drop.add("offer")
    compact = bool(types & {"totals", "hello"}) and not (types & {"list", "restaurants", "map", "sheet"})
    out = []
    restaurants = 0
    ctas = 0
    for raw in blocks:
        t = raw.get("type")
        if t in drop:
            continue
        if t == "cta":
            ctas += 1
            if ctas > (1 if compact else 2):
                continue
        if t == "restaurants":
            restaurants += 1
            if restaurants > 1:
                continue
            out.append(_trim_block(raw, 2))
            continue
        if t == "list":
            out.append(_trim_block(raw, 2))
            continue
        if t in ("categories", "pills"):
            out.append(_trim_block(raw, 4))
            continue
        out.append(dict(raw))
    return out


def _direction_informative(blocks: list[dict]) -> list[dict]:
    out = []
    restaurants = 0
    for raw in blocks:
        t = raw.get("type")
        if t == "note":
            continue
        if t == "restaurants":
            restaurants += 1
            out.append(_trim_block(raw, 2 if restaurants == 1 else 3))
            continue
        if t == "list":
            out.append(_trim_block(raw, 3))
            continue
        out.append(dict(raw))
    return out


def _direction_guided(blocks: list[dict], kind: str, screen: dict) -> list[dict]:
    out = [dict(b) for b in blocks]
    if any(b.get("type") == "note" for b in out):
        return out
    note = {"type": "note", "text": _guided_copy(kind, screen)}
    insert_at = 0
    for i, block in enumerate(out):
        if block.get("type") in {"hello", "location", "search", "map", "captain"}:
            insert_at = i + 1
    out.insert(insert_at, note)
    return out


def _sync_fields_from_blocks(screen: dict) -> dict:
    blocks = [b for b in (screen.get("blocks") or []) if isinstance(b, dict)]
    types = {b.get("type") for b in blocks}
    note = next((b for b in blocks if b.get("type") == "note"), None)
    tips = next((b for b in blocks if b.get("type") == "tips"), None)
    offer = next((b for b in blocks if b.get("type") == "offer"), None)
    listing = next((b for b in blocks if b.get("type") == "list"), None)
    cats = next((b for b in blocks if b.get("type") == "categories"), None)
    totals = next((b for b in blocks if b.get("type") == "totals"), None)
    rests = [b for b in blocks if b.get("type") == "restaurants"]
    screen["helper"] = (note or {}).get("text") or ""
    screen["tips"] = (tips or {}).get("items") or []
    screen["offer"] = (offer or {}).get("text") or ""
    if listing and listing.get("items") is not None:
        screen["items"] = listing.get("items")
    if totals and (totals.get("rows") or totals.get("items")):
        screen["rows"] = totals.get("rows") or totals.get("items")
    if cats and cats.get("items") is not None:
        screen["categories"] = cats.get("items")
        screen["slots"] = cats.get("items")
        if cats.get("items"):
            screen["slot"] = cats["items"][0]
    elif set(screen.get("_removed") or []) & {"slot", "categories"} or str(screen.get("kind") or "") == "checkout":
        if "categories" not in {b.get("type") for b in blocks}:
            screen["slots"] = []
            screen["slot"] = ""
    if rests:
        screen["restaurants"] = [row for b in rests for row in (b.get("items") or [])]
        screen["sections"] = [{"title": b.get("title") or "For you", "items": b.get("items") or []} for b in rests]
    screen["showRoute"] = "trip" in types
    screen["showCaptain"] = "captain" in types
    screen["showTips"] = "tips" in types
    screen["showFeedback"] = "note" in types
    screen["showProgress"] = "note" in types or "trip" in types
    screen["showPlate"] = "captain" in types
    screen["showPickup"] = "trip" in types
    if "cta" in types:
        primary = next((b for b in blocks if b.get("type") == "cta" and b.get("style") != "secondary"), None)
        secondary = next((b for b in blocks if b.get("type") == "cta" and b.get("style") == "secondary"), None)
        if primary:
            screen["primary"] = primary.get("text") or screen.get("primary")
        screen["secondary"] = (secondary or {}).get("text") or ""
    return screen


def apply_direction(screen: dict, direction_id: str, goal: str = "") -> dict:
    """Fastest / Informative / Guided are layout rules on whatever screen this brief produced."""
    did = str(direction_id or "B").upper()[:1]
    if did not in ("A", "B", "C"):
        did = "B"
    screen = complete_screen(copy.deepcopy(screen or {}), goal)
    kind = str(screen.get("kind") or infer_screen_kind(goal) or "generic")
    names = {"A": "Fastest", "B": "Informative", "C": "Guided"}
    blocks = [dict(b) for b in (screen.get("blocks") or []) if isinstance(b, dict)]
    if did == "A":
        blocks = _direction_fastest(blocks)
    elif did == "C":
        blocks = _direction_guided(blocks, kind, screen)
    else:
        blocks = _direction_informative(blocks)
    screen["blocks"] = blocks
    screen["_direction"] = did
    screen["kind"] = kind
    screen["label"] = f"{(screen.get('label') or kind.title()).split('·')[0].strip()} · {names[did]}"
    return _sync_fields_from_blocks(screen)


def direction_reply(kind: str, direction_id: str, fallback: str = "") -> str:
    did = str(direction_id or "B").upper()[:1]
    label = (kind or "screen").replace("_", " ")
    lines = {
        "A": f"Fastest {label} — fewer blocks, the primary number and CTA above the fold.",
        "B": f"Informative {label} — prices, fees, and context stay visible before the tap.",
        "C": f"Guided {label} — a helper for first-time users, still max two actions.",
    }
    return lines.get(did) or fallback or "Here is that direction, generated from your brief."


def sanitize_blocks(screen: dict, goal: str = "") -> dict:
    """Drop earnings charts and wrong block types for transactional screens."""
    kind = infer_screen_kind(goal) if goal else str(screen.get("kind") or "generic")
    wants_earnings = kind == "home" and any(
        w in (goal or "").lower() for w in ("earnings", "monthly", "dashboard", "cashback", "spent", "analytics")
    )
    earnings_only = {"hero", "stats", "split"}
    out = []
    for raw in screen.get("blocks") or []:
        if not isinstance(raw, dict):
            continue
        b = dict(raw)
        t = b.get("type")
        if not wants_earnings and t in earnings_only:
            if t == "hero":
                text = " ".join(
                    x for x in [b.get("label"), b.get("value"), b.get("meta")] if x
                ).strip()
                if text:
                    out.append({"type": "offer", "text": text[:80]})
            continue
        if t == "hero" and not wants_earnings:
            b.pop("bars", None)
        out.append(b)
    screen["blocks"] = out
    return screen


def _as_label(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, dict):
        for key in ("label", "name", "text", "title", "t", "value"):
            if value.get(key):
                return str(value[key])
        return ""
    return str(value)


KNOWN_BLOCK_TYPES = {
    "hello",
    "location",
    "search",
    "pills",
    "categories",
    "offer",
    "section",
    "restaurants",
    "hero",
    "stats",
    "split",
    "list",
    "note",
    "map",
    "sheet",
    "captain",
    "trip",
    "rating",
    "tips",
    "totals",
    "cta",
    "tabs",
}

BLOCK_ALIASES = {
    "captaincard": "captain",
    "captainrow": "captain",
    "drivercard": "captain",
    "driver": "captain",
    "progresslist": "list",
    "progress": "list",
    "timeline": "list",
    "steps": "list",
    "listrow": "list",
    "livemap": "map",
    "drivermap": "map",
    "bottomsheet": "sheet",
    "actionsheet": "sheet",
    "button": "cta",
    "primarybutton": "cta",
    "secondarybutton": "cta",
    "searchfield": "search",
    "whereto": "search",
    "offerbanner": "offer",
    "promo": "offer",
    "promobanner": "offer",
    "banner": "offer",
    "chiprow": "pills",
    "locationbar": "location",
    "locationchip": "location",
    "deliverylocation": "location",
    "categorychips": "categories",
    "categorychiprow": "categories",
    "filters": "categories",
    "restaurantcard": "restaurants",
    "restaurantlist": "restaurants",
    "restaurant": "restaurants",
    "restaurantsrow": "restaurants",
    "bottomstickycta": "cta",
    "stickycta": "cta",
    "cartlist": "list",
    "cart": "list",
    "cartitems": "list",
    "orderitems": "list",
    "slotpicker": "categories",
    "timeslot": "categories",
    "slots": "categories",
    "deliveryaddress": "location",
    "address": "location",
}


def _block_type(value) -> str:
    raw = str(value or "note")
    key = "".join(ch for ch in raw.lower() if ch.isalpha())
    if key in BLOCK_ALIASES:
        return BLOCK_ALIASES[key]
    if raw.lower() in KNOWN_BLOCK_TYPES:
        return raw.lower()
    return raw


def normalize_blocks(screen: dict) -> dict:
    """Coerce LLM objects into strings the phone renderer can paint."""
    cleaned = []
    for raw in screen.get("blocks") or []:
        if not isinstance(raw, dict):
            continue
        b = dict(raw)
        t = _block_type(b.get("type") or b.get("name") or b.get("component"))
        b["type"] = t
        if t in ("pills", "categories", "tabs", "tips") and isinstance(b.get("items"), list):
            b["items"] = [_as_label(x) for x in b["items"] if _as_label(x)]
        if t == "list" and isinstance(b.get("items"), list):
            rows = []
            for x in b["items"]:
                if isinstance(x, dict):
                    rows.append({"t": _as_label(x.get("t") or x.get("name") or x.get("title")), "s": _as_label(x.get("s") or x.get("price") or x.get("value") or x.get("meta") or x.get("eta"))})
                else:
                    rows.append({"t": _as_label(x), "s": ""})
            b["items"] = rows
        if t == "restaurants":
            if not isinstance(b.get("items"), list) or not b.get("items"):
                if b.get("name") or b.get("title"):
                    b["items"] = [
                        {
                            "name": _as_label(b.get("name") or b.get("title")),
                            "rating": _as_label(b.get("rating") or "4.8"),
                            "eta": _as_label(b.get("eta") or "25 min"),
                            "from": _as_label(b.get("from") or b.get("price")),
                            "dish": _as_label(b.get("dish") or b.get("item")),
                            "tag": _as_label(b.get("tag")),
                        }
                    ]
            elif isinstance(b.get("items"), list):
                cards = []
                for x in b["items"]:
                    if isinstance(x, dict):
                        cards.append(
                            {
                                "name": _as_label(x.get("name") or x.get("title")),
                                "rating": _as_label(x.get("rating") or "4.8"),
                                "eta": _as_label(x.get("eta") or "25 min"),
                                "from": _as_label(x.get("from") or x.get("price")),
                                "dish": _as_label(x.get("dish") or x.get("item")),
                                "tag": _as_label(x.get("tag")),
                            }
                        )
                    elif _as_label(x):
                        cards.append({"name": _as_label(x), "rating": "4.8", "eta": "25 min", "from": "", "dish": "", "tag": ""})
                b["items"] = cards
        if t == "cta":
            b["text"] = _as_label(b.get("text") or b.get("label") or "Continue")
        if t == "trip":
            for key in ("pickup", "dest", "fare", "duration", "distance", "method"):
                if key in b:
                    b[key] = _as_label(b.get(key))
        cleaned.append(b)
    merged = []
    for b in cleaned:
        if merged and b.get("type") == "restaurants" and merged[-1].get("type") == "restaurants":
            merged[-1]["items"] = (merged[-1].get("items") or []) + (b.get("items") or [])
            continue
        merged.append(b)
    screen["blocks"] = merged
    return screen


def _blocks_from_fields(screen: dict) -> list[dict]:
    """Turn older field-based screens into renderable blocks."""
    built: list[dict] = []
    kind = str(screen.get("kind") or "")
    if screen.get("hello") or (screen.get("title") and kind in ("dashboard", "home", "superapp", "food", "generic")):
        built.append({"type": "hello", "kicker": screen.get("hello") or "Careem", "title": screen.get("title") or "Careem"})
    if screen.get("location"):
        built.append({"type": "location", "text": screen["location"]})
    if screen.get("where") or screen.get("search"):
        built.append({"type": "search", "text": screen.get("search") or screen.get("where")})
    if isinstance(screen.get("categories"), list) and screen["categories"]:
        built.append({"type": "categories", "items": screen["categories"]})
    if isinstance(screen.get("offer"), str) and screen["offer"]:
        built.append({"type": "offer", "text": screen["offer"]})
    restaurants = screen.get("restaurants") or []
    for section in screen.get("sections") or []:
        if isinstance(section, dict) and section.get("items"):
            built.append({"type": "restaurants", "title": section.get("title") or "For you", "items": section["items"]})
            restaurants = []
    if restaurants:
        built.append({"type": "restaurants", "title": "Recommended", "items": restaurants})
    if screen.get("earned"):
        built.append(
            {
                "type": "hero",
                "label": screen.get("month") or "This month",
                "value": screen.get("earned"),
                "meta": screen.get("delta") or "",
                "bars": screen.get("weeks") or [],
            }
        )
    if screen.get("stats"):
        built.append({"type": "stats", "items": screen["stats"]})
    if screen.get("split"):
        items = []
        for row in screen["split"]:
            if isinstance(row, dict):
                items.append(row)
            elif isinstance(row, (list, tuple)) and len(row) >= 2:
                items.append({"n": row[0], "p": row[1]})
        if items:
            built.append({"type": "split", "items": items})
    if screen.get("trips") or screen.get("recent_title"):
        trips = []
        for row in screen.get("trips") or []:
            if isinstance(row, dict):
                trips.append({"t": row.get("t") or row.get("name"), "s": row.get("s") or row.get("meta")})
            elif isinstance(row, (list, tuple)):
                trips.append({"t": row[0], "s": row[1] if len(row) > 1 else ""})
        built.append({"type": "list", "title": screen.get("recent_title") or "Recent", "items": trips})
    if kind in ("arriving", "accept", "cancel") or screen.get("captain") or screen.get("pickup"):
        if kind in ("arriving", "accept", "cancel") or screen.get("map"):
            built.append({"type": "map"})
        if screen.get("captain"):
            built.append(
                {
                    "type": "captain",
                    "name": screen.get("captain"),
                    "rating": screen.get("rating") or "4.9",
                    "car": screen.get("car") or "",
                    "plate": screen.get("plate") or "",
                }
            )
    if screen.get("pickup") or screen.get("dest") or screen.get("fare"):
        built.append(
            {
                "type": "trip",
                "pickup": screen.get("pickup"),
                "dest": screen.get("dest"),
                "fare": screen.get("fare") or screen.get("amount"),
                "method": screen.get("method"),
                "duration": screen.get("duration"),
                "distance": screen.get("distance"),
            }
        )
    if isinstance(screen.get("items"), list) and screen["items"] and kind in ("checkout", "generic", ""):
        rows = []
        for row in screen["items"]:
            if isinstance(row, dict):
                rows.append({"t": row.get("t") or row.get("name"), "s": row.get("s") or row.get("price")})
            elif isinstance(row, (list, tuple)):
                rows.append({"t": row[0], "s": row[1] if len(row) > 1 else ""})
        if rows:
            built.append({"type": "list", "title": "Cart", "items": rows})
    if screen.get("slot") and "slot" not in set(screen.get("_removed") or []) and "categories" not in set(screen.get("_removed") or []):
        built.append({"type": "categories", "items": [screen["slot"]] if isinstance(screen["slot"], str) else screen.get("slots") or [screen["slot"]]})
    if screen.get("sub") or screen.get("fee") or screen.get("total"):
        built.append(
            {
                "type": "totals",
                "rows": [
                    {"label": "Subtotal", "value": screen.get("sub") or ""},
                    {"label": "Delivery", "value": screen.get("fee") or ""},
                    {"label": "Total", "value": screen.get("total") or ""},
                ],
            }
        )
    if kind in ("arriving", "accept", "cancel"):
        built.append(
            {
                "type": "sheet",
                "title": screen.get("title") or ("Captain is arriving" if kind == "arriving" else "Confirm"),
                "sub": screen.get("eta") or screen.get("feeNote") or "",
                "fee": screen.get("fee"),
                "feeNote": screen.get("feeNote") or "",
                "primary": screen.get("primary") or "Continue",
                "secondary": screen.get("secondary") or "",
            }
        )
    elif kind == "checkout" and screen.get("primary"):
        built.append({"type": "cta", "text": screen["primary"]})
        if screen.get("secondary"):
            built.append({"type": "cta", "text": screen["secondary"], "style": "secondary"})
    if kind == "failed" or (screen.get("amount") and screen.get("method") and not any(b.get("type") == "totals" for b in built)):
        built.append({"type": "hello", "kicker": "Payment", "title": screen.get("title") or "Payment failed"})
        built.append(
            {
                "type": "totals",
                "rows": [
                    {"label": "Trip amount", "value": screen.get("amount") or screen.get("fare") or ""},
                    {"label": "Card", "value": screen.get("method") or "Visa **** 1234"},
                ],
            }
        )
        built.append({"type": "cta", "text": screen.get("primary") or "Try Again"})
        built.append({"type": "cta", "text": screen.get("secondary") or "Change Payment", "style": "secondary"})
    if kind == "completed":
        if screen.get("fare"):
            built.append({"type": "hello", "kicker": "Trip complete", "title": screen.get("fare")})
        if screen.get("tips"):
            built.append({"type": "tips", "items": screen["tips"]})
        if screen.get("rating"):
            built.append({"type": "rating", "value": screen.get("rating")})
        if screen.get("primary"):
            built.append({"type": "cta", "text": screen.get("primary")})
        if screen.get("secondary"):
            built.append({"type": "cta", "text": screen["secondary"], "style": "secondary"})
    if isinstance(screen.get("tabs"), list) and screen["tabs"]:
        built.append({"type": "tabs", "items": screen["tabs"]})
    elif screen.get("cta") and not any(b.get("type") == "cta" for b in built):
        built.append({"type": "cta", "text": screen["cta"]})
    seen = set()
    unique = []
    for block in built:
        key = (block.get("type"), block.get("title"), block.get("text"), block.get("value"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(block)
    return unique[:12]


def ensure_blocks(screen: dict, goal: str = "") -> dict:
    if not isinstance(screen, dict):
        return {"kind": "generic", "label": "Careem", "blocks": [{"type": "note", "text": "No screen yet."}]}
    blocks = []
    for raw in screen.get("blocks") or []:
        if not isinstance(raw, dict):
            continue
        item = dict(raw)
        item["type"] = _block_type(item.get("type") or item.get("name") or item.get("component"))
        if item["type"] in KNOWN_BLOCK_TYPES:
            blocks.append(item)
    kind = infer_screen_kind(goal) if goal else str(screen.get("kind") or "generic")
    if kind and screen.get("kind") in (None, "", "generic"):
        screen["kind"] = kind
    screen["blocks"] = blocks
    banned = set(screen.get("_removed") or [])
    if screen.get("_locked") or banned:
        screen["blocks"] = [b for b in blocks if b.get("type") not in banned]
        if banned & {"slot", "categories"}:
            screen["slot"] = ""
            screen["slots"] = []
            screen["categories"] = []
            if re.search(r"slot", str(screen.get("secondary") or ""), re.I):
                screen["secondary"] = ""
        return screen
    if len(blocks) >= 2 and is_complete(screen, kind or screen.get("kind") or ""):
        return screen
    converted = [b for b in _blocks_from_fields(screen) if b.get("type") not in banned]
    if converted:
        screen["blocks"] = converted
        if is_complete(screen, kind or screen.get("kind") or ""):
            return screen
    kind = infer_screen_kind(goal) if goal else str(screen.get("kind") or "generic")
    builders = {
        "arriving": arriving_screen,
        "accept": accept_screen,
        "cancel": cancel_screen,
        "failed": failed_screen,
        "checkout": checkout_screen,
        "completed": completed_screen,
        "food": food_home,
        "home": rider_home_earnings,
        "superapp": superapp_home,
    }
    if kind in builders:
        tmpl = builders[kind](goal or screen.get("label") or "Careem")
        fallback = tmpl.get("blocks") or _blocks_from_fields(tmpl)
        if fallback:
            screen["kind"] = tmpl.get("kind") or kind
            screen["label"] = screen.get("label") or tmpl.get("label") or "Careem"
            screen["blocks"] = fallback
            for key, value in tmpl.items():
                if key in ("blocks", "kind", "label") or screen.get(key):
                    continue
                screen[key] = value
            return screen
    screen["blocks"] = converted or [
        {"type": "hello", "kicker": "Careem", "title": screen.get("label") or "Home"},
        {"type": "search", "text": "Where to?"},
        {"type": "pills", "items": ["Rides", "Food", "Quik", "Pay"]},
        {"type": "cta", "text": "Continue"},
    ]
    return screen


def _clean_screen(screen: dict, goal: str = "", brief: dict | None = None) -> dict:
    if not isinstance(screen, dict):
        return {}
    screen.setdefault("kind", "generic")
    screen.setdefault("label", "Careem")
    lang = str((brief or {}).get("language") or "EN").upper()
    wants_ar = lang == "AR" or _rtl(goal)
    screen["rtl"] = bool(wants_ar)
    blocks = screen.get("blocks")
    if isinstance(blocks, list):
        cleaned = []
        for raw in blocks[:12]:
            if not isinstance(raw, dict):
                continue
            item = dict(raw)
            item["type"] = str(item.get("type") or "note")
            cleaned.append(item)
        screen["blocks"] = cleaned
    if goal:
        sanitize_blocks(screen, goal)
    normalize_blocks(screen)
    return ensure_blocks(screen, goal)


EDIT_REMOVE = re.compile(
    r"(?:remove|hide|delete|drop|clear|get rid of|take off|without|no more|don't show|do not show)\s+(?:the\s+|a\s+|an\s+)?(.+?)(?:\s+from\b.*)?\s*$",
    re.I,
)
EDIT_ADD = re.compile(
    r"(?:add|show|include|put back|restore)\s+(?:a\s+|the\s+)?(.+?)(?:\s+back)?\s*$",
    re.I,
)
EDIT_CHANGE = re.compile(
    r"(?:change|rename|replace|update|make)\s+(?:the\s+)?(.+?)\s+(?:to|say|read)\s+(.+?)\s*$",
    re.I,
)

TARGET_TYPES = [
    (("delivery slot", "slot picker", "time slot", "timeslot", "slots", "slot"), ("categories",)),
    (("promo", "offer", "banner", "discount"), ("offer",)),
    (("helper", "note", "hint", "guidance"), ("note",)),
    (("cart", "cart items", "items", "order items"), ("list",)),
    (("address", "location", "pin"), ("location",)),
    (("search", "where to"), ("search",)),
    (("map",), ("map",)),
    (("captain", "driver"), ("captain",)),
    (("tips", "tip chips", "tip"), ("tips",)),
    (("stars", "rating"), ("rating",)),
    (("route", "trip summary", "pickup", "drop-off", "drop off"), ("trip",)),
    (("tabs", "tab bar"), ("tabs",)),
    (("categories", "chips", "filters"), ("categories",)),
]


def _edit_target(phrase: str) -> tuple[set[str], str]:
    raw = re.sub(r"^(the|a|an)\s+", "", (phrase or "").strip(), flags=re.I)
    key = re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()
    key = re.sub(r"\b(from|the|a|an|please|screen|checkout|canvas|phone|preview|this|that)\b", " ", key)
    key = re.sub(r"\s+", " ", key).strip()
    types: set[str] = set()
    for needles, mapped in TARGET_TYPES:
        if any(n in key for n in needles):
            types.update(mapped)
    return types, key


def _block_blob(block: dict) -> str:
    parts = [str(block.get("type") or ""), str(block.get("text") or ""), str(block.get("title") or ""), str(block.get("kicker") or "")]
    for item in block.get("items") or block.get("rows") or []:
        if isinstance(item, dict):
            parts.extend(str(item.get(k) or "") for k in ("t", "s", "label", "value", "name", "text"))
        else:
            parts.append(str(item))
    return " ".join(parts).lower()


def _looks_like_slots(block: dict) -> bool:
    if block.get("type") != "categories":
        return False
    blob = _block_blob(block)
    return bool(re.search(r"today|tomorrow|\d\s*[-–]\s*\d|\bam\b|\bpm\b|slot", blob))


def _drop_slots(screen: dict, blocks: list, removed: set) -> list:
    kept = [
        b
        for b in blocks
        if not (
            _looks_like_slots(b)
            or (str(screen.get("kind") or "") == "checkout" and b.get("type") == "categories")
            or (b.get("type") == "cta" and "slot" in _block_blob(b))
        )
    ]
    removed.update({"categories", "slot"})
    screen["slot"] = ""
    screen["slots"] = []
    screen["categories"] = []
    if re.search(r"slot", str(screen.get("secondary") or ""), re.I):
        screen["secondary"] = ""
    return kept


def apply_edit(screen: dict, command: str) -> tuple[dict, str, bool]:
    """Apply a designer command to the current canvas. Returns (screen, reply, applied)."""
    screen = copy.deepcopy(screen or {})
    q = str(command or "").strip()
    if not q or not isinstance(screen, dict):
        return screen, "", False
    blocks = [dict(b) for b in (screen.get("blocks") or []) if isinstance(b, dict)]
    if not blocks:
        blocks = [dict(b) for b in _blocks_from_fields(screen) if isinstance(b, dict)]
    removed = set(screen.get("_removed") or [])
    wants_off = bool(
        re.search(r"\b(remove|hide|delete|drop|clear|without|no more)\b", q, re.I)
        or re.search(r"get rid of|take off|don't show|do not show", q, re.I)
    )

    change = EDIT_CHANGE.search(q)
    if change:
        src, dst = change.group(1).strip().strip("\"'"), change.group(2).strip().strip("\"'")
        src = re.sub(r"^(button|cta|copy|label|text)\s+", "", src, flags=re.I)
        hit = False
        for block in blocks:
            for field in ("text", "title", "kicker", "primary", "secondary"):
                if src.lower() in str(block.get(field) or "").lower():
                    block[field] = re.sub(re.escape(src), dst, str(block[field]), flags=re.I)
                    hit = True
            items = block.get("items")
            if isinstance(items, list):
                nxt = []
                for item in items:
                    if isinstance(item, str) and src.lower() in item.lower():
                        nxt.append(re.sub(re.escape(src), dst, item, flags=re.I))
                        hit = True
                    elif isinstance(item, dict):
                        row = dict(item)
                        for field in ("t", "s", "name", "text"):
                            if src.lower() in str(row.get(field) or "").lower():
                                row[field] = re.sub(re.escape(src), dst, str(row[field]), flags=re.I)
                                hit = True
                        nxt.append(row)
                    else:
                        nxt.append(item)
                block["items"] = nxt
        for field in ("primary", "secondary", "title", "store", "helper", "offer", "slot"):
            if src.lower() in str(screen.get(field) or "").lower():
                screen[field] = re.sub(re.escape(src), dst, str(screen[field]), flags=re.I)
                hit = True
        if hit:
            screen["blocks"] = blocks
            screen["_locked"] = True
            return screen, f"Updated “{src}” to “{dst}”.", True

    if wants_off and re.search(r"\bslots?\b", q, re.I):
        blocks = _drop_slots(screen, blocks, removed)
        screen["blocks"] = blocks
        screen["_removed"] = sorted(removed)
        screen["_locked"] = True
        return screen, "Removed delivery slot from the canvas.", True

    add = None if wants_off else EDIT_ADD.search(q)
    if add:
        types, key = _edit_target(add.group(1))
        if types:
            removed -= types
            if "categories" in types:
                removed.discard("slot")
            screen["_removed"] = sorted(removed)
            goal = screen.get("label") or str(screen.get("kind") or "Careem")
            tmpl = ensure_blocks(prompt_screen(goal), goal)
            extra = [b for b in (tmpl.get("blocks") or []) if isinstance(b, dict) and b.get("type") in types]
            have = {b.get("type") for b in blocks}
            for block in extra:
                if block.get("type") not in have:
                    blocks.append(block)
                    have.add(block.get("type"))
            screen["blocks"] = blocks
            screen["_locked"] = True
            if "categories" in types:
                cats = next((b for b in blocks if b.get("type") == "categories"), None)
                screen["slots"] = (cats or {}).get("items") or tmpl.get("slots") or []
                screen["slot"] = (screen["slots"] or [tmpl.get("slot")])[0] if (screen["slots"] or tmpl.get("slot")) else ""
            return screen, f"Added {key} back onto the canvas.", True

    remove = EDIT_REMOVE.search(q) if wants_off else None
    if remove:
        types, key = _edit_target(remove.group(1) if hasattr(remove, "group") else q)
        kind = str(screen.get("kind") or "")
        drop_slots = "categories" in types and (
            "slot" in key or kind == "checkout" or any(_looks_like_slots(b) for b in blocks)
        )
        kept = []
        dropped = []
        for block in blocks:
            blob = _block_blob(block)
            type_hit = block.get("type") in types
            if drop_slots and _looks_like_slots(block):
                type_hit = True
            text_hit = bool(key) and len(key) > 2 and key in blob and block.get("type") in {
                "categories", "offer", "note", "cta", "pills", "tips", "location", "search"
            }
            cta_hit = block.get("type") == "cta" and (
                ("slot" in key and "slot" in blob) or (key and key in blob)
            )
            if type_hit or text_hit or cta_hit:
                dropped.append(block.get("type"))
                continue
            kept.append(block)
        if dropped or types:
            if types:
                removed.update(types)
            if drop_slots:
                kept = _drop_slots(screen, kept, removed)
            for t in dropped:
                if t and t != "cta":
                    removed.add(t)
            screen["blocks"] = kept
            screen["_removed"] = sorted(removed)
            screen["_locked"] = True
            if "list" in types:
                screen["items"] = []
            if "offer" in types:
                screen["offer"] = ""
            if "note" in types:
                screen["helper"] = ""
            if "tips" in types:
                screen["tips"] = []
            if "location" in types:
                screen["location"] = ""
            return screen, f"Removed {key} from the canvas.", bool(dropped or types)
    return screen, "", False


def converse(question: str, history: list | None = None, dna: dict | None = None, screen: dict | None = None) -> dict:
    current = screen if isinstance(screen, dict) else None
    if current and (current.get("blocks") or current.get("kind")):
        edited, reply, applied = apply_edit(current, question)
        if applied:
            return {
                "reply": reply,
                "intent": "edit",
                "screen": edited,
                "topic": "edit",
                "confidence": 1,
                "evidence": [],
                "model": "studio-edit",
                "design_system": None,
                "critic": {"score": 92, "note": reply},
                "choices": [],
            }
    try:
        prompt = question
        if current and (current.get("blocks") or current.get("kind")):
            prompt = (
                f"Edit this Careem screen. Command: {question}\n"
                f"Keep the same kind and do not add back removed sections.\n"
                f"Current screen JSON: {str(current)[:3500]}"
            )
        data, model = design(prompt, history, dna)
        next_screen = _clean_screen(data.get("screen") or {}, question)
        if current:
            next_screen["_removed"] = list(current.get("_removed") or [])
            next_screen["_locked"] = True
            next_screen, _, _ = apply_edit(next_screen, question)
            banned = set(next_screen.get("_removed") or [])
            next_screen["blocks"] = [
                b for b in (next_screen.get("blocks") or []) if isinstance(b, dict) and b.get("type") not in banned
            ]
        else:
            next_screen = complete_screen(next_screen, question)
        if not _screen_usable(next_screen) or _looks_like_wrong_template(question, next_screen):
            if current:
                edited, reply, applied = apply_edit(copy.deepcopy(current), question)
                if applied:
                    return {
                        "reply": reply,
                        "intent": "edit",
                        "screen": edited,
                        "topic": "edit",
                        "confidence": 1,
                        "evidence": [],
                        "model": "studio-edit",
                        "design_system": None,
                        "critic": {"score": 90, "note": reply},
                        "choices": [],
                    }
            raise ValueError("Model returned an unusable screen")
        critic = data.get("critic") if isinstance(data.get("critic"), dict) else {}
        choices = data.get("choices") if isinstance(data.get("choices"), list) else []
        ds = data.get("design_system") if isinstance(data.get("design_system"), dict) else None
        return {
            "reply": data.get("reply") or "Here is the screen.",
            "intent": data.get("intent") or "screen",
            "screen": next_screen,
            "topic": data.get("intent") or "screen",
            "confidence": 0.9,
            "evidence": [],
            "model": model,
            "design_system": ds,
            "critic": {
                "score": int(critic.get("score") or 90),
                "note": str(critic.get("note") or "Matches Careem components and your DNA."),
            },
            "choices": [
                {"id": str(c.get("id") or f"c{i}"), "label": str(c.get("label") or "Adjust")}
                for i, c in enumerate(choices)
                if isinstance(c, dict)
            ][:3],
        }
    except Exception:
        if current:
            return {
                "reply": "I kept the current canvas. Try a more specific edit like “remove the promo” or “change Pay now to Place order”.",
                "intent": "edit",
                "screen": current,
                "topic": "edit",
                "confidence": 0.5,
                "evidence": [],
                "model": "studio-edit",
                "design_system": None,
                "critic": {"score": 80, "note": "Kept the live canvas instead of replacing it."},
                "choices": [],
            }
        fallback = ensure_blocks(prompt_screen(question), question)
        return {
            "reply": "Here is a working screen for that step. Refine the copy or layout in the composer.",
            "intent": infer_screen_kind(question) or "screen",
            "screen": fallback,
            "topic": infer_screen_kind(question) or "screen",
            "confidence": 0.6,
            "evidence": [],
            "model": "studio-fallback",
            "design_system": None,
            "critic": {"score": 80, "note": "Fallback blocks so the canvas never goes blank."},
            "choices": [],
        }
