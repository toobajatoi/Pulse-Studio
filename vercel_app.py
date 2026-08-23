"""Vercel ASGI entrypoint for Pulse Studio APIs."""

from __future__ import annotations

import json

from screen_gen import converse
from studio_brain import pick_direction, start_project


async def _read_body(receive) -> dict:
    chunks = []
    more = True
    while more:
        message = await receive()
        chunks.append(message.get("body", b""))
        more = message.get("more_body", False)
    raw = b"".join(chunks) or b"{}"
    return json.loads(raw)


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
            await _send_json(send, 200, converse(question, body.get("history") or [], body.get("dna") or {}))
            return
        await _send_json(send, 404, {"error": "Not found."})
    except Exception as exc:
        await _send_json(send, 500, {"error": str(exc)})
