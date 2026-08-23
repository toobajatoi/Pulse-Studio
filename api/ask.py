from http.server import BaseHTTPRequestHandler

try:
    from _util import read_json, send_json
except ImportError:
    from api._util import read_json, send_json
from screen_gen import converse


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        send_json(self, 200, {"ok": True})

    def do_GET(self):
        send_json(self, 200, {"ok": True, "model": "studio-brain + gemini"})

    def do_POST(self):
        body = read_json(self)
        question = str(body.get("question") or body.get("prompt") or "").strip()
        if not question:
            send_json(self, 400, {"error": "Ask needs a question."})
            return
        try:
            send_json(self, 200, converse(question, body.get("history") or [], body.get("dna") or {}))
        except Exception as exc:
            send_json(self, 500, {"error": str(exc)})

    def log_message(self, fmt, *args):
        return
