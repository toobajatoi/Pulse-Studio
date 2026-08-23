from http.server import BaseHTTPRequestHandler

try:
    from _util import read_json, send_json
except ImportError:
    from api._util import read_json, send_json
from studio_brain import pick_direction, start_project


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        send_json(self, 200, {"ok": True})

    def do_GET(self):
        send_json(self, 200, {"ok": True, "model": "studio-brain + gemini"})

    def do_POST(self):
        body = read_json(self)
        action = body.get("action") or "start"
        brief = body.get("brief") or {}
        dna = body.get("dna") or {}
        try:
            if action == "start":
                send_json(self, 200, start_project(brief, dna))
            elif action == "pick":
                send_json(self, 200, pick_direction(brief, body.get("direction") or "B", body.get("combine"), dna))
            else:
                send_json(self, 400, {"error": "Unknown studio action."})
        except Exception as exc:
            send_json(self, 500, {"error": str(exc)})

    def log_message(self, fmt, *args):
        return
