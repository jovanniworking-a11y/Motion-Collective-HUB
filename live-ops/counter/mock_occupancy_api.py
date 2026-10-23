#!/usr/bin/env python3
"""Stand-in for POST /api/data/occupancy, for testing occupancy_bridge.py. Not the real API.

Stdlib only. Accepts JSON, answers 201 {"ok": true, "received": <payload>} and can append
each accepted payload to a JSONL log. Failure knobs: --status (force a code), --fail-rate
(random 503s), --delay (seconds before answering).

    python mock_occupancy_api.py --port 3000 [--fail-rate 0.3] [--delay 5] [--status 422]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional

PATH = "/api/data/occupancy"


def serve(host: str = "127.0.0.1", port: int = 3000, *, quiet: bool = False,
          log_path: Optional[str] = None, status: Optional[int] = None,
          fail_rate: float = 0.0, delay: float = 0.0,
          rng: Optional[random.Random] = None) -> ThreadingHTTPServer:
    """Build (not start) the server. Call .serve_forever() on it, e.g. in a thread."""
    rng = rng or random.Random()
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # noqa: N802 - stdlib name
            if not quiet:
                sys.stderr.write("[mock] " + fmt % args + "\n")

        def _reply(self, code: int, body: dict) -> None:
            raw = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):  # noqa: N802 - stdlib name
            if self.path.split("?", 1)[0] != PATH:
                self._reply(404, {"ok": False, "error": "not found"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            if delay:
                time.sleep(delay)
            if status is not None:
                self._reply(status, {"ok": False, "error": f"forced {status}"})
                return
            with lock:
                flaky = fail_rate > 0 and rng.random() < fail_rate
            if flaky:
                self._reply(503, {"ok": False, "error": "flaky 503"})
                return
            try:
                payload = json.loads(raw or b"null")
            except ValueError:
                self._reply(400, {"ok": False, "error": "invalid json"})
                return
            if log_path:
                with lock, open(log_path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(payload) + "\n")
            self._reply(201, {"ok": True, "received": payload})

    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    return srv


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Mock POST /api/data/occupancy for bridge tests")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=3000)
    p.add_argument("--status", type=int, help="always answer with this HTTP status")
    p.add_argument("--fail-rate", type=float, default=0.0, help="share of requests answered 503")
    p.add_argument("--delay", type=float, default=0.0, help="seconds to wait before answering")
    p.add_argument("--log", help="append accepted payloads to this JSONL file")
    a = p.parse_args(argv)
    srv = serve(a.host, a.port, log_path=a.log, status=a.status, fail_rate=a.fail_rate, delay=a.delay)
    print(f"mock listening on http://{a.host}:{a.port}{PATH}", file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
