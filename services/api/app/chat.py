"""Per-area chat proxy — Anthropic if key present, otherwise deterministic mock."""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from .activity import clear_live, set_live
from .config import ANTHROPIC_API_KEY, CHAT_STORE
from .routing import get_agent, route_for
from .usage import log_usage

STANDING = (
    "Standing orders: never spend/send/post/publish; draft only. "
    "Label numbers confirmed/estimate/open. No venue address or guest PII."
)


def _load_chats() -> dict[str, list[dict[str, Any]]]:
    if not CHAT_STORE.exists():
        return {}
    try:
        return json.loads(CHAT_STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_chats(data: dict[str, list[dict[str, Any]]]) -> None:
    CHAT_STORE.parent.mkdir(parents=True, exist_ok=True)
    CHAT_STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def history(agent_id: str) -> list[dict[str, Any]]:
    return list(_load_chats().get(agent_id, []))


def _append(agent_id: str, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    data = _load_chats()
    thread = data.setdefault(agent_id, [])
    thread.extend(messages)
    data[agent_id] = thread[-80:]
    _save_chats(data)
    return data[agent_id]


def _mock_reply(agent: dict[str, Any], prompt: str, action: str) -> str:
    route = route_for(agent["area"], action)
    pl = prompt.lower()
    if action == "correct":
        return (
            f"[{agent['name']}] Correction noted (draft). "
            f"Standing preference for {agent['channel']}. "
            f"Routed via {route['model']}. {STANDING}"
        )
    if action == "form":
        return (
            f"[{agent['name']}] Formed system note:\n"
            f"— Role: {agent['description']}\n"
            f"— Default model: {agent['default_model']} (worker: {agent['worker']})\n"
            f"— Caps: {', '.join(agent['capabilities'])}\n{STANDING}"
        )
    if "sim" in pl or "crowd" in pl:
        return (
            f"[{agent['name']}] Use Muse → Run Sim (job API wraps studio scripts). "
            f"Route: {route['model']}. Draft only."
        )
    if "budget" in pl or "money" in pl or "pool" in pl:
        return (
            f"[{agent['name']}] Pool $450 (confirmed). Pool spend ~$381.13 (estimate). "
            f"Buffer ~$68.87 (estimate). HE//THEY $300 (confirmed); CDJ rental $345 (confirmed)."
        )
    return (
        f"[{agent['name']}] Received (mock — Pro bridge: Open in Claude.ai in the ops panel, "
        f"or set ANTHROPIC_API_KEY for billed API). "
        f"Route: {route['model']} · why: {route['why']}\n"
        f"You said: {prompt[:280]}\n{STANDING}"
    )


def _anthropic_reply(agent: dict[str, Any], prompt: str, action: str) -> tuple[str, int, int]:
    import httpx

    model_map = {
        "claude-sonnet": "claude-sonnet-4-20250514",
        "claude-haiku": "claude-3-5-haiku-latest",
    }
    model = model_map.get(agent["default_model"], "claude-3-5-haiku-latest")
    system = (
        f"You are the MOTION Collective agent for area '{agent['area']}' "
        f"({agent['name']}). {agent['description']} {STANDING} Action mode: {action}."
    )
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 512,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        body = resp.json()
    text_parts = [b.get("text", "") for b in body.get("content", []) if b.get("type") == "text"]
    usage = body.get("usage") or {}
    return (
        "\n".join(text_parts).strip() or "(empty model response)",
        int(usage.get("input_tokens") or 0),
        int(usage.get("output_tokens") or 0),
    )


def chat(agent_id: str, prompt: str, *, action: str = "prompt") -> dict[str, Any]:
    agent = get_agent(agent_id)
    if not agent:
        raise KeyError(f"unknown agent: {agent_id}")
    prompt = (prompt or "").strip()
    if not prompt and action == "prompt":
        raise ValueError("prompt required")
    if not prompt:
        prompt = f"(empty {action})"

    run_id = f"chat-{uuid.uuid4().hex[:10]}"
    set_live(
        run_id,
        {
            "id": run_id,
            "agent_id": agent_id,
            "action": action,
            "title": f"{agent['channel']} · {action}",
            "status": "running",
        },
    )

    model = agent["default_model"]
    provider = "mock"
    tokens_in = max(1, len(prompt) // 4)
    tokens_out = 0
    try:
        if ANTHROPIC_API_KEY and agent["default_model"].startswith("claude"):
            try:
                text, tokens_in, tokens_out = _anthropic_reply(agent, prompt, action)
                provider = "anthropic"
            except Exception as exc:  # noqa: BLE001
                text = f"(Anthropic error, mock fallback: {exc})\n" + _mock_reply(
                    agent, prompt, action
                )
                tokens_out = max(1, len(text) // 4)
                provider = "mock-fallback"
        else:
            text = _mock_reply(agent, prompt, action)
            tokens_out = max(1, len(text) // 4)
    finally:
        clear_live(run_id)

    ts = time.time()
    user_msg = {
        "id": f"u-{uuid.uuid4().hex[:8]}",
        "role": "user",
        "action": action,
        "content": prompt,
        "ts": ts,
    }
    assistant_msg = {
        "id": f"a-{uuid.uuid4().hex[:8]}",
        "role": "assistant",
        "action": action,
        "content": text,
        "ts": ts,
        "model": model,
        "provider": provider,
    }
    thread = _append(agent_id, [user_msg, assistant_msg])
    usage = log_usage(
        agent_id=agent_id,
        area=agent["area"],
        model=f"{provider}:{model}",
        action=action,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        label="estimate" if provider.startswith("mock") else "confirmed",
        meta=run_id,
    )
    return {
        "agent": agent,
        "message": assistant_msg,
        "thread": thread,
        "usage": usage,
        "route": route_for(agent["area"], action),
    }
