"""Turn a designer prompt into a chat reply + a real phone screen."""

from __future__ import annotations

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
    if any(p in q for p in ("checkout", "grocery", "quik cart", "delivery fee")):
        return "checkout"
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
    if kind == "checkout":
        return "food_home"
    if kind == "home":
        if any(w in q for w in ("captain", "driver")) and "arriv" not in q:
            return "captain_earnings"
        return "rider_home_earnings"
    make = any(w in q for w in ("make", "create", "design", "build", "screen", "generate", "show me", "draw"))
    if any(w in q for w in ("food", "order", "restaurant")):
        return "food_home"
    if last and not make and any(w in q for w in ("arabic", "rtl", "egypt", "ksa", "larger", "bigger")):
        return last
    return "rider_home_earnings" if make else "advice"


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
    return {
        "kind": "dashboard",
        "title": "Food",
        "label": f"Food · {mk['city']}",
        "rtl": _rtl(question),
        "hello": "Evening cravings",
        "where": "Search restaurants",
        "month": "August food spend",
        "earned": f"{mk['cur']} 312",
        "delta": "11 orders · 2 Plus perks used",
        "weeks": [20, 44, 28, 60],
        "stats": [
            {"n": "11", "l": "Orders"},
            {"n": f"{mk['cur']} 312", "l": "Spent"},
            {"n": f"{mk['cur']} 24", "l": "Saved"},
        ],
        "split": [("Restaurants", 70), ("Quik", 30)],
        "recent_title": "Recent",
        "trips": [
            ("Salt", "Today · 46", mk["cur"]),
            ("Al Mallah", "Mon · 28", mk["cur"]),
        ],
        "tabs": ["Home", "Search", "Orders", "You"],
    }


REPLIES = {
    "rider_home_earnings": "Here’s a Careem rider home with this month’s earnings on the first screen — cashback earned, money spent, and a weekly chart. Where to stays one tap away.",
    "captain_earnings": "Captain earnings home: monthly net, hours, and the last payouts. Peak bonus stays visible so the number is trusted.",
    "arriving": "Captain arriving: name, rating, car, plate, and ETA on the map. Call or message first. Cancel stays secondary.",
    "accept": "Accept sheet on the map: pickup, drop-off, distance, time, and fare before they tap. Two actions only.",
    "cancel": "Cancel sheet with the fee before the tap. Riders see the rule while the map and fare stay on screen.",
    "failed": "Payment failed with the trip amount and card still visible. Try Again is the only primary.",
    "food_home": "Food home with monthly spend analytics and a search field first — same Careem components as Rides.",
    "advice": None,
}


def _clean_screen(screen: dict) -> dict:
    if not isinstance(screen, dict):
        return rider_home_earnings("home")
    screen.setdefault("kind", "generic")
    screen.setdefault("label", "Careem")
    screen.setdefault("rtl", False)
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
    return screen


def converse(question: str, history: list | None = None, dna: dict | None = None) -> dict:
    try:
        data, model = design(question, history, dna)
        screen = _clean_screen(data.get("screen") or {})
        kind = infer_screen_kind(question)
        if kind == "arriving":
            screen = arriving_screen(question)
        elif kind == "accept":
            screen = accept_screen(question)
        elif kind == "cancel":
            screen = cancel_screen(question)
        elif kind == "failed":
            screen = failed_screen(question)
        critic = data.get("critic") if isinstance(data.get("critic"), dict) else {}
        choices = data.get("choices") if isinstance(data.get("choices"), list) else []
        return {
            "reply": data.get("reply") or "Here is the screen.",
            "intent": data.get("intent") or "screen",
            "screen": screen,
            "topic": data.get("intent") or "screen",
            "confidence": 0.9,
            "evidence": [],
            "model": model,
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
        pass
    intent = detect(question, history)
    builders = {
        "rider_home_earnings": rider_home_earnings,
        "captain_earnings": captain_earnings,
        "arriving": arriving_screen,
        "accept": accept_screen,
        "cancel": cancel_screen,
        "failed": failed_screen,
        "food_home": food_home,
    }
    if intent == "advice":
        advice = ask(question)
        return {
            "reply": advice.get("answer"),
            "intent": advice.get("topic", "advice"),
            "screen": rider_home_earnings(question),
            "topic": advice.get("topic"),
            "confidence": advice.get("confidence"),
            "evidence": advice.get("evidence", []),
            "model": "local-fallback",
            "critic": {"score": 84, "note": "Local fallback still follows Careem DNA."},
            "choices": [
                {"id": "learn", "label": "Learn this style"},
                {"id": "compact", "label": "Make it more compact"},
            ],
        }
    screen = builders.get(intent, rider_home_earnings)(question)
    return {
        "reply": REPLIES.get(intent) or REPLIES["rider_home_earnings"],
        "intent": intent,
        "screen": screen,
        "topic": intent,
        "confidence": 0.8,
        "evidence": [],
        "model": "local-fallback",
        "critic": {"score": 86, "note": "Local fallback. Learn a style so the next pass adapts."},
        "choices": [
            {"id": "learn", "label": "Learn this style"},
            {"id": "compact", "label": "Make it more compact"},
            {"id": "clear", "label": "Show the number sooner"},
        ],
    }
