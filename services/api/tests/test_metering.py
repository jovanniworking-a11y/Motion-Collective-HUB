"""T-038 · Usage metering: one row per agent call, counts only (no prompt text), routing matches the doc."""

from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routing import AGENT_REGISTRY

SECRET_PROMPT = "pass 041 group of seven, call 512-555-0199"


def _calls(c: TestClient) -> int:
    return c.get("/api/usage").json()["totals"]["calls"]


def test_each_chat_writes_exactly_one_usage_row():
    with TestClient(app) as c:
        for agent in AGENT_REGISTRY:
            before = _calls(c)
            r = c.post(f"/api/agents/{agent['id']}/chat", json={"prompt": "status?", "action": "prompt"})
            assert r.status_code == 200
            assert _calls(c) == before + 1, agent["id"]
            row = r.json()["usage"]
            assert row["agent_id"] == agent["id"] and row["area"] == agent["area"]
            assert row["label"] in {"confirmed", "estimate"}


def test_usage_rows_never_hold_prompt_text():
    with TestClient(app) as c:
        c.post("/api/agents/night-of/chat", json={"prompt": SECRET_PROMPT, "action": "prompt"})
        usage = c.get("/api/usage").json()
        blob = repr(usage)
        assert "512-555-0199" not in blob and "group of seven" not in blob
        latest = usage["recent"][0]
        assert latest["meta"].startswith("chat-")  # run id only


def test_sim_runs_are_metered():
    with TestClient(app) as c:
        before = _calls(c)
        assert c.post("/api/sims/run", json={"kind": "smoke-stub"}).status_code == 200
        assert _calls(c) == before + 1


def test_routing_table_matches_doc():
    doc = (Path(__file__).resolve().parents[1] / "MODEL_ROUTING.md").read_text()
    rows = {
        m.group(1): m.group(2)
        for m in re.finditer(r"^\| (\S+) \| #\S+ \| ([^|]+) \|", doc, flags=re.M)
    }
    assert rows, "routing table not found in MODEL_ROUTING.md"
    for agent in AGENT_REGISTRY:
        assert agent["area"] in rows, agent["area"]
        assert rows[agent["area"]].strip().startswith(agent["default_model"]), agent["area"]
