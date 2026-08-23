import json
import requests

q = "Make me a screen for Home dashboard for careem riders that should have analytics of their montly earnings"
r = requests.post("http://127.0.0.1:8787/api/ask", json={"question": q}, timeout=15)
print(r.status_code)
data = r.json()
print(data["intent"], data["reply"][:80])
print(data["screen"]["kind"], data["screen"]["month"], data["screen"]["earned"])
print("HOME", requests.get("http://127.0.0.1:8787/", timeout=5).status_code)
print("google sans", "Google Sans" in requests.get("http://127.0.0.1:8787/").text)
