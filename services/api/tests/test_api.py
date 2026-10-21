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
    body = run.json()
    assert body["sim_run"]["status"] == "completed"
    assert body["sim_run"]["params"]["guests"] == 50
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


def _occ(ts, zone, count, **extra):
    body = {
        "captured_at": ts,
        "zone": zone,
        "count": count,
        "confidence": 0.8,
        "count_quality": "ok",
        "camera_id": "wyze_living" if zone in {"living", "dance"} else "action_2",
        "sample_kind": "primary",
        "label": "estimate",
    }
    body.update(extra)
    return body


def _frame(client, ts, living, dance, kitchen=5, hallway=3, balcony=2):
    samples = [
        _occ(ts, "living", living),
        _occ(ts, "dance", dance),
        _occ(ts, "kitchen", kitchen, camera_id="action_2"),
        _occ(ts, "hallway", hallway, camera_id="action_2"),
        _occ(ts, "balcony", balcony, camera_id="action_2"),
    ]
    res = client.post("/api/data/occupancy/batch", json={"samples": samples})
    assert res.status_code == 200
    return res.json()["samples"]


def test_occupancy_rejects_image_and_address(client: TestClient):
    bad = _occ(1_700_000_000, "dance", 3)
    bad["image"] = "aaaa"
    assert client.post("/api/data/occupancy", json=bad).status_code == 422
    bad = _occ(1_700_000_000, "dance", 3)
    bad["address"] = "nope"
    assert client.post("/api/data/occupancy", json=bad).status_code == 422


def test_occupancy_count_drops_boxes_and_keeps_dance_inside_living(client: TestClient):
    res = client.post(
        "/api/data/occupancy/count",
        json={
            "captured_at": 1_700_000_100,
            "camera_id": "wyze_living",
            "detections": [{"conf": 0.91, "x1": 0.30, "y1": 0.40, "x2": 0.40, "y2": 0.60}],
        },
    )
    assert res.status_code == 200
    text = res.text
    assert "x1" not in text
    by_zone = {s["zone"]: s for s in res.json()["samples"]}
    assert by_zone["dance"]["count"] == 1
    assert by_zone["living"]["count"] == 1
    board = client.get("/api/data/occupancy/board").json()
    assert board["house_total"] == 1
    assert board["sim_dance_peak"] == 30.42


def test_occupancy_scorecard_prove_break_and_cap_gap(client: TestClient):
    _frame(client, 1_700_000_200, living=40, dance=30)
    prove = client.get("/api/data/occupancy/scorecard").json()
    assert prove["verdict"] == "prove"
    assert prove["sim_guests"] == 50
    _frame(client, 1_700_000_300, living=40, dance=50)
    broken = client.get("/api/data/occupancy/scorecard").json()
    assert broken["verdict"] == "break"
    _frame(client, 1_700_010_000, living=60, dance=40, kitchen=5, hallway=3, balcony=2)
    # Later, higher house mean makes the 70-cap window the busiest one.
    gap = client.get("/api/data/occupancy/scorecard").json()
    assert gap["verdict"] == "inconclusive_headcount"


def test_occupancy_spot_check_confirms_count(client: TestClient):
    saved = client.post(
        "/api/data/occupancy",
        json=_occ(1_700_000_400, "hallway", 6, count_quality="low", camera_id="action_2"),
    ).json()["sample"]
    assert saved["needs_spot"] is True
    checked = client.post(f"/api/data/occupancy/{saved['id']}/spot", json={"count": 4})
    assert checked.status_code == 200
    body = checked.json()["sample"]
    assert body["count"] == 4
    assert body["label"] == "confirmed"
    assert body["needs_spot"] is False
    assert "image" not in body
