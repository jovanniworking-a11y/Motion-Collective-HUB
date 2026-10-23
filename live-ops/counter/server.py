#!/usr/bin/env python3
"""MOTION door counter. LAN only. $0 stack.

    python server.py --test-video synthetic     # no camera
    python server.py --rtsp rtsp://user:pass@cam/live

WebSocket :8766 pushes {occupancy, ins, outs, peak, health, cap, space_left}.
HTTP :8765 serves ../dashboard/index.html.

YOLO+ByteTrack is optional (ultralytics, free). If it is not installed, RTSP
mode refuses to pretend and exits. Mock mode never needs it.

Stream loss: health.camera goes red, last count is kept, the process stays up.
Supported picture: an RTSP url, or a local webcam (--camera 0).
Not supported: a Wyze account or docker-wyze-bridge.
The overview camera is a different device. It never connects to this process.
CHECK IN counts only while the camera tile is red, so a live camera and a
door tap cannot count the same person twice.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

import websockets

from lan import allowed, host
from synthetic import script
from tripwire import TripWire

CAP = 70
HTTP_PORT = 8765
WS_PORT = 8766
ROOT = Path(__file__).resolve().parent
DASH = ROOT.parent / "dashboard" / "index.html"
STALE_SEC = 2.0


class Counter:
    def __init__(self, line_x: float = 320.0):
        self.wire = TripWire(line_x)
        self.camera = "green"
        self.fps = 0.0
        self.last_frame = time.monotonic()
        self._frames = 0
        self._fps_t = time.monotonic()
        self.manual_ins = 0

    def observe(self, tracks: list[tuple[int, float]]) -> None:
        self.wire.update(tracks)
        now = time.monotonic()
        self._frames += 1
        self.last_frame = now
        dt = now - self._fps_t
        if dt >= 1.0:
            self.fps = round(self._frames / dt, 1)
            self._frames = 0
            self._fps_t = now
        self.camera = "green"

    def mark_stale(self) -> None:
        if time.monotonic() - self.last_frame > STALE_SEC:
            self.camera = "red"

    def check_in(self) -> bool:
        """One door tap. Only when the camera is already red, and not past cap."""
        self.mark_stale()
        now = time.monotonic()
        if now - getattr(self, "_last_check", 0) < 1.0:
            return False
        if self.camera != "red":
            return False
        if self.wire.occupancy >= CAP:
            return False
        self._last_check = now
        self.manual_ins += 1
        self.wire.ins += 1
        self.wire.occupancy += 1
        self.wire.peak = max(self.wire.peak, self.wire.occupancy)
        return True

    def payload(self) -> dict:
        self.mark_stale()
        snap = self.wire.snapshot()
        space = max(0, CAP - snap["occupancy"])
        return {
            "occupancy": snap["occupancy"],
            "ins": snap["ins"],
            "outs": snap["outs"],
            "peak": snap["peak"],
            "cap": CAP,
            "space_left": space,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "health": {
                "camera": self.camera,
                "counter_fps": self.fps,
                "djm": "unknown",
                "projector": "unknown",
                "recorder": "unknown",
            },
        }


CLIENTS: set = set()
STATE = Counter()


async def broadcast() -> None:
    if not CLIENTS:
        return
    msg = json.dumps(STATE.payload())
    dead = []
    for ws in list(CLIENTS):
        try:
            await ws.send(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        CLIENTS.discard(ws)


async def ws_handler(ws):
    path = getattr(getattr(ws, "request", None), "path", "") or ""
    if not allowed(path):
        await ws.close(code=1008)
        return
    CLIENTS.add(ws)
    try:
        await ws.send(json.dumps(STATE.payload()))
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(msg, dict) and msg.get("action") == "checkin":
                STATE.check_in()
                await broadcast()
    finally:
        CLIENTS.discard(ws)


def _http_app():
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            from lan import TOKEN, allowed
            if TOKEN and not allowed(self.path):
                self.send_response(401)
                self.end_headers()
                return
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                body = DASH.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_response(404)
            self.end_headers()

        def log_message(self, fmt, *args):
            return

    return ThreadingHTTPServer((host(), HTTP_PORT), Handler)


async def pump_synthetic() -> None:
    frames = script()
    while True:
        for tracks in frames:
            if tracks:
                STATE.observe(tracks)
            else:
                await asyncio.sleep(STALE_SEC + 0.2)
                STATE.mark_stale()
            await broadcast()
            await asyncio.sleep(0.15)


async def pump_rtsp(url):
    try:
        import cv2
        from ultralytics import YOLO
    except ImportError:
        print("Live video needs opencv-python and ultralytics (both free). They are not installed.", file=sys.stderr)
        print("Until the 29 Oct test: python server.py --test-video synthetic", file=sys.stderr)
        raise SystemExit(2)
    model = YOLO("yolov8s.pt")
    cap = cv2.VideoCapture(url)
    fails = 0
    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            fails += 1
            STATE.camera = "red"
            STATE.mark_stale()
            await broadcast()
            await asyncio.sleep(0.5)
            if fails % 10 == 0:
                cap.release()
                cap = cv2.VideoCapture(url)
            continue
        fails = 0
        h, w = frame.shape[:2]
        STATE.wire.line_x = w / 2
        result = model.track(frame, persist=True, tracker="bytetrack.yaml", classes=[0], verbose=False)
        tracks = []
        boxes = result[0].boxes
        if boxes is not None and boxes.id is not None:
            ids = boxes.id.int().tolist()
            xyxy = boxes.xyxy.tolist()
            for tid, (x1, y1, x2, y2) in zip(ids, xyxy):
                tracks.append((int(tid), (x1 + x2) / 2))
        STATE.observe(tracks)
        await broadcast()
        await asyncio.sleep(0)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-video", choices=["synthetic"], help="No camera. Scripted ins/outs.")
    ap.add_argument("--rtsp", default="", help="rtsp://user:pass@ip:554/stream")
    ap.add_argument("--camera", type=int, default=-1, help="Local webcam index. Not the overview camera.")
    args = ap.parse_args()
    if not args.test_video and not args.rtsp and args.camera < 0:
        ap.error("pass --test-video synthetic, --rtsp URL, or --camera 0")
    if not DASH.exists():
        raise SystemExit(f"dashboard missing: {DASH}")

    http = _http_app()
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, http.serve_forever)

    async with websockets.serve(ws_handler, host(), WS_PORT, max_size=4096):
        print(f"dashboard http://{host()}:{HTTP_PORT}  ws :{WS_PORT}  cap {CAP}  token={'set' if host()=='0.0.0.0' else 'off, localhost only'}")
        if args.test_video:
            await pump_synthetic()
        elif args.camera >= 0:
            await pump_rtsp(args.camera)
        else:
            await pump_rtsp(args.rtsp)


if __name__ == "__main__":
    asyncio.run(main())
