from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.usage import init_usage_db


@pytest.fixture(scope="module")
def client():
    init_usage_db()
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    assert client.get("/health").json()["ok"] is True


def test_agents_registry(client: TestClient):
    agents = client.get("/api/agents").json()["agents"]
    assert len(agents) >= 3
    assert {"muse", "night-of", "orch"}.issubset({a["id"] for a in agents})


def test_chat_and_usage(client: TestClient):
    r = client.post("/api/agents/muse/chat", json={"prompt": "baths?", "action": "prompt"})
    assert r.status_code == 200
    usage = client.get("/api/usage").json()
    assert usage["totals"]["calls"] >= 1


def test_activity_board(client: TestClient):
    data = client.get("/api/activity").json()
    assert data["board_count"] >= 1


def test_routing(client: TestClient):
    assert len(client.get("/api/routing").json()["routes"]) >= 3


def test_layout_strips_address(client: TestClient):
    layout = client.get("/api/studio/layout").json()["layout"]
    layout["address"] = "NO"
    out = client.put("/api/studio/layout", json={"layout": layout}).json()["layout"]
    assert "address" not in out


def test_sim_stub(client: TestClient):
    job_id = client.post("/api/sims/run", json={"kind": "smoke-stub"}).json()["job"]["id"]
    status = "queued"
    for _ in range(40):
        status = client.get(f"/api/sims/jobs/{job_id}").json()["job"]["status"]
        if status in {"completed", "failed"}:
            break
        time.sleep(0.05)
    assert status == "completed"


def test_data_platform_ingest_and_compare(client: TestClient):
    assert client.get("/api/data/health").json()["ok"] is True
    run = client.post("/api/data/sims/run", json={"kind": "smoke-stub", "params": {"guests": 50}})
    assert run.status_code == 200
    assert "sim_run" in run.json()
    obs = client.post(
        "/api/data/observations",
        json={
            "crew_count": 42,
            "density_est": 0.55,
            "zone": "dance",
            "image_path": "/tmp/fake_frame.jpg",
            "meta": {"address": "MUST_STRIP", "sensor": "stub"},
            "label": "estimate",
        },
    )
    assert obs.status_code == 200
    body = obs.json()["observation"]
    assert body["image_path_hash"]
    assert "address" not in (body.get("meta") or {})
    assert body["note"] == "no faces/PII stored"
    drink = client.post("/api/data/drinks", json={"station": "island", "drink_type": "paloma", "quantity": 1})
    assert drink.status_code == 200
    flow = client.post("/api/data/flow", json={"zone": "dance", "count": 12})
    assert flow.status_code == 200
    cmp_ = client.get("/api/data/compare").json()
    assert cmp_["metrics"]["label"] == "estimate"
    assert cmp_["metrics"]["obs_mean_crew_count"] == 42
    assert "face" not in str(cmp_).lower() or "no face" in str(cmp_).lower()
