"""Vercel ASGI entrypoint for Pulse Studio APIs."""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path

from screen_gen import converse
from studio_brain import pick_direction, start_project

ROOT = Path(__file__).resolve().parent
STATIC_DIRS = [ROOT / "public", ROOT / "studio"]
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".txt": "text/plain; charset=utf-8",
}


async def _read_body(receive) -> dict:
    chunks = []
    more = True
    while more:
        message = await receive()
        chunks.append(message.get("body", b""))
        more = message.get("more_body", False)
    raw = b"".join(chunks) or b"{}"
    return json.loads(raw)


def _static_file(url_path: str) -> Path | None:
    name = url_path.lstrip("/") or "index.html"
    if name.endswith("/"):
        name += "index.html"
    for folder in STATIC_DIRS:
        if not folder.exists():
            continue
        target = (folder / name).resolve()
        if folder.resolve() not in target.parents and target != folder.resolve():
            continue
        if target.is_file():
            return target
        index = folder / "index.html"
        if name == "index.html" and index.is_file():
            return index
    return None


async def _send_bytes(send, status: int, body: bytes, content_type: str) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", content_type.encode()],
                [b"access-control-allow-origin", b"*"],
                [b"cache-control", b"no-store"],
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def _send_json(send, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"access-control-allow-origin", b"*"],
                [b"access-control-allow-methods", b"GET, POST, OPTIONS"],
                [b"access-control-allow-headers", b"content-type"],
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def app(scope, receive, send):
    if scope["type"] != "http":
        return
    path = scope.get("path") or ""
    method = scope.get("method") or "GET"
    if method == "OPTIONS":
        await _send_json(send, 200, {"ok": True})
        return
    if path.startswith("/api/") and method == "GET":
        await _send_json(send, 200, {"ok": True, "model": "studio-brain + gemini"})
        return
    try:
        if path == "/api/studio" and method == "POST":
            body = await _read_body(receive)
            action = body.get("action") or "start"
            brief = body.get("brief") or {}
            dna = body.get("dna") or {}
            if action == "start":
                await _send_json(send, 200, start_project(brief, dna))
            elif action == "pick":
                await _send_json(send, 200, pick_direction(brief, body.get("direction") or "B", body.get("combine"), dna))
            else:
                await _send_json(send, 400, {"error": "Unknown studio action."})
            return
        if path == "/api/ask" and method == "POST":
            body = await _read_body(receive)
            question = str(body.get("question") or body.get("prompt") or "").strip()
            if not question:
                await _send_json(send, 400, {"error": "Ask needs a question."})
                return
            await _send_json(send, 200, converse(question, body.get("history") or [], body.get("dna") or {}, body.get("screen")))
            return
        static = _static_file(path)
        if static and method == "GET":
            content_type = MIME.get(static.suffix.lower()) or mimetypes.guess_type(static.name)[0] or "application/octet-stream"
            await _send_bytes(send, 200, static.read_bytes(), content_type)
            return
        await _send_json(send, 404, {"error": "Not found."})
    except Exception as exc:
        await _send_json(send, 500, {"error": str(exc)})
