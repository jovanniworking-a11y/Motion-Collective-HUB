from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.auth import SESSION_COOKIE, auth_mode, sign_session, verify_session
from app.main import app
from app.platform_db import normalize_url

SECRET = "s" * 40


def test_auth_mode_fails_closed():
    assert auth_mode({}) == "off"
    assert auth_mode({"VERCEL": "1"}) == "misconfigured"
    assert auth_mode({"MOTION_SESSION_SECRET": "short"}) == "misconfigured"
    assert auth_mode({"MOTION_SESSION_SECRET": SECRET}) == "on"


def test_session_round_trip_and_tamper():
    t = sign_session("jovanni", SECRET, now=1_000_000)
    assert verify_session(t, SECRET, now=1_000_000)["u"] == "jovanni"
    assert verify_session(t, "x" * 40, now=1_000_000) is None
    body, sig = t.split(".")
    assert verify_session(body + "A." + sig, SECRET, now=1_000_000) is None
    assert verify_session(t, SECRET, now=1_000_000 + 13 * 3600) is None
    assert verify_session("junk", SECRET) is None


def test_gate_blocks_without_cookie(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MOTION_SESSION_SECRET", SECRET)
    with TestClient(app) as c:
        assert c.get("/health").status_code == 200
        for path in ("/api/agents", "/api/usage", "/api/data/health", "/api/studio/layout"):
            assert c.get(path).status_code == 401, path
        assert c.post("/api/agents/muse/chat", json={"prompt": "x"}).status_code == 401
        c.cookies.set(SESSION_COOKIE, sign_session("jovanni", SECRET))
        assert c.get("/api/agents").status_code == 200


def test_gate_misconfigured_on_vercel(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("MOTION_SESSION_SECRET", raising=False)
    monkeypatch.setenv("VERCEL", "1")
    with TestClient(app) as c:
        assert c.get("/api/agents").status_code == 503


def test_panel_and_api_tokens_match():
    """The panel signs in TypeScript; this is the exact same format (checked in vitest too)."""
    t = sign_session("a", SECRET, now=0, ttl=10)
    assert t.count(".") == 1 and "=" not in t


def test_normalize_postgres_urls():
    assert normalize_url("postgres://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_url("postgresql://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_url("postgresql+psycopg://u:p@h/db") == "postgresql+psycopg://u:p@h/db"
    assert normalize_url("sqlite:///x.db") == "sqlite:///x.db"
