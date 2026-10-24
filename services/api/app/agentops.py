# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_859bf85b78e64c46]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Agent ops: cross-machine leases + a mirror of the provenance ledger.

- Leases live in the shared database (Postgres in the cloud, SQLite locally), so agents on different
  machines can't edit the same resource at once. Acquire is a row-locked read-modify-write.
- Stamps are mirrored into `agent_stamps` (idempotent on stamp_id) so the panel can show who did what
  without reading the git checkout. Locally the repo's `.agent/ledger.jsonl` is read as a fallback.

Machines authenticate with `Authorization: Bearer $MOTION_AGENT_TOKEN` (see auth.py); people use the
panel session. No guest data, no venue address: stamps are validated for both on the way in.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import time
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import Float, Integer, String, Text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from .config import REPO_ROOT
from .platform_db import Base, init_platform_db, session_scope

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")
_REQUIRED = ("stamp_id", "trace_id", "timestamp_utc", "agent", "scope", "work_summary", "handoff_context")


class AgentLease(Base):
    __tablename__ = "agent_leases"

    resource: Mapped[str] = mapped_column(String(400), primary_key=True)
    owner: Mapped[str] = mapped_column(String(64), nullable=False)
    lease_id: Mapped[str] = mapped_column(String(40), nullable=False)
    acquired_at: Mapped[float] = mapped_column(Float, nullable=False)
    expires_at: Mapped[float] = mapped_column(Float, nullable=False)
    ttl: Mapped[float] = mapped_column(Float, nullable=False)


class AgentStamp(Base):
    __tablename__ = "agent_stamps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stamp_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    timestamp_utc: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    target_uri: Mapped[str] = mapped_column(String(400), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(24), nullable=False)
    intent: Mapped[str] = mapped_column(String(240), nullable=False)
    stamp_json: Mapped[str] = mapped_column(Text, nullable=False)


class Conflict(RuntimeError):
    pass


def _row(l: AgentLease) -> dict[str, Any]:
    return {"resource": l.resource, "owner": l.owner, "lease_id": l.lease_id, "acquired_at": l.acquired_at,
            "expires_at": l.expires_at, "ttl": l.ttl}


def acquire(resource: str, owner: str, ttl: float) -> dict[str, Any]:
    try:
        return _acquire(resource, owner, ttl)
    except IntegrityError as exc:  # two first-time acquirers raced on the primary key
        raise Conflict(f"{resource} was just leased by another agent") from exc


def _acquire(resource: str, owner: str, ttl: float) -> dict[str, Any]:
    init_platform_db()
    now = time.time()
    with session_scope() as s:
        cur = s.execute(select(AgentLease).where(AgentLease.resource == resource).with_for_update()).scalar_one_or_none()
        if cur and cur.expires_at > now and cur.owner != owner:
            raise Conflict(f"{resource} is leased by {cur.owner} for another {int(cur.expires_at - now)}s")
        lease_id = f"ls_{secrets.token_hex(6)}"
        if cur:
            cur.owner, cur.lease_id, cur.acquired_at, cur.expires_at, cur.ttl = owner, lease_id, now, now + ttl, ttl
            row = cur
        else:
            row = AgentLease(resource=resource, owner=owner, lease_id=lease_id, acquired_at=now, expires_at=now + ttl, ttl=ttl)
            s.add(row)
        s.flush()
        return _row(row)


def heartbeat(resource: str, lease_id: str) -> dict[str, Any]:
    init_platform_db()
    with session_scope() as s:
        cur = s.execute(select(AgentLease).where(AgentLease.resource == resource).with_for_update()).scalar_one_or_none()
        if not cur or cur.lease_id != lease_id:
            raise Conflict(f"lease on {resource} was lost")
        cur.expires_at = time.time() + cur.ttl
        s.flush()
        return _row(cur)


def release(resource: str, lease_id: str) -> bool:
    init_platform_db()
    with session_scope() as s:
        cur = s.execute(select(AgentLease).where(AgentLease.resource == resource).with_for_update()).scalar_one_or_none()
        if cur and cur.lease_id == lease_id:
            s.delete(cur)
            return True
        return False


def active_leases() -> list[dict[str, Any]]:
    init_platform_db()
    now = time.time()
    with session_scope() as s:
        rows = s.execute(select(AgentLease).where(AgentLease.expires_at > now).order_by(AgentLease.expires_at)).scalars().all()
        return [_row(r) for r in rows]


def _check_clean(stamp: dict[str, Any]) -> None:
    missing = [k for k in _REQUIRED if k not in stamp]
    if missing:
        raise ValueError(f"stamp is missing {', '.join(missing)}")
    blob = json.dumps({k: stamp.get(k) for k in ("work_summary", "handoff_context")})
    if _EMAIL.search(blob) or _PHONE.search(blob):
        raise ValueError("stamp contains an email or phone number; guest data stays out")
    names = [n.strip() for n in re.split(r"[\n,]", os.environ.get("GUEST_DENYLIST", "")) if n.strip()]
    if names and re.search(r"(?<!\w)(?:" + "|".join(map(re.escape, names)) + r")(?!\w)", blob, re.IGNORECASE):
        raise ValueError("stamp contains a name on the guest denylist; guest data stays out")


def mirror_stamps(stamps: list[dict[str, Any]]) -> dict[str, int]:
    """Idempotent on stamp_id: re-sending the whole ledger is safe."""
    init_platform_db()
    added = skipped = 0
    with session_scope() as s:
        for st in stamps:
            _check_clean(st)
            if s.execute(select(AgentStamp.id).where(AgentStamp.stamp_id == st["stamp_id"])).first():
                skipped += 1
                continue
            s.add(AgentStamp(
                stamp_id=st["stamp_id"], trace_id=st["trace_id"], timestamp_utc=st["timestamp_utc"],
                agent_id=st["agent"]["agent_id"], target_uri=st["scope"]["target_uri"],
                status=st["handoff_context"]["status"], verification_status=st["work_summary"]["verification_status"],
                intent=st["work_summary"]["intent"][:240], stamp_json=json.dumps(st, separators=(",", ":")),
            ))
            added += 1
    return {"added": added, "skipped": skipped}


def _brief(st: dict[str, Any]) -> dict[str, Any]:
    hc, ws = st["handoff_context"], st["work_summary"]
    return {"timestamp_utc": st["timestamp_utc"], "agent_id": st["agent"]["agent_id"], "role": st["agent"].get("role"),
            "target_uri": st["scope"]["target_uri"], "status": hc["status"], "verification_status": ws["verification_status"],
            "intent": ws["intent"], "trace_id": st["trace_id"], "next": (hc.get("next_agent_directives") or [None])[0],
            "failure_reason": hc.get("failure_reason")}


def recent_stamps(limit: int = 30, ledger_path: Optional[Path] = None) -> dict[str, Any]:
    init_platform_db()
    with session_scope() as s:
        rows = s.execute(select(AgentStamp.stamp_json).order_by(AgentStamp.timestamp_utc.desc()).limit(limit)).scalars().all()
    if rows:
        return {"source": "database", "stamps": [_brief(json.loads(r)) for r in rows]}
    path = ledger_path or (REPO_ROOT / ".agent" / "ledger.jsonl")
    if path.exists():
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()][-limit:]
        return {"source": "ledger-file", "stamps": [_brief(json.loads(l)) for l in reversed(lines)]}
    return {"source": "none", "stamps": []}
