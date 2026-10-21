"""LAN bind rules. No token, no party-wide socket."""
from __future__ import annotations

import hmac
import os
from urllib.parse import unquote

TOKEN = os.environ.get("MOTION_TOKEN", "").strip()


def host() -> str:
    return "0.0.0.0" if TOKEN else "127.0.0.1"


def token_from(path: str) -> str:
    if "?" not in path:
        return ""
    for part in path.split("?", 1)[1].split("&"):
        if part.startswith("token="):
            return unquote(part[6:])
    return ""


def allowed(path: str) -> bool:
    if not TOKEN:
        return True
    got = token_from(path).encode()
    want = TOKEN.encode()
    if len(got) != len(want):
        return False
    return hmac.compare_digest(got, want)
