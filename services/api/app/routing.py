from __future__ import annotations
from typing import Any

AGENT_REGISTRY: list[dict[str, Any]] = [
    {"id":"muse","area":"muse","name":"Muse / Studio","channel":"#muse-3d","description":"Room Studio layout, crowd sims, drink/bin/ball optimizers.","default_model":"claude-sonnet","worker":"Codex","capabilities":["layout","sim","optimize"]},
    {"id":"night-of","area":"night-of","name":"Night-Of Ops","channel":"#night-of","description":"Door check-in, welfare rounds, run-of-show cues.","default_model":"claude-haiku","worker":"Claude","capabilities":["ops","checklist","welfare"]},
    {"id":"logistics","area":"logistics","name":"Logistics","channel":"#logistics","description":"Budget lines, vendors, gear, load-in timing.","default_model":"claude-sonnet","worker":"Codex","capabilities":["budget","vendors","gear"]},
    {"id":"creative","area":"creative","name":"Creative","channel":"#creative","description":"Promo drafts, edit recipes, FX — never publish from here.","default_model":"chatgpt","worker":"ChatGPT","capabilities":["copy","promo","edit-recipe"]},
    {"id":"orch","area":"orch","name":"Orchestration","channel":"#orch","description":"Task board, inbox/outbox, worker routing decisions.","default_model":"claude-sonnet","worker":"Claude","capabilities":["board","routing","review"]},
]

MODEL_ROUTES: list[dict[str, str]] = [
    {"area":"muse","task_kind":"sim / studio code","model":"claude-sonnet → Codex seat","why":"Needs file edits + Playwright; keep Claude for brief/review only."},
    {"area":"muse","task_kind":"quick layout Q&A","model":"claude-haiku","why":"Cheap answers for param nudges."},
    {"area":"night-of","task_kind":"crew checklist / cue help","model":"claude-haiku","why":"Short ops answers; low latency."},
    {"area":"logistics","task_kind":"budget / workbook","model":"claude-sonnet → Codex","why":"Numbers + xlsx; label confirmed/estimate/open."},
    {"area":"creative","task_kind":"IG captions / DMs","model":"chatgpt","why":"Fast copy; draft only."},
    {"area":"creative","task_kind":"video / reel audit","model":"gemini","why":"Long multimodal clips."},
    {"area":"orch","task_kind":"split work / SoT decisions","model":"claude-sonnet (orchestrator)","why":"Only Claude edits SoT."},
    {"area":"*","task_kind":"spend / post / publish","model":"none — human gate","why":"Never spend/send/post without Jovanni OK."},
]

def get_agent(agent_id: str) -> dict[str, Any] | None:
    for a in AGENT_REGISTRY:
        if a["id"] == agent_id:
            return a
    return None

def route_for(area: str, task_kind: str = "") -> dict[str, str]:
    kind = (task_kind or "").lower()
    area_l = (area or "").lower()
    for row in MODEL_ROUTES:
        if row["area"] in {area_l, "*"} and (not kind or kind in row["task_kind"].lower()):
            if row["area"] == area_l or (row["area"] == "*" and "spend" in kind):
                return row
    agent = next((a for a in AGENT_REGISTRY if a["area"] == area_l), None)
    if agent:
        return {"area": area_l, "task_kind": task_kind or "general", "model": agent["default_model"], "why": f"Default for {agent['name']}"}
    return {"area": area_l or "unknown", "task_kind": task_kind or "general", "model": "claude-haiku", "why": "Fallback cheap route"}
