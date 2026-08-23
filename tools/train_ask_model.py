"""Train a local Ask Canvas model.

Public dataset:
  Uber ride reviews (Atharvak19) — used as retrieval evidence
  https://github.com/Atharvak19/Uber-Reviews-Sentimental-Analysis

Careem dummy notes + synthetic designer questions — used to train the topic router.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
UBER = ROOT / "data" / "uber_ride_reviews.csv"
NOTES = ROOT / "data" / "usability_feedback.csv"
OUT = ROOT / "models"
OUT.mkdir(exist_ok=True)

SCREEN_TOPIC = {
    "Fare estimate": "fare",
    "Receipt": "fare",
    "Captain matching": "wait",
    "Notifications": "wait",
    "Pickup pin": "pickup",
    "Drop-off": "pickup",
    "Search": "pickup",
    "Cancellation": "cancel_fee",
    "Safety": "safety",
    "In-trip": "safety",
    "Payment": "payment",
    "Wallet": "payment",
    "Home": "app",
    "Onboarding": "app",
    "Captain profile": "app",
}

UBER_KEYS = {
    "cancel_fee": ("cancel", "cancellation", "cancelled", "fee"),
    "fare": ("fare", "price", "charge", "charged", "expensive", "surge", "cost", "overcharge"),
    "wait": ("wait", "late", "eta", "minutes", "long time", "never came"),
    "pickup": ("pickup", "pick up", "location", "address", "wrong street", "pin"),
    "safety": ("safe", "safety", "stranded", "night", "dangerous", "scary"),
    "payment": ("payment", "card", "wallet", "cash", "refund", "credit", "charged twice"),
    "app": ("app", "freeze", "notification", "otp", "login", "crash"),
}

SYNTH = {
    "cancel_fee": [
        "Should I hide the cancel fee until after they tap?",
        "Where does the cancellation fee belong on this screen?",
        "Riders get charged when they cancel and they are angry",
        "Show the fee before cancel or after?",
        "Make cancel harder so we lose less money",
        "Free cancel window is not shown during matching",
        "Fee appears only on the confirm sheet",
        "Do not bury the cancellation charge",
        "Captain already accepted so there is a fee",
        "How do we show AED fee if they cancel now",
        "Cancellation surprise charges in reviews",
        "Keep Cancel visible and honest",
        "Is a cancel fee okay after the captain arrives?",
        "Warn about the fee on the matching screen",
        "Don't hide cancel behind three menus",
    ],
    "fare": [
        "The fare jumped after they tapped Book",
        "Lock the price before booking",
        "Map number is not the price they pay",
        "Surge said busy area with no reason",
        "Estimate was 28 but trip ended at 36",
        "Promo barely moved the fare",
        "Show an all-in fare chip",
        "GO vs Comfort vs Plus price difference",
        "Toll plus waiting on the receipt is confusing",
        "Riders screenshot fares because they don't trust us",
        "Keep the fare visible in trip",
        "Cash riders only saw the total after arrival",
        "Why is this ride more expensive",
        "Price changed after I booked",
        "Need a locked fare not an estimate",
    ],
    "wait": [
        "Spinner just says finding a captain",
        "After 40 seconds I thought the app froze",
        "Show nearby cars while matching",
        "ETA flipped from 8 min to 3 with no reason",
        "Captain arriving and delayed in the same minute",
        "Wait anxiety during matching",
        "Blank map while searching for a ride",
        "How long until a captain accepts",
        "Replace the spinner with named stages",
        "Rider cancelled after two minutes of waiting",
        "Progress copy beats a silent wait",
        "Matching feels broken",
        "Why is pickup taking so long",
        "Show cars on the map during search",
        "Don't leave riders on a spinner",
    ],
    "pickup": [
        "Pin snapped to the mall across the street",
        "I cannot nudge the pickup pin",
        "Editing the pin restarted matching",
        "Search found the street not my gate",
        "Wrong pickup location",
        "Captain is behind the building",
        "Work address keeps resetting",
        "Add a stop before confirming",
        "Changed drop-off and fare preview vanished",
        "Urdu search suggestions don't match the map",
        "Recents mixed food orders with ride drop-offs",
        "Let riders fix the pin without restarting",
        "Pickup is on the wrong side of the road",
        "Home is saved but work is not",
        "Pin accuracy at malls",
    ],
    "safety": [
        "Share trip needs two taps",
        "I wanted one tap to a trusted person",
        "Women preferred toggle is easy to miss",
        "Share live location asked contacts again",
        "Report is only after the trip ends",
        "Call captain is buried in a menu",
        "Plate is too small at night",
        "Two white Camrys arrived",
        "Feel safe on a night ride",
        "Family sharing should stay on the happy path",
        "Don't hide safety controls",
        "Share my trip with my brother before accept",
        "Captain photo and plate must stay large",
        "I almost got in the wrong car",
        "Safety complaints about being stranded",
    ],
    "payment": [
        "Card failed with try again was I charged",
        "Wallet deducted twice receipt said pending",
        "Cash vs card is buried under a chevron",
        "Promo field appears after payment method",
        "Add money jumped to a web view",
        "Refund said 2-5 days with no progress",
        "Name the money state pending failed paid",
        "You were not charged must be visible",
        "Payment recovery after a failed card",
        "Double charge on Careem Pay",
        "How do we show payment pending",
        "Rider does not know if money left the card",
        "Keep checkout context if payment fails",
        "Refund tracking is missing",
        "Cash still works but total was late",
    ],
    "app": [
        "Food Pay and Boxes sit above Ride",
        "I just want a car at 7am",
        "Promos take half the home screen",
        "Phone OTP took 90 seconds",
        "Location permission wiped my destination text",
        "Last destination chip is perfect",
        "Ride should stay one tap from open",
        "App freeze during matching",
        "Onboarding OTP timer is wrong",
        "Too many services on home",
        "Where to is below the fold",
        "Notification noise at 11pm",
        "First run permission timing",
        "Keep Ride as the primary action",
        "Don't make the home a promo wall",
    ],
    "locale": [
        "Arabic fare chip flipped to the wrong side",
        "I switched to Arabic and Ride stayed English",
        "Test Arabic expansion before we ship",
        "RTL layout for cancel sheet",
        "Numbers stayed Western in Arabic UI",
        "Egypt large text market",
        "Support Arabic and English on the same canvas",
        "Urdu keyboard vs English search",
        "Bilingual EN AR both mode",
        "Right to left Careem components",
        "Arabic title overflow on the primary button",
        "Cairo large text cash market",
        "Fare chip side in RTL",
        "Mixed language home screen",
        "Does this break in Arabic",
    ],
}

GOLD = [
    ("hide the cancel fee", "cancel_fee"),
    ("where should the cancellation fee show", "cancel_fee"),
    ("riders charged when they cancel", "cancel_fee"),
    ("fare jumped after book", "fare"),
    ("lock the price before booking", "fare"),
    ("why is surge so expensive", "fare"),
    ("spinner finding a captain", "wait"),
    ("app froze while matching", "wait"),
    ("wrong pickup pin", "pickup"),
    ("cannot move the pin", "pickup"),
    ("share trip with family", "safety"),
    ("women preferred toggle", "safety"),
    ("card failed was I charged", "payment"),
    ("wallet double charge", "payment"),
    ("arabic rtl fare chip", "locale"),
    ("egypt large text", "locale"),
    ("too many products on home", "app"),
    ("otp onboarding wait", "app"),
]


def uber_topic(text: str) -> str:
    t = text.lower()
    for topic, keys in UBER_KEYS.items():
        if any(k in t for k in keys):
            return topic
    return "other"


def note_topic(row: pd.Series) -> str:
    quote = str(row["quote"]).lower()
    if any(k in quote for k in ("arabic", "english", "urdu", "language")):
        return "locale"
    return SCREEN_TOPIC.get(row["screen"], "app")


def main() -> None:
    notes = pd.read_csv(NOTES)
    notes["text"] = notes["quote"].astype(str)
    notes["topic"] = notes.apply(note_topic, axis=1)
    notes["source"] = "careem_dummy"
    notes["ride_rating"] = notes["severity"].map({"critical": 1, "high": 2, "medium": 3, "low": 4}).fillna(3)

    synth = pd.DataFrame(
        [{"text": q, "topic": topic, "source": "synth_designer", "ride_rating": 3} for topic, qs in SYNTH.items() for q in qs]
    )

    train_df = pd.concat(
        [notes[["text", "topic", "source", "ride_rating"]], synth],
        ignore_index=True,
    )

    uber = pd.read_csv(UBER)
    uber["text"] = uber["ride_review"].astype(str)
    uber["topic"] = uber["text"].map(uber_topic)
    uber["source"] = "uber_public"
    corpus = pd.concat(
        [train_df, uber[["text", "topic", "source", "ride_rating"]]],
        ignore_index=True,
    )

    x_train, x_test, y_train, y_test = train_test_split(
        train_df["text"], train_df["topic"], test_size=0.25, random_state=7, stratify=train_df["topic"]
    )
    clf = Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=6000, ngram_range=(1, 2), min_df=1, stop_words="english")),
            ("lr", LogisticRegression(max_iter=500, class_weight="balanced")),
        ]
    )
    clf.fit(x_train, y_train)
    holdout = float(clf.score(x_test, y_test))
    clf.fit(train_df["text"], train_df["topic"])

    gold_x, gold_y = zip(*GOLD)
    gold_acc = float(clf.score(list(gold_x), list(gold_y)))
    report = classification_report(y_test, clf.predict(x_test), zero_division=0)

    vec = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), min_df=2, stop_words="english")
    matrix = vec.fit_transform(corpus["text"])
    nn = NearestNeighbors(n_neighbors=8, metric="cosine")
    nn.fit(matrix)

    joblib.dump(
        {
            "classifier": clf,
            "retriever_vec": vec,
            "retriever_nn": nn,
            "corpus": corpus[["text", "source", "topic", "ride_rating"]].to_dict("records"),
            "accuracy": gold_acc,
            "holdout": holdout,
            "dataset": "https://github.com/Atharvak19/Uber-Reviews-Sentimental-Analysis",
        },
        OUT / "ask_model.joblib",
    )
    (OUT / "metrics.json").write_text(
        json.dumps(
            {
                "gold_accuracy": round(gold_acc, 3),
                "holdout_accuracy": round(holdout, 3),
                "train_rows": int(len(train_df)),
                "corpus_rows": int(len(corpus)),
                "dataset": "https://github.com/Atharvak19/Uber-Reviews-Sentimental-Analysis",
            },
            indent=2,
        )
    )
    print(f"holdout={holdout:.3f} gold={gold_acc:.3f} train={len(train_df)} corpus={len(corpus)}")
    print(report)


if __name__ == "__main__":
    main()
