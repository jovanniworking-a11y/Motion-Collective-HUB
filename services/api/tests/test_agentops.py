# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_9163a204b3ff4512]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Cross-machine leases and the stamp mirror (agentops)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.auth import SESSION_COOKIE, sign_session
from app.main import app

TOKEN = "t" * 40
SECRET = "s" * 40


def _stamp(sid: str, intent: str = "Rescore run 42") -> dict:
    return {
        "stamp_id": sid, "trace_id": f"tr_{sid}", "timestamp_utc": "2026-10-24T20:00:00.000Z",
        "agent": {"agent_id": "grok-jerry", "role": "backend"},
        "scope": {"surface_type": "code_file", "target_uri": "live-ops/counter/server.py"},
        "work_summary": {"intent": intent, "verification_status": "verified_passed"},
        "handoff_context": {"status": "completed", "next_agent_directives": ["bench test on 29 Oct"]},
    }


def test_leases_across_agents():
    with TestClient(app) as c:
        a = c.post("/api/agentops/leases/acquire", json={"resource": "live-ops/fader/server.py", "owner": "grok-jerry", "ttl": 60})
        assert a.status_code == 200
        lid = a.json()["lease"]["lease_id"]
        b = c.post("/api/agentops/leases/acquire", json={"resource": "live-ops/fader/server.py", "owner": "cursor", "ttl": 60})
        assert b.status_code == 409 and "grok-jerry" in b.json()["detail"]
        assert c.post("/api/agentops/leases/heartbeat", json={"resource": "live-ops/fader/server.py", "lease_id": lid}).status_code == 200
        assert any(l["owner"] == "grok-jerry" for l in c.get("/api/agentops/leases").json()["leases"])
        assert c.post("/api/agentops/leases/release", json={"resource": "live-ops/fader/server.py", "lease_id": lid}).json()["released"]
        assert c.post("/api/agentops/leases/acquire", json={"resource": "live-ops/fader/server.py", "owner": "cursor", "ttl": 60}).status_code == 200


def test_expired_lease_can_be_taken_over():
    with TestClient(app) as c:
        c.post("/api/agentops/leases/acquire", json={"resource": "x/expire.py", "owner": "agent-a", "ttl": 10})
        from app import agentops
        from app.platform_db import session_scope
        with session_scope() as s:
            row = s.get(agentops.AgentLease, "x/expire.py")
            row.expires_at = 0
        r = c.post("/api/agentops/leases/acquire", json={"resource": "x/expire.py", "owner": "agent-b", "ttl": 10})
        assert r.status_code == 200 and r.json()["lease"]["owner"] == "agent-b"


def test_stamp_mirror_is_idempotent_and_refuses_guest_data():
    with TestClient(app) as c:
        r = c.post("/api/agentops/stamps", json={"stamps": [_stamp("stp_a1"), _stamp("stp_a2")]})
        assert r.json() == {"added": 2, "skipped": 0}
        assert c.post("/api/agentops/stamps", json={"stamps": [_stamp("stp_a1")]}).json() == {"added": 0, "skipped": 1}
        bad = c.post("/api/agentops/stamps", json={"stamps": [_stamp("stp_a3", "Text the guest at 512-555-0199")]})
        assert bad.status_code == 400
        recent = c.get("/api/agentops/stamps").json()
        assert recent["stamps"][0]["intent"].startswith("Rescore")
        assert recent["source"] == "database" and recent["stamps"][0]["agent_id"] == "grok-jerry"


def test_machine_token_only_opens_agentops(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MOTION_SESSION_SECRET", SECRET)
    monkeypatch.setenv("MOTION_AGENT_TOKEN", TOKEN)
    with TestClient(app) as c:
        h = {"Authorization": f"Bearer {TOKEN}"}
        assert c.get("/api/agentops/leases", headers=h).status_code == 200
        assert c.get("/api/agentops/leases", headers={"Authorization": "Bearer wrong"}).status_code == 401
        assert c.get("/api/usage", headers=h).status_code == 401          # token is not a login
        c.cookies.set(SESSION_COOKIE, sign_session("jovanni", SECRET))
        assert c.get("/api/agentops/leases").status_code == 200           # people use the session


def test_stamp_mirror_honours_guest_denylist(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GUEST_DENYLIST", "Zelda Quintanilla,Ignatius Fernwood")
    with TestClient(app) as c:
        assert c.post("/api/agentops/stamps", json={"stamps": [_stamp("stp_d1", "Comp for zelda quintanilla")]}).status_code == 400
        assert c.post("/api/agentops/stamps", json={"stamps": [_stamp("stp_d2", "Comp list moved")]}).status_code == 200
