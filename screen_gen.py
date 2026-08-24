"""Turn a designer prompt into a chat reply + a real phone screen."""

from __future__ import annotations

import copy

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
        return "food_home"
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
    return {
        "kind": "checkout",
        "title": "Checkout",
        "label": f"Checkout · {mk['city']}",
        "rtl": _rtl(question),
        "store": "Spinneys · JLT",
        "slot": "Today · 6–8 pm",
        "items": [
            {"t": "Oat milk 1L", "s": f"{mk['cur']} 12"},
            {"t": "Baby spinach", "s": f"{mk['cur']} 9"},
            {"t": "Eggs · 12", "s": f"{mk['cur']} 20"},
        ],
        "sub": f"{mk['cur']} 41",
        "fee": f"{mk['cur']} 9",
        "feeNote": "Delivery fee · shown before you pay",
        "total": f"{mk['cur']} 50",
        "primary": "Pay now",
        "secondary": "Change slot",
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
    if kind in ("arriving", "accept", "cancel", "failed", "checkout", "completed", "food", "superapp"):
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
        return bool(screen.get("fare")) or "trip" in types or "hello" in types
    if kind == "superapp":
        return "pills" in types and "search" in types
    if kind == "checkout":
        return "totals" in types or bool(screen.get("total"))
    return len(types) >= 4


def complete_screen(screen: dict, goal: str = "") -> dict:
    kind = infer_screen_kind(goal) or str(screen.get("kind") or "generic")
    screen = dict(screen or {})
    if screen.get("kind") in (None, "", "generic"):
        screen["kind"] = kind
    tmpl = ensure_blocks(prompt_screen(goal or screen.get("label") or "Careem"), goal)
    if is_complete(screen, kind):
        return screen
    have = _block_types(screen)
    merged = [b for b in (screen.get("blocks") or []) if isinstance(b, dict)]
    for block in tmpl.get("blocks") or []:
        t = block.get("type")
        if t and t not in have:
            merged.append(block)
            have.add(t)
    screen["blocks"] = merged
    screen["kind"] = kind
    for key in ("location", "search", "categories", "offer", "restaurants", "captain", "amount", "method", "fare"):
        if not screen.get(key) and tmpl.get(key):
            screen[key] = tmpl[key]
    return ensure_blocks(screen, goal)


def apply_direction(screen: dict, direction_id: str, goal: str = "") -> dict:
    """Make Fastest / Informative / Guided actually different layouts."""
    screen = copy.deepcopy(screen or {})
    did = str(direction_id or "B").upper()[:1]
    if did not in ("A", "B", "C"):
        did = "B"
    kind = str(screen.get("kind") or infer_screen_kind(goal) or "generic")
    names = {"A": "Fastest", "B": "Informative", "C": "Guided"}
    screen["_direction"] = did
    screen["kind"] = kind
    screen["label"] = f"{(screen.get('label') or kind.title()).split('·')[0].strip()} · {names[did]}"
    blocks = [b for b in (screen.get("blocks") or []) if isinstance(b, dict)]

    if kind == "food":
        rests: list[dict] = []
        for b in blocks:
            if b.get("type") == "restaurants":
                rests.extend(b.get("items") or [])
        if not rests:
            rests = list(food_home(goal).get("restaurants") or [])
        loc = next((b for b in blocks if b.get("type") == "location"), None) or {
            "type": "location",
            "text": screen.get("location") or "Marina Walk, JBR",
        }
        search = next((b for b in blocks if b.get("type") == "search"), None) or {
            "type": "search",
            "text": screen.get("search") or "Search restaurants or dishes",
        }
        if did == "A":
            keep, cats, offer, helper = rests[:2], ["Burgers", "Arabic", "Pizza", "Coffee"], "30% off first order", ""
            title = "For you"
        elif did == "C":
            keep, cats, offer, helper = (
                rests[:3],
                ["Burgers", "Healthy", "Arabic", "Desserts", "Coffee", "Pizza"],
                "30% off · First Food order · FOOD20",
                "We deliver to this pin. Change it if this is not home.",
            )
            title = "Start here"
        else:
            keep, cats, offer, helper = (
                rests[:4],
                ["Burgers", "Healthy", "Arabic", "Desserts", "Coffee", "Pizza"],
                "Free delivery over AED 40 · Plus",
                "",
            )
            title = "Recommended"
        rebuilt = [
            loc,
            search,
            {"type": "categories", "items": cats},
            {"type": "offer", "text": offer},
        ]
        if helper:
            rebuilt.append({"type": "note", "text": helper})
        rebuilt.append({"type": "restaurants", "title": title, "items": keep[:2] if did == "A" else keep[:2]})
        if did != "A" and keep[2:]:
            rebuilt.append({"type": "restaurants", "title": "Popular near you", "items": keep[2:]})
        rebuilt.append({"type": "tabs", "items": ["Food", "Search", "Orders", "You"]})
        screen["blocks"] = rebuilt
        screen["helper"] = helper
        screen["offer"] = offer
        screen["categories"] = cats
        screen["restaurants"] = keep
        screen["location"] = loc.get("text")
        screen["search"] = search.get("text")
        return screen

    if kind == "failed":
        amount = screen.get("amount") or screen.get("fare") or "AED 25.00"
        method = screen.get("method") or "Visa **** 1234"
        if did == "A":
            rows = [{"label": "Trip amount", "value": amount}]
            helper = ""
            sub = "Retry with the same card"
        elif did == "C":
            rows = [{"label": "Trip amount", "value": amount}, {"label": "Card", "value": method}]
            helper = "Your card was declined. The amount stays on this screen until you retry or change the method."
            sub = "Choose how you want to pay"
        else:
            rows = [
                {"label": "Trip amount", "value": amount},
                {"label": "Card", "value": method},
                {"label": "Time", "value": "Just now"},
            ]
            helper = ""
            sub = "Payment could not be processed"
        screen["blocks"] = [
            {"type": "hello", "kicker": "Pay", "title": "Payment failed"},
            *( [{"type": "note", "text": helper}] if helper else [] ),
            {"type": "totals", "rows": rows},
            {"type": "cta", "text": "Try Again"},
            {"type": "cta", "text": "Change Payment", "style": "secondary"},
        ]
        screen["amount"] = amount
        screen["method"] = method
        screen["helper"] = helper
        screen["sub"] = sub
        screen["rows"] = rows
        return screen

    if kind == "arriving":
        name = screen.get("captain") or "Yousef"
        if did == "A":
            screen["helper"] = ""
            screen["eta"] = screen.get("eta") or "3 min"
            screen["secondary"] = "Message"
        elif did == "C":
            screen["helper"] = f"Walk to the pin. Plate {screen.get('plate') or 'D-17234'}."
            screen["eta"] = screen.get("eta") or "3 min"
        else:
            screen["helper"] = ""
        rebuilt = [b for b in blocks if b.get("type") in {"map", "captain", "trip", "sheet", "note"}]
        if not any(b.get("type") == "map" for b in rebuilt):
            rebuilt.insert(0, {"type": "map"})
        if did == "C" and screen.get("helper") and not any(b.get("type") == "note" for b in rebuilt):
            rebuilt.append({"type": "note", "text": screen["helper"]})
        if rebuilt:
            screen["blocks"] = rebuilt
        return screen

    if kind == "superapp" and did == "A":
        screen["blocks"] = [b for b in blocks if b.get("type") in {"hello", "search", "pills", "tabs"}]
        if len(screen["blocks"]) < 3:
            screen["blocks"] = superapp_home(goal).get("blocks") or screen["blocks"]
        return screen

    return screen


def direction_reply(kind: str, direction_id: str, fallback: str = "") -> str:
    did = str(direction_id or "B").upper()[:1]
    table = {
        "food": {
            "A": "Fastest Food home — search and two restaurants above the fold. Categories stay one row.",
            "B": "Informative Food home — location, offer, and cards with rating, ETA, and from-price.",
            "C": "Guided Food home — a helper under search so first-time users can change the delivery pin.",
        },
        "failed": {
            "A": "Fastest payment failed — trip amount and Try Again first. Change Payment stays secondary.",
            "B": "Informative payment failed — amount, card, and time stay visible before they retry.",
            "C": "Guided payment failed — a short reason the charge failed, then Try Again or Change Payment.",
        },
        "arriving": {
            "A": "Fastest arriving — ETA and Call on the first glance. Cancel stays a text action.",
            "B": "Informative arriving — name, rating, car, and plate before they wait.",
            "C": "Guided arriving — a pin hint and plate so new riders can find the car.",
        },
        "superapp": {
            "A": "Fastest Super App — Where to and the service grid above the fold.",
            "B": "Informative Super App — services, a promo, and recent places without hunting.",
            "C": "Guided Super App — new users see every Careem product and how to search.",
        },
    }
    return (table.get(kind) or {}).get(did) or fallback or "Here is that direction, generated from your brief."


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
    "stickybutton": "cta",
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
                    rows.append({"t": _as_label(x.get("t") or x.get("name") or x.get("title")), "s": _as_label(x.get("s") or x.get("meta") or x.get("eta"))})
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
        if kind in ("arriving", "accept", "cancel") or screen.get("primary"):
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
        if screen.get("rating") and not screen.get("captain"):
            built.append({"type": "rating", "value": screen.get("rating")})
        if screen.get("primary"):
            built.append({"type": "cta", "text": screen.get("primary")})
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
    if len(blocks) >= 2:
        screen["blocks"] = blocks
        return screen
    converted = _blocks_from_fields(screen)
    if len(converted) >= 2:
        screen["blocks"] = converted
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


def converse(question: str, history: list | None = None, dna: dict | None = None) -> dict:
    try:
        data, model = design(question, history, dna)
        screen = _clean_screen(data.get("screen") or {}, question)
        if not _screen_usable(screen) or _looks_like_wrong_template(question, screen):
            raise ValueError("Model returned an unusable screen")
        critic = data.get("critic") if isinstance(data.get("critic"), dict) else {}
        choices = data.get("choices") if isinstance(data.get("choices"), list) else []
        ds = data.get("design_system") if isinstance(data.get("design_system"), dict) else None
        return {
            "reply": data.get("reply") or "Here is the screen.",
            "intent": data.get("intent") or "screen",
            "screen": screen,
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
        screen = ensure_blocks(prompt_screen(question), question)
        return {
            "reply": "Here is a working screen for that step. Refine the copy or layout in the composer.",
            "intent": infer_screen_kind(question) or "screen",
            "screen": screen,
            "topic": infer_screen_kind(question) or "screen",
            "confidence": 0.6,
            "evidence": [],
            "model": "studio-fallback",
            "design_system": None,
            "critic": {"score": 80, "note": "Fallback blocks so the canvas never goes blank."},
            "choices": [],
        }
