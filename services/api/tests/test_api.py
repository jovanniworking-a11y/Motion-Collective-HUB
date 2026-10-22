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


def test_observations_survive_missing_column(client: TestClient):
    """A live table missing an ORM column used to 500. Align adds it."""
    from sqlalchemy import inspect, text

    from app.platform_db import get_engine

    seeded = client.post(
        "/api/data/observations",
        json={"crew_count": 3, "zone": "hallway", "label": "estimate"},
    )
    assert seeded.status_code == 200
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE imaging_observations DROP COLUMN note"))
    cols = {c["name"] for c in inspect(engine).get_columns("imaging_observations")}
    assert "note" not in cols

    listed = client.get("/api/data/observations")
    assert listed.status_code == 200, listed.text
    rows = listed.json()["observations"]
    assert rows
    assert all(row["note"] == "no faces/PII stored" for row in rows)

    again = client.post(
        "/api/data/observations",
        json={"crew_count": 4, "zone": "kitchen", "label": "open"},
    )
    assert again.status_code == 200, again.text
    assert again.json()["observation"]["note"] == "no faces/PII stored"
    assert again.json()["observation"]["zone"] == "kitchen"


def _counter_frame(ts: int, living: int = 4, total: int = 10) -> dict:
    return {
        "ts": ts,
        "zones": {
            "living_room": living,
            "dance_floor": 3,
            "kitchen_bar": 2,
            "hallway": 1,
            "balcony": 0,
        },
        "total": total,
    }


def test_counter_frame_lands_in_flow_counts(client: TestClient):
    from sqlalchemy import select

    from app.platform import counter_health
    from app.platform_db import FlowCount, session_scope

    ts = 1_700_000_000
    res = client.post("/api/data/occupancy", json=_counter_frame(ts, living=4, total=7))
    assert res.status_code == 201
    assert res.json()["inserted"] == 6
    with session_scope() as session:
        rows = session.scalars(select(FlowCount).where(FlowCount.created_at == float(ts))).all()
    stored = {row.zone: row.count for row in rows}
    assert stored["living_room"] == 4
    assert stored["dance_floor"] == 3
    assert stored["total"] == 7
    assert all(row.source == "counter" and row.label == "estimate" for row in rows)
    assert stored["total"] != sum(stored[name] for name in stored if name != "total")
    assert counter_health(now=float(ts))["status"] == "live"
    assert counter_health(now=float(ts))["last_seen"] == ts
    assert counter_health(now=float(ts) + 15)["status"] == "live"
    assert counter_health(now=float(ts) + 15.01)["status"] == "stale"
    assert counter_health(now=float(ts) + 60)["status"] == "stale"
    assert counter_health(now=float(ts) + 60.01)["status"] == "offline"


def test_counter_health_http_and_bad_input(client: TestClient):
    from app.platform import counter_status

    assert counter_status(None, 1_000) == "offline"
    ts = int(time.time())
    res = client.post("/api/data/occupancy", json=_counter_frame(ts, living=1, total=6))
    assert res.status_code == 201
    health = client.get("/api/data/counter-health").json()
    assert health["status"] == "live"
    assert health["last_seen"] >= ts
    missing = client.post("/api/data/occupancy", json={"ts": ts, "total": 1, "zones": {"living_room": 1}})
    assert missing.status_code == 400
    named = _counter_frame(ts)
    named["name"] = "someone"
    assert client.post("/api/data/occupancy", json=named).status_code == 400
    lines = "\n".join(
        [
            __import__("json").dumps(_counter_frame(ts - 30, living=2, total=7)),
            __import__("json").dumps(_counter_frame(ts - 20, living=3, total=8)),
        ]
    )
    batch = client.post("/api/data/occupancy", content=lines, headers={"content-type": "application/x-ndjson"})
    assert batch.status_code == 201
    assert batch.json()["inserted"] == 12
    assert (
        client.post(
            "/api/data/occupancy",
            content='{"ts":1}\nnot-json',
            headers={"content-type": "application/x-ndjson"},
        ).status_code
        == 400
    )


def test_local_db_flag_ignores_neon():
    from app.config import LOCAL_DATABASE_URL, database_url_from_env

    neon = "postgresql+psycopg://motion_api:secret@ep-cool.neon.tech/motion?sslmode=require"
    assert database_url_from_env({"MOTION_DB_LOCAL": "1", "DATABASE_URL": neon}) == LOCAL_DATABASE_URL
    assert "neon" not in database_url_from_env({"MOTION_DB_LOCAL": "1", "DATABASE_URL": neon})
    local = "postgresql+psycopg://motion@127.0.0.1:5432/motion"
    assert database_url_from_env({"MOTION_DB_LOCAL": "1", "MOTION_DB_LOCAL_URL": local}) == local
    with pytest.raises(ValueError):
        database_url_from_env({"MOTION_DB_LOCAL": "1", "MOTION_DB_LOCAL_URL": neon})
    assert database_url_from_env({"MOTION_DB_LOCAL": "0", "DATABASE_URL": "sqlite:////tmp/x.sqlite3"}) == (
        "sqlite:////tmp/x.sqlite3"
    )
