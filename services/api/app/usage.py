"""Local usage metering — SQLite, tokens/calls per bot, labeled."""

from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Iterator

from .config import USAGE_DB


def _connect() -> sqlite3.Connection:
    USAGE_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(USAGE_DB), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_usage_db() -> None:
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                agent_id TEXT NOT NULL,
                area TEXT NOT NULL,
                model TEXT NOT NULL,
                action TEXT NOT NULL,
                tokens_in INTEGER NOT NULL DEFAULT 0,
                tokens_out INTEGER NOT NULL DEFAULT 0,
                label TEXT NOT NULL DEFAULT 'estimate',
                meta TEXT NOT NULL DEFAULT ''
            )
            """
        )


def log_usage(
    *,
    agent_id: str,
    area: str,
    model: str,
    action: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    label: str = "estimate",
    meta: str = "",
) -> dict[str, Any]:
    init_usage_db()
    ts = time.time()
    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO usage_events
            (ts, agent_id, area, model, action, tokens_in, tokens_out, label, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, agent_id, area, model, action, tokens_in, tokens_out, label, meta),
        )
        row_id = cur.lastrowid
    return {
        "id": row_id,
        "ts": ts,
        "agent_id": agent_id,
        "area": area,
        "model": model,
        "action": action,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "label": label,
        "meta": meta,
    }


def usage_summary() -> dict[str, Any]:
    init_usage_db()
    with db() as conn:
        rows = conn.execute(
            """
            SELECT agent_id, area, model,
                   COUNT(*) AS calls,
                   SUM(tokens_in) AS tokens_in,
                   SUM(tokens_out) AS tokens_out
            FROM usage_events
            GROUP BY agent_id, area, model
            ORDER BY calls DESC
            """
        ).fetchall()
        recent = conn.execute(
            """
            SELECT id, ts, agent_id, area, model, action,
                   tokens_in, tokens_out, label, meta
            FROM usage_events
            ORDER BY id DESC
            LIMIT 50
            """
        ).fetchall()
    return {
        "by_bot": [dict(r) for r in rows],
        "recent": [dict(r) for r in recent],
        "totals": {
            "calls": sum(int(r["calls"]) for r in rows),
            "tokens_in": sum(int(r["tokens_in"] or 0) for r in rows),
            "tokens_out": sum(int(r["tokens_out"] or 0) for r in rows),
            "label": "estimate",
        },
    }
