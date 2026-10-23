#!/usr/bin/env python3
"""MOTION Ops desktop launcher (Python entrypoint).

Prefers the Electron shell in this folder. Optional: MOTION_OPS_ENGINE=webview
uses pywebview against the same target resolution rules (no Electron required).

Usage (from repo root or desktop/):
  python desktop/launch.py
  MOTION_OPS_URL=http://localhost:3000 python desktop/launch.py
  MOTION_OPS_SMOKE=1 python desktop/launch.py
"""

from __future__ import annotations

import http.client
import http.server
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

DESKTOP = Path(__file__).resolve().parent
REPO = DESKTOP.parent
OPS = REPO / "ops"
PANEL = REPO / "apps" / "ops-panel"
FALLBACK = DESKTOP / "shell" / "fallback.html"
PANEL_URL = os.environ.get("MOTION_OPS_PANEL_URL", "http://localhost:3000")
SMOKE = os.environ.get("MOTION_OPS_SMOKE") == "1"
FORCE = (os.environ.get("MOTION_OPS_FALLBACK") or "").lower()
ENGINE = (os.environ.get("MOTION_OPS_ENGINE") or "electron").lower()


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A003
        return


def _reachable(url: str, timeout: float = 0.8) -> bool:
    try:
        parsed = urlparse(url)
        conn = http.client.HTTPConnection(
            parsed.hostname, parsed.port or 80, timeout=timeout
        )
        conn.request("GET", parsed.path or "/")
        res = conn.getresponse()
        res.read()
        conn.close()
        return res.status < 500
    except OSError:
        return False


def _serve(root: Path) -> str:
    os.chdir(root)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), QuietHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{port}/"


def resolve_target() -> tuple[str, str]:
    if os.environ.get("MOTION_OPS_URL"):
        return "url", os.environ["MOTION_OPS_URL"]
    if FORCE == "shell":
        return "shell", FALLBACK.as_uri()
    if FORCE in {"night-of", "ops"} and (OPS / "index.html").exists():
        return "night-of", _serve(OPS)
    panel_exists = (PANEL / "package.json").exists()
    if FORCE == "panel" or (not FORCE and panel_exists):
        if _reachable(PANEL_URL):
            return "panel", PANEL_URL
        if FORCE == "panel":
            return "panel-waiting", PANEL_URL
    if (OPS / "index.html").exists():
        return "night-of", _serve(OPS)
    return "shell", FALLBACK.as_uri()


def launch_electron() -> int:
    npm = shutil.which("npm")
    if not npm:
        print("npm not found; install Node.js or use MOTION_OPS_ENGINE=webview", file=sys.stderr)
        return 1
    node_modules = DESKTOP / "node_modules" / "electron"
    if not node_modules.exists():
        print("Installing desktop dependencies…")
        subprocess.check_call([npm, "install"], cwd=DESKTOP)
    env = os.environ.copy()
    cmd = [npm, "run", "smoke" if SMOKE else "desktop"]
    return subprocess.call(cmd, cwd=DESKTOP, env=env)


def launch_webview(url: str) -> int:
    try:
        import webview  # type: ignore
    except ImportError:
        print(
            "pywebview not installed. pip install pywebview  OR use Electron (default).",
            file=sys.stderr,
        )
        return 1
    if SMOKE:
        print(f"[MOTION Ops] webview smoke target={url}")
        return 0
    webview.create_window("MOTION Ops", url, width=1280, height=800, min_size=(960, 640))
    webview.start()
    return 0


def main() -> int:
    if ENGINE == "electron":
        return launch_electron()
    kind, url = resolve_target()
    print(f"[MOTION Ops] engine=webview target={kind} url={url}")
    return launch_webview(url)


if __name__ == "__main__":
    raise SystemExit(main())
