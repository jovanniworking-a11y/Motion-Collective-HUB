#!/usr/bin/env python3
"""Booth master fader. iPad on the same LAN. No paid APIs.

    python server.py --test-tone

Signal path (real night):
    DJM REC OUT (analog) -> booth PC line-in -> this gain + tanh limiter
    -> PC line-out -> PA

PHYSICAL BYPASS — part of the deliverable, not a note in the margin:
    If the laptop dies, the PA goes silent because the laptop is in the path.
    Restore in about 30 seconds: pull the laptop, patch DJM Booth Out straight
    to the PA input that the laptop line-out was feeding. Gain lives on the
    DJM again. Label both ends of that cable before doors.
    Crew test on 29 Oct: pull the laptop power once and time the repatch.

--test-tone does not open a soundcard. It runs a hot sine through the limiter
and serves the fader page so the iPad UI can be checked on a table.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import websockets

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "counter"))
from lan import allowed, host
from dsp import process

HTTP_PORT = 8775
WS_PORT = 8767
PAGE = Path(__file__).resolve().parent / "index.html"

GAIN = 0.7
MUTE = False
LIMITING = False


def _http():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            from lan import TOKEN, allowed
            if TOKEN and not allowed(self.path):
                self.send_response(401)
                self.end_headers()
                return
            body = PAGE.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return

    return ThreadingHTTPServer((host(), HTTP_PORT), Handler)


CLIENTS: set = set()


async def push():
    msg = json.dumps({"gain": GAIN, "mute": MUTE, "limiter": LIMITING})
    for ws in list(CLIENTS):
        try:
            await ws.send(msg)
        except Exception:
            CLIENTS.discard(ws)


def apply_control(msg, gain, mute):
    if not isinstance(msg, dict):
        return gain, mute
    if "gain" in msg:
        try:
            nxt = float(msg["gain"])
        except (TypeError, ValueError):
            nxt = None
        if nxt is not None and nxt == nxt and nxt not in (float("inf"), float("-inf")):
            gain = max(0.0, min(1.0, nxt))
    if msg.get("mute") is True or msg.get("mute") is False:
        mute = msg["mute"]
    return gain, mute


async def ws_handler(ws):
    global GAIN, MUTE
    path = getattr(getattr(ws, "request", None), "path", "") or ""
    if not allowed(path):
        await ws.close(code=1008)
        return
    CLIENTS.add(ws)
    try:
        await push()
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            GAIN, MUTE = apply_control(msg, GAIN, MUTE)
            await push()
    finally:
        CLIENTS.discard(ws)


async def tone_loop():
    global LIMITING
    sr = 48000
    n = 1024
    t = 0
    while True:
        phase = 2 * np.pi * 80 * (np.arange(n) + t) / sr
        block = (0.95 * np.sin(phase)).astype(np.float32)
        _out, LIMITING = process(block, GAIN, MUTE)
        t += n
        await push()
        await asyncio.sleep(n / sr)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-tone", action="store_true")
    args = ap.parse_args()
    if not args.test_tone:
        ap.error("soundcard path is not wired — use --test-tone until the 29 Oct DJM test")
    http = _http()
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, http.serve_forever)
    async with websockets.serve(ws_handler, host(), WS_PORT, max_size=4096):
        print(f"fader http://{host()}:{HTTP_PORT}  ws :{WS_PORT}")
        await tone_loop()


if __name__ == "__main__":
    asyncio.run(main())
