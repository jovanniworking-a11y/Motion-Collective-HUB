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


def test_contract_sim_run_is_insert_only(client: TestClient):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    from app.contract import contract_engine

    body = {
        "sim_id": "E001-layout-b",
        "event_id": "E001",
        "model": "room-studio",
        "params_json": {"guests": 50},
        "predicted_peak_curve": [30.42],
    }
    first = client.post("/api/data/sim_runs", json=body)
    assert first.status_code == 200
    row_id = first.json()["id"]
    assert isinstance(row_id, int)
    again = client.post(
        "/api/data/sim_runs",
        json={**body, "params_json": {"guests": 70}, "predicted_peak_curve": [99]},
    )
    assert again.status_code == 409
    with contract_engine().connect() as conn:
        stored = conn.execute(
            text("SELECT params_json, predicted_peak_curve FROM sim_runs WHERE sim_id = :sim_id"),
            {"sim_id": "E001-layout-b"},
        ).one()
    assert "50" in str(stored[0])
    assert "70" not in str(stored[0])
    assert "99" not in str(stored[1])
    with pytest.raises(IntegrityError, match="insert-only"):
        with contract_engine().begin() as conn:
            conn.execute(text("UPDATE sim_runs SET model = 'edited' WHERE sim_id = 'E001-layout-b'"))
    with pytest.raises(IntegrityError, match="insert-only"):
        with contract_engine().begin() as conn:
            conn.execute(text("DELETE FROM sim_runs WHERE sim_id = 'E001-layout-b'"))
    assert client.put("/api/data/sim_runs", json=body).status_code == 405
    assert client.delete("/api/data/sim_runs").status_code == 405


def test_contract_rejects_bad_input(client: TestClient):
    missing = client.post("/api/data/sim_runs", json={"sim_id": "only"})
    assert missing.status_code == 400
    banned = client.post(
        "/api/data/sim_runs",
        json={
            "sim_id": "E001-banned",
            "event_id": "E001",
            "model": "room-studio",
            "params_json": {"address": "nope"},
            "predicted_peak_curve": [],
        },
    )
    assert banned.status_code == 400
    unknown = client.post(
        "/api/data/events",
        json={"event_id": "E001", "name": "AFTERIMAGE 001", "phone": "555"},
    )
    assert unknown.status_code == 400
    invalid = client.post(
        "/api/data/events",
        content="not-json",
        headers={"content-type": "application/json"},
    )
    assert invalid.status_code == 400
    array = client.post("/api/data/zones", json=["dance"])
    assert array.status_code == 400
    named = client.post(
        "/api/data/occupancy_samples",
        json={
            "ts": 1_700_000_000,
            "event_id": "E001",
            "zone_id": "dance",
            "headcount": 3,
            "source": "wyze_living",
            "confidence": 0.8,
            "name": "someone",
        },
    )
    assert named.status_code == 400
    zero = client.post(
        "/api/data/drink_events",
        json={"ts": "2026-10-30T21:00:00Z", "event_id": "E001", "drink_id": "paloma", "qty": 0},
    )
    assert zero.status_code == 400


def test_contract_upserts_and_inserts_counts(client: TestClient):
    from sqlalchemy import text

    from app.contract import contract_engine

    event = client.post("/api/data/events", json={"event_id": "E001", "name": "AFTERIMAGE 001", "cap": 70})
    assert event.status_code == 200
    assert event.json()["id"] == "E001"
    renamed = client.post("/api/data/events", json={"event_id": "E001", "name": "AFTERIMAGE 001"})
    assert renamed.status_code == 200
    assert renamed.json()["id"] == "E001"
    zone = client.post(
        "/api/data/zones",
        json={"zone_id": "dance", "event_id": "E001", "name": "dance", "area_sqft": 124.5},
    )
    assert zone.status_code == 200
    assert zone.json()["id"] == "dance"
    moved = client.post(
        "/api/data/zones",
        json={"zone_id": "dance", "event_id": "E001", "name": "dance floor", "area_sqft": 124.5},
    )
    assert moved.json()["id"] == "dance"
    sample_a = client.post(
        "/api/data/occupancy_samples",
        json={
            "ts": 1_700_000_000,
            "event_id": "E001",
            "zone_id": "dance",
            "headcount": 30,
            "source": "wyze_living",
            "confidence": 0.8,
        },
    )
    sample_b = client.post(
        "/api/data/occupancy_samples",
        json={
            "ts": 1_700_000_010,
            "event_id": "E001",
            "zone_id": "dance",
            "headcount": 31,
            "source": "wyze_living",
            "confidence": 0.7,
        },
    )
    assert sample_a.status_code == 200
    assert sample_b.status_code == 200
    assert sample_a.json()["id"] != sample_b.json()["id"]
    drink = client.post(
        "/api/data/drink_events",
        json={"ts": 1_700_000_000, "event_id": "E001", "drink_id": "paloma", "qty": 1},
    )
    assert drink.status_code == 200
    assert isinstance(drink.json()["id"], int)
    with contract_engine().connect() as conn:
        zone_name = conn.execute(text("SELECT name FROM zones WHERE zone_id = 'dance'")).scalar()
        cap = conn.execute(text("SELECT cap FROM events WHERE event_id = 'E001'")).scalar()
        count = conn.execute(text("SELECT COUNT(*) FROM occupancy_samples")).scalar()
    assert zone_name == "dance floor"
    assert cap == 70
    assert count == 2


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
    # Dance is not added into total. Jerry's total is stored as sent.
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
    assert client.post(
        "/api/data/occupancy",
        content='{"ts":1}\nnot-json',
        headers={"content-type": "application/x-ndjson"},
    ).status_code == 400


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


def test_contract_postgres_role_and_lock_are_declared():
    import inspect

    from app import contract

    assert "SET LOCAL ROLE motion_api" in inspect.getsource(contract._assume_motion_api)
    assert "BEFORE UPDATE OR DELETE" in contract._POSTGRES_TRIGGER_CREATE
    assert "REVOKE UPDATE, DELETE ON sim_runs" in inspect.getsource(contract._grant_motion_api)
    assert "UPDATE sim_runs" not in inspect.getsource(contract._write_insert)
    assert "DELETE FROM sim_runs" not in inspect.getsource(contract._write_insert)
