"""Login gate for the API — verifies the panel's signed session cookie.

The panel (Next) issues `motion_session` after password + TOTP. On Vercel the
rewrites send /api/* straight to this service, so it checks the cookie itself.
Format: base64url(JSON payload) + "." + base64url(HMAC-SHA256(secret, payload)).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

SESSION_COOKIE = "motion_session"
PUBLIC_PATHS = {"/health"}


def auth_mode(env: dict[str, str] | None = None) -> str:
    env = dict(os.environ) if env is None else env
    secret = env.get("MOTION_SESSION_SECRET", "")
    if len(secret) >= 32:
        return "on"
    if secret or env.get("VERCEL"):
        return "misconfigured"
    return "off"


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign_session(user: str, secret: str, now: float | None = None, ttl: int = 12 * 3600) -> str:
    iat = int(now if now is not None else time.time())
    body = base64.urlsafe_b64encode(
        json.dumps({"u": user, "iat": iat, "exp": iat + ttl, "v": 1}, separators=(",", ":")).encode()
    ).rstrip(b"=")
    sig = base64.urlsafe_b64encode(hmac.new(secret.encode(), body, hashlib.sha256).digest()).rstrip(b"=")
    return f"{body.decode()}.{sig.decode()}"


def verify_session(token: str | None, secret: str, now: float | None = None) -> dict[str, Any] | None:
    if not token or not secret:
        return None
    parts = token.split(".")
    if len(parts) != 2:
        return None
    body, sig = parts
    try:
        want = hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(want, _b64d(sig)):
            return None
        payload = json.loads(_b64d(body))
    except Exception:
        return None
    if payload.get("v") != 1 or not isinstance(payload.get("u"), str):
        return None
    if int(payload.get("exp", 0)) <= int(now if now is not None else time.time()):
        return None
    return payload


class SessionGate(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        mode = auth_mode()
        if mode == "off" or request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)
        if mode == "misconfigured":
            return JSONResponse({"ok": False, "error": "login not configured"}, status_code=503)
        if verify_session(request.cookies.get(SESSION_COOKIE), os.environ["MOTION_SESSION_SECRET"]) is None:
            return JSONResponse({"ok": False, "error": "login required"}, status_code=401)
        return await call_next(request)
