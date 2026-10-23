"""Usage metering — tokens/calls per bot, labeled. Same database as the Muse platform
(SQLite locally, Postgres when DATABASE_URL is set), so it survives serverless restarts."""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy import func, select

from .platform_db import UsageEvent, init_platform_db, session_scope


def init_usage_db() -> None:
    init_platform_db()


def _row(e: UsageEvent) -> dict[str, Any]:
    return {
        "id": e.id,
        "ts": e.ts,
        "agent_id": e.agent_id,
        "area": e.area,
        "model": e.model,
        "action": e.action,
        "tokens_in": e.tokens_in,
        "tokens_out": e.tokens_out,
        "label": e.label,
        "meta": e.meta,
    }


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
    with session_scope() as s:
        e = UsageEvent(
            ts=time.time(),
            agent_id=agent_id,
            area=area,
            model=model,
            action=action,
            tokens_in=int(tokens_in),
            tokens_out=int(tokens_out),
            label=label,
            meta=meta,
        )
        s.add(e)
        s.flush()
        return _row(e)


def usage_summary() -> dict[str, Any]:
    init_usage_db()
    with session_scope() as s:
        grouped = s.execute(
            select(
                UsageEvent.agent_id,
                UsageEvent.area,
                UsageEvent.model,
                func.count().label("calls"),
                func.coalesce(func.sum(UsageEvent.tokens_in), 0).label("tokens_in"),
                func.coalesce(func.sum(UsageEvent.tokens_out), 0).label("tokens_out"),
            )
            .group_by(UsageEvent.agent_id, UsageEvent.area, UsageEvent.model)
            .order_by(func.count().desc())
        ).all()
        recent = s.scalars(select(UsageEvent).order_by(UsageEvent.id.desc()).limit(50)).all()
        by_bot = [
            {
                "agent_id": r.agent_id,
                "area": r.area,
                "model": r.model,
                "calls": int(r.calls),
                "tokens_in": int(r.tokens_in),
                "tokens_out": int(r.tokens_out),
            }
            for r in grouped
        ]
        recent_rows = [_row(e) for e in recent]
    return {
        "by_bot": by_bot,
        "recent": recent_rows,
        "totals": {
            "calls": sum(r["calls"] for r in by_bot),
            "tokens_in": sum(r["tokens_in"] for r in by_bot),
            "tokens_out": sum(r["tokens_out"] for r in by_bot),
            "label": "estimate",
        },
    }
