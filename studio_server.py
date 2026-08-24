"""Serve Careem Studio — brief, directions, pick, ask."""

from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from screen_gen import converse
from studio_brain import pick_direction, start_project

ROOT = Path(__file__).resolve().parent
STUDIO = ROOT / "studio"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STUDIO), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/studio":
            action = body.get("action") or "start"
            brief = body.get("brief") or {}
            dna = body.get("dna") or {}
            try:
                if action == "start":
                    self._json(200, start_project(brief, dna))
                elif action == "pick":
                    self._json(200, pick_direction(brief, body.get("direction") or "B", body.get("combine"), dna))
                elif action == "step":
                    step = str(body.get("step") or "Home")
                    product = brief.get("product") or "Careem"
                    goal = brief.get("goal") or ""
                    question = f"Design the {product} {step} screen. Journey context: {goal}"
                    self._json(200, converse(question, body.get("history") or [], dna))
                else:
                    self._json(400, {"error": "Unknown studio action."})
            except Exception as exc:
                self._json(500, {"error": str(exc)})
            return
        if self.path == "/api/ask":
            question = str(body.get("question") or body.get("prompt") or "").strip()
            if not question:
                self._json(400, {"error": "Ask needs a question."})
                return
            try:
                self._json(200, converse(question, body.get("history") or [], body.get("dna") or {}, body.get("screen")))
            except Exception as exc:
                self._json(500, {"error": str(exc)})
            return
        self.send_error(404)

    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            self._json(200, {"ok": True, "model": "studio-brain + gemini"})
            return
        super().do_GET()

    def _json(self, status: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt: str, *args) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8787), Handler)
    print("Careem Studio  http://localhost:8787")
    server.serve_forever()
