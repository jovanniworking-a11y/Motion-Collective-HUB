"""Agent activity feed — BOARD.md + inbox/outbox + in-memory run status."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from .config import BOARD_PATH, INBOX_DIR, OUTBOX_DIR

_LIVE: dict[str, dict[str, Any]] = {}


def set_live(run_id: str, payload: dict[str, Any]) -> None:
    _LIVE[run_id] = {**payload, "updated_at": time.time()}


def clear_live(run_id: str) -> None:
    _LIVE.pop(run_id, None)


def list_live() -> list[dict[str, Any]]:
    return sorted(_LIVE.values(), key=lambda x: x.get("updated_at", 0), reverse=True)


_BOARD_ROW = re.compile(
    r"^\|\s*(T-\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$",
    re.MULTILINE,
)


def parse_board(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or BOARD_PATH
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="replace")
    items: list[dict[str, Any]] = []
    for m in _BOARD_ROW.finditer(text):
        tid, task, owner, status = m.groups()
        if tid.upper() == "ID" or task.lower() == "task":
            continue
        items.append(
            {
                "id": tid.strip(),
                "task": task.strip(),
                "owner": owner.strip(),
                "status": status.strip(),
                "source": "board",
            }
        )
    return items


def _scan_md_dir(directory: Path, kind: str) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            mtime = path.stat().st_mtime
            head = path.read_text(encoding="utf-8", errors="replace")[:400]
            first = next((ln.strip() for ln in head.splitlines() if ln.strip()), path.stem)
            out.append(
                {
                    "id": path.stem,
                    "task": first.lstrip("# ").strip()[:160],
                    "owner": "worker" if kind == "outbox" else "orchestrator",
                    "status": kind,
                    "source": kind,
                    "updated_at": mtime,
                }
            )
        except OSError:
            continue
    return out


def activity_feed(limit: int = 40) -> dict[str, Any]:
    board = parse_board()
    inbox = _scan_md_dir(INBOX_DIR, "inbox")
    outbox = _scan_md_dir(OUTBOX_DIR, "outbox")
    live = list_live()
    feed: list[dict[str, Any]] = []
    for item in live:
        feed.append(
            {
                "kind": "live",
                "agent_id": item.get("agent_id"),
                "title": item.get("title") or item.get("action", "running"),
                "status": item.get("status", "running"),
                "ts": item.get("updated_at", time.time()),
                "detail": item,
            }
        )
    for row in board:
        feed.append(
            {
                "kind": "board",
                "agent_id": _owner_to_agent(row["owner"]),
                "title": f"{row['id']}: {row['task'][:80]}",
                "status": row["status"],
                "ts": None,
                "detail": row,
            }
        )
    for row in outbox[:15]:
        feed.append(
            {
                "kind": "outbox",
                "agent_id": _owner_to_agent(row.get("owner", "")),
                "title": row["task"],
                "status": "result",
                "ts": row.get("updated_at"),
                "detail": row,
            }
        )
    for row in inbox[:10]:
        feed.append(
            {
                "kind": "inbox",
                "agent_id": "orch",
                "title": row["task"],
                "status": "queued",
                "ts": row.get("updated_at"),
                "detail": row,
            }
        )

    def sort_key(e: dict[str, Any]) -> tuple:
        ts = e.get("ts") or 0
        prio = {"live": 0, "outbox": 1, "inbox": 2, "board": 3}.get(e["kind"], 9)
        return (prio, -float(ts))

    return {
        "feed": sorted(feed, key=sort_key)[:limit],
        "board_count": len(board),
        "inbox_count": len(inbox),
        "outbox_count": len(outbox),
        "live_count": len(live),
        "label": "confirmed" if board else "open",
    }


def _owner_to_agent(owner: str) -> str:
    o = (owner or "").lower()
    if "codex" in o:
        return "muse"
    if "chatgpt" in o or "gemini" in o:
        return "creative"
    return "orch"
