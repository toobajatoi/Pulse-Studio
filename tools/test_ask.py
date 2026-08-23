import requests

print("HOME", requests.get("http://127.0.0.1:8787/", timeout=5).status_code)
print("HEALTH", requests.get("http://127.0.0.1:8787/api/ask", timeout=5).json())
qs = [
    "Should I hide the cancel fee until after they tap?",
    "Do riders get a surprise cancellation charge?",
    "The fare jumped after they tapped Book",
    "Lock an all-in price before booking",
    "Spinner just says finding a captain",
    "Pin snapped to the mall across the street",
    "Share trip needs two taps",
    "Card failed with try again was I charged",
    "Arabic fare chip flipped to the wrong side",
    "Does this break in Arabic?",
    "Egypt large text cash market",
    "Food Pay and Boxes sit above Ride",
]
for q in qs:
    r = requests.post("http://127.0.0.1:8787/api/ask", json={"question": q}, timeout=10).json()
    print(r["topic"], r["confidence"], r["routed"], q)
    print(" ", r["answer"][:110])
    print(" ", r["evidence"][0]["source"], r["evidence"][0]["text"][:90])
