"""Local analysis + generation for Pulse, the Careem Design Companion.

Works offline. Clusters dummy usability notes, then drafts Careem-voiced
copy and layout hypotheses grounded in the selected evidence.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field


THEMES = {
    "fare_transparency": {
        "label": "Fare transparency",
        "need": "Show a trustworthy price before and during booking",
        "keywords": (
            "fare", "price", "estimate", "surge", "promo", "cost", "charged",
            "sar", "aed", "total", "busy area", "adjustment", "toll",
        ),
    },
    "matching_anxiety": {
        "label": "Matching anxiety",
        "need": "Make waiting feel like progress, not a freeze",
        "keywords": (
            "finding a captain", "spinner", "froze", "nearby cars",
            "trust the eta", "greyed out", "keep looking",
        ),
    },
    "pickup_accuracy": {
        "label": "Pickup accuracy",
        "need": "Let people place a precise, editable pin",
        "keywords": (
            "pin", "pickup", "nudge", "snapped", "society", "mall entrance",
            "behind the building", "saved places", "work keeps resetting",
        ),
    },
    "trip_changes": {
        "label": "Stops & changes",
        "need": "Edit the trip without losing the fare",
        "keywords": ("stop", "destination", "drop-off", "change", "edit", "pharmacy"),
    },
    "home_ia": {
        "label": "Home & wayfinding",
        "need": "Keep Ride one tap away inside the Super App",
        "keywords": (
            "food, pay", "where to", "too many choices", "promos take",
            "one tap", "ride card", "boxes sit",
        ),
    },
    "payment_friction": {
        "label": "Payment friction",
        "need": "Make money states obvious and reversible",
        "keywords": (
            "card", "wallet", "payment", "cash", "promo field", "charged",
            "pending", "deducted", "credit", "refund",
        ),
    },
    "in_trip_control": {
        "label": "In-trip control",
        "need": "Keep the captain, car, and actions visible in motion",
        "keywords": (
            "recentered", "plate", "camry", "arriving now", "call captain",
            "lost the car", "at night",
        ),
    },
    "safety_trust": {
        "label": "Safety & trust",
        "need": "Put safety actions on the happy path",
        "keywords": (
            "share", "safe", "women", "family", "report", "trusted",
            "permission", "toggle",
        ),
    },
    "cancellation_clarity": {
        "label": "Cancellation clarity",
        "need": "Show the free-cancel rule before people tap",
        "keywords": ("cancel", "free cancel", "cancel free", "fee warning"),
    },
    "language_rtl": {
        "label": "Language & RTL",
        "need": "Treat Arabic as a first-class layout, not a translation pass",
        "keywords": ("arabic", "english", "urdu", "language", "rtl", "keyboard"),
    },
}

SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}


@dataclass
class ThemeInsight:
    key: str
    label: str
    need: str
    count: int
    severity_score: float
    top_severity: str
    cities: list[str]
    screens: list[str]
    quotes: list[dict]
    opportunity: str


@dataclass
class CopyDeck:
    screen: str
    tone: str
    language: str
    variants: list[dict] = field(default_factory=list)
    rationale: str = ""
    constraints_used: list[str] = field(default_factory=list)


def _blob(row: dict) -> str:
    return f"{row.get('quote', '')} {row.get('screen', '')} {row.get('task', '')}".lower()


def _has_keyword(text: str, keyword: str) -> bool:
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def classify_row(row: dict) -> list[str]:
    text = _blob(row)
    hits = [key for key, meta in THEMES.items() if any(_has_keyword(text, k) for k in meta["keywords"])]
    return hits or ["home_ia"]


def analyze(rows: list[dict]) -> list[ThemeInsight]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        for key in classify_row(row):
            buckets[key].append(row)

    insights: list[ThemeInsight] = []
    for key, items in buckets.items():
        meta = THEMES[key]
        score = sum(SEVERITY_WEIGHT.get(str(i.get("severity", "low")).lower(), 1) for i in items)
        top = max(items, key=lambda r: SEVERITY_WEIGHT.get(str(r.get("severity", "low")).lower(), 1))
        cities = [c for c, _ in Counter(r["city"] for r in items).most_common()]
        screens = [s for s, _ in Counter(r["screen"] for r in items).most_common()]
        quotes = sorted(
            items,
            key=lambda r: SEVERITY_WEIGHT.get(str(r.get("severity", "low")).lower(), 1),
            reverse=True,
        )[:4]
        fail_n = sum(1 for r in items if str(r.get("success", "")).lower() == "fail")
        opportunity = (
            f"If we fix {meta['label'].lower()} on {screens[0]}, "
            f"{fail_n} of {len(items)} notes in this set should stop failing "
            f"— starting in {cities[0]}."
        )
        insights.append(
            ThemeInsight(
                key=key,
                label=meta["label"],
                need=meta["need"],
                count=len(items),
                severity_score=round(score / max(len(items), 1), 2),
                top_severity=str(top.get("severity", "medium")),
                cities=cities,
                screens=screens,
                quotes=quotes,
                opportunity=opportunity,
            )
        )

    return sorted(insights, key=lambda t: (t.severity_score, t.count), reverse=True)


def _city_hook(cities: list[str]) -> str:
    if "Jeddah" in cities:
        return "Jeddah"
    if "Karachi" in cities:
        return "Karachi"
    if "Dubai" in cities:
        return "Dubai"
    return cities[0] if cities else "your city"


COPY_BANK = {
    "fare_transparency": {
        "calm": [
            {
                "headline": "Your fare, before you book.",
                "helper": "This is the price you’ll pay, unless you change the trip.",
                "cta": "Book this fare",
                "empty": "Add a drop-off to see your fare.",
                "error": "We couldn’t lock this fare. Check your connection and try again.",
                "chip": "Fare locked",
            },
            {
                "headline": "No surprises on this ride.",
                "helper": "Tolls and waiting show up here — not at the end.",
                "cta": "Confirm fare",
                "empty": "Pick pickup and drop-off for a price.",
                "error": "This fare changed. Review the new total to continue.",
                "chip": "All-in fare",
            },
        ],
        "punchy": [
            {
                "headline": "This is the price.",
                "helper": "Book it now and that’s what you’ll pay.",
                "cta": "Book for {price}",
                "empty": "Where to? We’ll price it instantly.",
                "error": "Price refreshed. Take a look before you book.",
                "chip": "Price you see",
            },
        ],
        "reassuring": [
            {
                "headline": "We’ll show every dirham.",
                "helper": "If something extra applies, you’ll see it before you confirm.",
                "cta": "See full breakdown",
                "empty": "Set your trip to preview the fare.",
                "error": "We paused booking so you can review the new fare.",
                "chip": "Breakdown ready",
            },
        ],
    },
    "matching_anxiety": {
        "calm": [
            {
                "headline": "Looking nearby.",
                "helper": "Captains in your area can see this trip. We’ll update you as they respond.",
                "cta": "Keep waiting",
                "empty": "No captains yet. We’ll keep looking for 2 more minutes.",
                "error": "Still looking. You can cancel free until a captain accepts.",
                "chip": "12 captains nearby",
            },
        ],
        "punchy": [
            {
                "headline": "On it.",
                "helper": "A captain is deciding. Usually under a minute here.",
                "cta": "Stay with this trip",
                "empty": "Quiet right now. Try GO, or wait a little longer.",
                "error": "No accept yet. Cancel is still free.",
                "chip": "Free cancel · 1:20",
            },
        ],
        "reassuring": [
            {
                "headline": "You’re not stuck.",
                "helper": "The app is working. We’ll show cars as they come online.",
                "cta": "Share this wait",
                "empty": "Matching is taking longer than usual. You can still cancel free.",
                "error": "We lost the connection. Your trip is still live — tap to refresh.",
                "chip": "Still matching",
            },
        ],
    },
    "pickup_accuracy": {
        "calm": [
            {
                "headline": "Drag the pin. We’ll wait.",
                "helper": "Nudge it to your side of the street. The captain sees this exact spot.",
                "cta": "Set pickup here",
                "empty": "Move the map to drop your pin.",
                "error": "We couldn’t save this pin. Try once more.",
                "chip": "Pin looks precise",
            },
        ],
        "punchy": [
            {
                "headline": "Your side of the street.",
                "helper": "If the pin jumps, drag it back. You’re in control.",
                "cta": "Confirm pin",
                "empty": "Search a gate, or drop a pin.",
                "error": "That pin didn’t stick. Drag it again.",
                "chip": "Exact pickup",
            },
        ],
        "reassuring": [
            {
                "headline": "We’ll send the captain here.",
                "helper": "You can edit this anytime before they arrive — without restarting.",
                "cta": "Use this pickup",
                "empty": "Saved places live under Search.",
                "error": "Editing the pin kept your place in line.",
                "chip": "Matching continues",
            },
        ],
    },
    "safety_trust": {
        "calm": [
            {
                "headline": "Share this trip in one tap.",
                "helper": "Send live location to someone you trust. They’ll see the captain and the route.",
                "cta": "Share trip",
                "empty": "Add a trusted contact to share faster next time.",
                "error": "Sharing didn’t send. Try SMS, or copy the link.",
                "chip": "Women preferred · on",
            },
        ],
        "punchy": [
            {
                "headline": "One tap. They know you’re on the way.",
                "helper": "Plate, route, and ETA — sent to your person.",
                "cta": "Tell someone",
                "empty": "Pick a trusted contact once. We’ll remember.",
                "error": "Link copied. Send it any way you like.",
                "chip": "Shared now",
            },
        ],
        "reassuring": [
            {
                "headline": "You’re in control of this ride.",
                "helper": "Women preferred is on. Share trip is ready before a captain accepts.",
                "cta": "Review safety",
                "empty": "Safety tools stay on this screen, not behind a menu.",
                "error": "We couldn’t reach your contact. The trip is still being shared in the app.",
                "chip": "Safety on",
            },
        ],
    },
    "payment_friction": {
        "calm": [
            {
                "headline": "How you’ll pay.",
                "helper": "Cash, card, or Pay — pick it before you book. We’ll say if a charge fails.",
                "cta": "Use this method",
                "empty": "Add a card, or keep cash.",
                "error": "Card didn’t go through. You were not charged. Try cash or another card.",
                "chip": "Not charged",
            },
        ],
        "punchy": [
            {
                "headline": "Pay your way.",
                "helper": "Promo sits next to the method. Apply it before you book.",
                "cta": "Apply promo",
                "empty": "Got a code? Add it here.",
                "error": "Promo didn’t apply to this trip. The fare above is without it.",
                "chip": "Promo on fare",
            },
        ],
        "reassuring": [
            {
                "headline": "If money moves, you’ll see it.",
                "helper": "Pending means we haven’t taken it yet. Failed means nothing left your account.",
                "cta": "Check this payment",
                "empty": "No receipts yet.",
                "error": "This payment is pending. We’ll update this screen — no need to pay twice.",
                "chip": "Wallet · pending",
            },
        ],
    },
    "home_ia": {
        "calm": [
            {
                "headline": "Where to?",
                "helper": "Ride stays up top. Everything else is one swipe away.",
                "cta": "Book a ride",
                "empty": "Your last trip home is ready.",
                "error": "We couldn’t load Ride. Pull to refresh.",
                "chip": "Ride · 1 tap",
            },
        ],
        "punchy": [
            {
                "headline": "Need a ride? You got it.",
                "helper": "Food and Pay can wait. Your car is right here.",
                "cta": "Get a ride",
                "empty": "Heading home?",
                "error": "Ride is taking a second. Still with you.",
                "chip": "GO nearby",
            },
        ],
        "reassuring": [
            {
                "headline": "Your ride, first.",
                "helper": "Offers sit below. They never cover Where to.",
                "cta": "Set destination",
                "empty": "No recent places yet. Search a destination.",
                "error": "Home loaded without offers. You can still book.",
                "chip": "Where to",
            },
        ],
    },
    "cancellation_clarity": {
        "calm": [
            {
                "headline": "Free to cancel for 2:00.",
                "helper": "A fee applies only after a captain accepts and the timer ends.",
                "cta": "Keep this trip",
                "empty": "No active trip to cancel.",
                "error": "Fee applies if you cancel now. Wait, or confirm the fee.",
                "chip": "Free cancel · 1:42",
            },
        ],
        "punchy": [
            {
                "headline": "No fee yet.",
                "helper": "Clock is on the matching screen, not hidden in a sheet.",
                "cta": "Cancel free",
                "empty": "Nothing to cancel.",
                "error": "This cancel has a fee. See why before you confirm.",
                "chip": "Fee after accept",
            },
        ],
        "reassuring": [
            {
                "headline": "You’ll see the rule before you tap.",
                "helper": "We’d rather you wait 30 seconds than get a surprise fee.",
                "cta": "Show cancel rules",
                "empty": "Rules appear once matching starts.",
                "error": "This fee is because a captain is already on the way.",
                "chip": "Rule visible",
            },
        ],
    },
    "in_trip_control": {
        "calm": [
            {
                "headline": "Ahmed is 3 min away.",
                "helper": "White Camry · plate RAK 48291. We’ll keep the car centered.",
                "cta": "Call Ahmed",
                "empty": "Trip details appear once a captain accepts.",
                "error": "Map lost the car. Tap to recenter on your captain.",
                "chip": "Plate · RAK 48291",
            },
        ],
        "punchy": [
            {
                "headline": "Look for RAK 48291.",
                "helper": "Two similar cars? Trust the plate. It’s large for a reason.",
                "cta": "Call captain",
                "empty": "Waiting for a captain.",
                "error": "Can’t see the car? Recenter, or call.",
                "chip": "Your car",
            },
        ],
        "reassuring": [
            {
                "headline": "Your captain is on the map.",
                "helper": "Call and share stay on this screen. The map follows the car, not you.",
                "cta": "Share trip",
                "empty": "We’ll show the car as soon as someone accepts.",
                "error": "Live location paused. Sharing is still on.",
                "chip": "Car centered",
            },
        ],
    },
    "trip_changes": {
        "calm": [
            {
                "headline": "Add a stop before you book.",
                "helper": "Pharmacy, gate, or a second drop-off. The fare updates as you add it.",
                "cta": "Add stop",
                "empty": "No stops yet.",
                "error": "We updated the fare. Review it before this stop is added.",
                "chip": "Fare updated",
            },
        ],
        "punchy": [
            {
                "headline": "Change of plans? Add it.",
                "helper": "Edit drop-off. See the new fare. Then confirm.",
                "cta": "Update trip",
                "empty": "Your trip has one stop.",
                "error": "Fare preview is back. Nothing changes until you confirm.",
                "chip": "New fare",
            },
        ],
        "reassuring": [
            {
                "headline": "You won’t confirm blind.",
                "helper": "If the trip changes, the price stays on screen.",
                "cta": "Review new fare",
                "empty": "Add a stop whenever you need.",
                "error": "We kept your original trip. The change wasn’t saved.",
                "chip": "Still your trip",
            },
        ],
    },
    "language_rtl": {
        "calm": [
            {
                "headline": "العربية جاهزة هنا.",
                "helper": "Ride, fare, and actions flip with the language. Nothing stays leftover in English.",
                "cta": "استمر بالعربي",
                "empty": "ابحث عن وجهتك",
                "error": "تعذر تحميل اللغة. جرّب مرة ثانية.",
                "chip": "AR · RTL",
            },
        ],
        "punchy": [
            {
                "headline": "Your language. The whole screen.",
                "helper": "Arabic, English, or Urdu search — results should match the keyboard you used.",
                "cta": "Keep Arabic",
                "empty": "إلى أين؟",
                "error": "This screen is still catching up. Ride still works.",
                "chip": "Full Arabic",
            },
        ],
        "reassuring": [
            {
                "headline": "إلى أين؟",
                "helper": "الأرقام والأزرار تبقى في مكانها الصحيح. الأجرة على اليمين.",
                "cta": "احجز مشوارك",
                "empty": "لا توجد أماكن أخيرة بعد.",
                "error": "حرّكنا الشريحة لمكانها الصحيح.",
                "chip": "الأجرة هنا",
            },
        ],
    },
}

AR_OVERLAY = {
    "fare_transparency": {
        "headline": "أجرتك، قبل ما تحجز.",
        "helper": "هذا السعر اللي راح تدفعه، إلا إذا غيّرت المشوار.",
        "cta": "احجز بهذه الأجرة",
        "empty": "أضف وجهتك لتشوف الأجرة.",
        "error": "ما قدرنا نثبت الأجرة. حاول مرة ثانية.",
        "chip": "الأجرة ثابتة",
    },
    "matching_anxiety": {
        "headline": "ندور لك قريب.",
        "helper": "الكباتن في منطقتك يشوفون طلبك. بنحدّثك أول ما يرد أحد.",
        "cta": "خلني أنتظر",
        "empty": "ما في كابتن للحين. بنكمّل البحث دقيقتين.",
        "error": "للحين ندورت. تقدر تلغي بدون رسوم إلى أن يقبل كابتن.",
        "chip": "إلغاء مجاني",
    },
    "pickup_accuracy": {
        "headline": "حرّك الدبوس. إحنا معك.",
        "helper": "خلّه على طرف الشارع اللي أنت فيه. الكابتن يشوف نفس النقطة.",
        "cta": "أكّد نقطة الركوب",
        "empty": "حرّك الخريطة وحط الدبوس.",
        "error": "ما انحفظ الدبوس. حاول مرة ثانية.",
        "chip": "ركوب دقيق",
    },
    "safety_trust": {
        "headline": "شارك المشوار بضغطة.",
        "helper": "ارسل موقعك لشخص تثق فيه. بيشوف الكابتن والمسار.",
        "cta": "شارك المشوار",
        "empty": "أضف شخص تثق فيه عشان المشاركة تصير أسرع.",
        "error": "ما انرسلت المشاركة. جرّب رسالة أو انسخ الرابط.",
        "chip": "تفضيل النساء · تشغيل",
    },
    "home_ia": {
        "headline": "إلى أين؟",
        "helper": "المشوير فوق. باقي الخدمات بسحبة واحدة.",
        "cta": "احجز مشوار",
        "empty": "آخر مشوار للبيت جاهز.",
        "error": "ما فتح المشوير. اسحب للتحديث.",
        "chip": "مشوير · ضغطة",
    },
}


CONSTRAINTS = [
    "Less is more — headlines under 8 words",
    "Upbeat & everyday — contractions, no jargon",
    "Always dependable — no overpromise, name the state",
    "Never curt, never cocky",
    "City can flavor the line, not the whole message",
    "Arabic is a layout, not a leftover string",
]


def generate_copy(insight: ThemeInsight, tone: str, language: str) -> CopyDeck:
    tone_key = {"Careem default": "calm", "More punchy": "punchy", "More reassuring": "reassuring"}.get(tone, "calm")
    bank = COPY_BANK.get(insight.key, COPY_BANK["home_ia"])
    variants = [dict(v) for v in bank.get(tone_key, bank.get("calm", []))]
    city = _city_hook(insight.cities)

    for variant in variants:
        if city and "heading home" in variant["helper"].lower():
            variant["helper"] = f"Heading home, {city}? Your last trip is one tap."
        if "{price}" in variant["cta"]:
            variant["cta"] = variant["cta"].format(price="42 AED" if city == "Dubai" else "28 SAR")

    if language in ("Arabic", "Both") and insight.key in AR_OVERLAY:
        ar = dict(AR_OVERLAY[insight.key])
        if language == "Arabic":
            variants = [ar]
        else:
            variants = variants + [ar]

    quotes = "; ".join(f"“{q['quote']}”" for q in insight.quotes[:2])
    rationale = (
        f"Grounded in {insight.count} notes on {insight.label.lower()} "
        f"({', '.join(insight.cities[:3])}). {insight.need}. "
        f"Evidence: {quotes} "
        f"Tone follows Careem public TOV: short, certain, human — never a lecture."
    )
    return CopyDeck(
        screen=insight.screens[0] if insight.screens else "Ride",
        tone=tone,
        language=language,
        variants=variants,
        rationale=rationale,
        constraints_used=CONSTRAINTS,
    )


LAYOUTS = {
    "fare_transparency": [
        {
            "name": "Receipt-first booking",
            "hypothesis": "If the fare breakdown is visible before Book, surprise-at-confirm drops.",
            "structure": ["Map + route", "All-in fare card with Why this price", "Promo on the card", "Book this fare"],
            "test": "Task: book a GO ride and say the final price before tapping. Success = stated price matches confirm.",
            "tradeoff": "Adds a step on repeat trips. Soften with a compact chip for returning riders.",
        },
        {
            "name": "Range, then lock",
            "hypothesis": "A 42–48 range with a lock-on-book moment is more honest than a fake-precise 45.",
            "structure": ["Fare range chip on map", "Lock fare on Book", "In-trip chip stays", "Receipt mirrors the chip"],
            "test": "Compare trust scores: point price vs range. Watch cancel rate after Book.",
            "tradeoff": "Ranges can feel vague in price-sensitive cities. Show the Why.",
        },
        {
            "name": "No-surprises strip",
            "hypothesis": "A persistent fare strip across matching and in-trip beats a single confirm moment.",
            "structure": ["Sticky fare strip", "Tap to expand breakdown", "Change trip → strip updates", "Never hide on scroll"],
            "test": "In-trip destination change: can people find the new fare in under 5 seconds?",
            "tradeoff": "Strip competes with safety actions. Keep it to one line until opened.",
        },
    ],
    "matching_anxiety": [
        {
            "name": "Progressive matching",
            "hypothesis": "Named stages beat a spinner. People wait longer when they see work happening.",
            "structure": ["Looking nearby", "Captains can see your trip", "One is deciding", "Ahmed is on the way"],
            "test": "Wait 45s. Do people still think the app froze? Measure cancel-during-match.",
            "tradeoff": "Fake progress destroys trust. Only advance on real events.",
        },
        {
            "name": "Cars on the map first",
            "hypothesis": "Ghost cars (privacy-safe, non-identifying) prove supply exists.",
            "structure": ["Nearby cars immediately", "Free-cancel timer", "Captain card after accept", "Share trip enabled early"],
            "test": "Anxiety rating at 20s vs blank map. Do people still try to exit the app?",
            "tradeoff": "Supply can look thinner than it feels. Never invent cars.",
        },
        {
            "name": "Useful wait",
            "hypothesis": "The wait screen can finish jobs people do later: share trip, confirm pin, payment.",
            "structure": ["Status + timer", "Confirm pin", "Share trip (live)", "Payment check"],
            "test": "Does share-trip happen before accept? Does pin-edit restart matching? It must not.",
            "tradeoff": "Don’t turn wait into a form. One optional action at a time.",
        },
    ],
    "pickup_accuracy": [
        {
            "name": "Nudge mode",
            "hypothesis": "A dedicated nudge state stops the pin from snapping away from the rider.",
            "structure": ["Large pin", "Nudge ±10m controls", "Side of street label", "Set pickup here"],
            "test": "Mall entrance task: can they place the pin on their curb without search?",
            "tradeoff": "Extra control chrome. Hide it once the pin is confirmed.",
        },
        {
            "name": "Gate, not street",
            "hypothesis": "Societies and malls need gates as first-class places, not dropped pins.",
            "structure": ["Search → building → gate", "Saved Home/Work with gate", "Captain instruction line", "Keep matching on edit"],
            "test": "Lahore society task. Success = captain instruction includes the gate name.",
            "tradeoff": "Needs place data. Fall back to pin + note.",
        },
        {
            "name": "Edit without restart",
            "hypothesis": "Mid-wait pin edits should keep the match, not reset the queue.",
            "structure": ["Edit pickup", "Matching continues banner", "Captain notified", "Fare unchanged unless trip changes"],
            "test": "Edit pin at 20s. Does matching restart? It should not.",
            "tradeoff": "Large moves may need a rematch. Threshold it (e.g. >150m).",
        },
    ],
    "safety_trust": [
        {
            "name": "Safety on the happy path",
            "hypothesis": "If Share and Women preferred sit next to Book, they get used.",
            "structure": ["Women preferred toggle (visible)", "Share trip before accept", "Trusted contact", "Book"],
            "test": "First-time night ride. Can they share before a captain accepts, in under 10s?",
            "tradeoff": "Home-screen density. Keep Share as a persistent icon, not a paragraph.",
        },
        {
            "name": "In-car report",
            "hypothesis": "Reporting only after the trip is too late for safety-critical moments.",
            "structure": ["Quiet report in-trip", "Optional silent alert", "Trip continues", "Follow-up after drop-off"],
            "test": "Can someone start a report without the captain seeing the screen easily?",
            "tradeoff": "Misuse risk. Confirm, but don’t bury.",
        },
        {
            "name": "Plate-first night mode",
            "hypothesis": "At night, plate and color beat the photo.",
            "structure": ["Huge plate", "Car color + make", "Flash-friendly contrast", "Call"],
            "test": "Two similar cars. Identification time with large plate vs current card.",
            "tradeoff": "Less room for rating. Move rating to a second line.",
        },
    ],
    "payment_friction": [
        {
            "name": "Money states, named",
            "hypothesis": "Pending / failed / paid in plain language stops double-pay and tickets.",
            "structure": ["Method + promo on one row", "Named state", "You were not charged", "Try another way"],
            "test": "Failed card. Do people open their bank app? They shouldn’t need to.",
            "tradeoff": "Longer error copy. Worth it.",
        },
        {
            "name": "Promo before Book",
            "hypothesis": "Promo next to the fare, not after payment, fixes late-code failure.",
            "structure": ["Fare", "Add promo", "Method", "Book"],
            "test": "Apply a 20% code. Can they say what it applied to?",
            "tradeoff": "Promo abuse. Still validate, just earlier.",
        },
        {
            "name": "In-app money, always",
            "hypothesis": "Wallet top-up in a web view feels like leaving. Keep it in-app.",
            "structure": ["Add money sheet", "Amount chips", "Status timeline", "Back to Ride"],
            "test": "Top-up completion rate vs web view. Watch accidental closes.",
            "tradeoff": "Payment-provider constraints. If web is required, skin it and keep a sticky back.",
        },
    ],
    "cancellation_clarity": [
        {
            "name": "Timer on the match screen",
            "hypothesis": "If the free-cancel clock is visible while waiting, surprise fees disappear.",
            "structure": ["Matching status", "Free cancel · mm:ss", "Why a fee might start", "Keep this trip"],
            "test": "Ask riders when a fee starts. They should answer without opening a sheet.",
            "tradeoff": "A timer can pressure people. Pair it with You’re fine until… copy.",
        },
        {
            "name": "Fee only after accept",
            "hypothesis": "No fee language before a captain accepts. After accept, the rule is one line.",
            "structure": ["Pre-accept: Cancel free", "Accept moment: rule appears", "Confirm sheet with why", "Keep or cancel"],
            "test": "Cancel at 20s pre-accept vs 20s post-accept. Is the rule understood both times?",
            "tradeoff": "Two states to design. Worth it — they are different promises.",
        },
        {
            "name": "Wait-or-fee choice",
            "hypothesis": "A 30-second nudge beats a sudden charge when someone is about to cancel.",
            "structure": ["You’re 30 seconds from a fee", "Wait", "Cancel and pay", "See the rule"],
            "test": "Do people wait when shown the remaining free window? Measure fee tickets.",
            "tradeoff": "Must not feel like a dark pattern. Offer a clear cancel too.",
        },
    ],
    "home_ia": [
        {
            "name": "Ride is the product",
            "hypothesis": "A commute open should land on Where to, not a promo wall.",
            "structure": ["Where to + last trip chip", "Service rail (Food, Pay)", "Offers below the fold", "City greeting"],
            "test": "7am task: start a ride in one tap from cold open.",
            "tradeoff": "Discovery of new verticals drops. Use the rail, not the hero.",
        },
        {
            "name": "Commute mode",
            "hypothesis": "Morning hours can collapse the Super App to Ride + last destination.",
            "structure": ["Time-aware home", "Home/Work chips", "Quiet offers", "One primary CTA"],
            "test": "Compare time-to-book 7–9am vs current home.",
            "tradeoff": "Personalization can feel presumptuous. Keep an All services escape.",
        },
        {
            "name": "Language-complete cards",
            "hypothesis": "A language switch must flip every card, not the chrome only.",
            "structure": ["Language first", "Card audit checklist", "RTL fare chip", "No mixed strings"],
            "test": "Switch to Arabic. Count leftover English strings on Home + Ride.",
            "tradeoff": "Content ops cost. Ship a blocker list, not a hope.",
        },
    ],
}

DEFAULT_LAYOUTS = [
    {
        "name": "One job per screen",
        "hypothesis": "If this screen has one primary action, error and empty states get easier to write.",
        "structure": ["Context", "Primary action", "Secondary safety/payment", "Status"],
        "test": "5-second test: can a new rider say what this screen is for?",
        "tradeoff": "Power users may want density. Offer an advanced collapse, not a wall.",
    }
]


def generate_layouts(insight: ThemeInsight) -> list[dict]:
    layouts = LAYOUTS.get(insight.key, DEFAULT_LAYOUTS)
    city = ", ".join(insight.cities[:3])
    enriched = []
    for item in layouts:
        row = dict(item)
        row["grounding"] = (
            f"Based on {insight.count} notes ({insight.top_severity} peak) in {city}. "
            f"{insight.opportunity}"
        )
        enriched.append(row)
    return enriched


def build_llm_brief(insight: ThemeInsight, tone: str) -> str:
    quotes = "\n".join(f"- ({q['city']}, {q['screen']}, {q['severity']}) {q['quote']}" for q in insight.quotes)
    return f"""You are a product designer and UX writer embedded in Careem Ride.
Follow Careem's public tone of voice: less is more; upbeat and everyday; always dependable; driven but never cocky; no slang; no jargon (never say "user" or "purchase"); contractions are good; headlines under 10 words.

Job
Review the design notes below and return quick, usable improvements — not a critique essay.

Theme: {insight.label}
Job-to-be-done: {insight.need}
Tone slider: {tone}
Markets in the notes: {", ".join(insight.cities)}
Screens: {", ".join(insight.screens)}

Evidence
{quotes}

Return exactly this structure:
1. Diagnosis (3 bullets, each citing a quote)
2. Usability fixes (5 bullets). Each bullet: problem → change → why it helps a first-time rider in one of the named cities
3. UI copy deck in English AND Arabic: headline, helper, CTA, empty, error
4. 3 layout directions: name, 4-part structure, what to test, one tradeoff
5. What not to do (2 bullets) — brand or trust risks

Constraints
- Do not invent metrics or research Careem did not provide
- Do not recommend dark patterns (hidden fees, fake nearby cars, forced wait)
- Prefer one primary action per screen
- Arabic must include RTL placement notes, not only translation
- Keep the whole answer under 350 words"""
