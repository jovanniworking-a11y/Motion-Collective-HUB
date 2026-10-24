"""Database surface: transactional outbox + shadow audit columns.

Write the business change and the stamp in ONE transaction:

    with engine.begin() as conn:
        conn.execute(text("UPDATE sim_runs SET ... WHERE id = :id"), {...})
        record_db_work(conn, stamp, table="sim_runs", pk_column="id", pk_value=42)

If the stamp insert fails, the whole transaction rolls back, so no row changes without provenance.
Works with a SQLAlchemy Connection (SQLite or Postgres).
"""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.engine import Connection

from .models import ProvenanceStamp

OUTBOX_TABLE = "agent_work_ledger"

_OUTBOX_DDL = {
    "postgresql": f"""
CREATE TABLE IF NOT EXISTS {OUTBOX_TABLE} (
    id BIGSERIAL PRIMARY KEY,
    stamp_id TEXT NOT NULL UNIQUE,
    trace_id TEXT NOT NULL,
    parent_trace_id TEXT,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    agent_id TEXT NOT NULL,
    target_uri TEXT NOT NULL,
    status TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    summary TEXT NOT NULL,
    idempotency_key TEXT,
    stamp JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS {OUTBOX_TABLE}_target_idx ON {OUTBOX_TABLE} (target_uri, timestamp_utc DESC);
CREATE UNIQUE INDEX IF NOT EXISTS {OUTBOX_TABLE}_idem_idx ON {OUTBOX_TABLE} (idempotency_key) WHERE idempotency_key IS NOT NULL AND status = 'completed';
""",
    "sqlite": f"""
CREATE TABLE IF NOT EXISTS {OUTBOX_TABLE} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp_id TEXT NOT NULL UNIQUE,
    trace_id TEXT NOT NULL,
    parent_trace_id TEXT,
    timestamp_utc TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    target_uri TEXT NOT NULL,
    status TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    summary TEXT NOT NULL,
    idempotency_key TEXT,
    stamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS {OUTBOX_TABLE}_target_idx ON {OUTBOX_TABLE} (target_uri, timestamp_utc);
""",
}

SHADOW_COLUMNS = ("last_agent_id", "last_agent_timestamp_utc", "last_agent_summary", "last_agent_trace_id")


def _ident(name: str) -> str:
    if not name.replace("_", "").isalnum():
        raise ValueError(f"unsafe SQL identifier: {name!r}")
    return name


def ensure_outbox(conn: Connection) -> None:
    for stmt in _OUTBOX_DDL["postgresql" if conn.dialect.name == "postgresql" else "sqlite"].split(";"):
        if stmt.strip():
            conn.execute(text(stmt))


def shadow_columns_ddl(table: str, dialect: str = "postgresql") -> list[str]:
    """ALTERs that add shadow audit columns to an existing table (idempotent on Postgres)."""
    t = _ident(table)
    ts_type = "TIMESTAMPTZ" if dialect == "postgresql" else "TEXT"
    ine = " IF NOT EXISTS" if dialect == "postgresql" else ""
    return [
        f"ALTER TABLE {t} ADD COLUMN{ine} last_agent_id TEXT",
        f"ALTER TABLE {t} ADD COLUMN{ine} last_agent_timestamp_utc {ts_type}",
        f"ALTER TABLE {t} ADD COLUMN{ine} last_agent_summary TEXT",
        f"ALTER TABLE {t} ADD COLUMN{ine} last_agent_trace_id TEXT",
    ]


def record_db_work(conn: Connection, stamp: ProvenanceStamp, *, table: Optional[str] = None,
                   pk_column: Optional[str] = None, pk_value: Any = None) -> None:
    """Insert the stamp into the outbox and, if a row is named, update its shadow columns.

    Must be called inside the caller's transaction (engine.begin()). Raises on failure so the
    surrounding business write rolls back with it.
    """
    ensure_outbox(conn)
    is_pg = conn.dialect.name == "postgresql"
    conn.execute(
        text(
            f"INSERT INTO {OUTBOX_TABLE} (stamp_id, trace_id, parent_trace_id, timestamp_utc, agent_id, target_uri, "
            f"status, verification_status, summary, idempotency_key, stamp) VALUES (:stamp_id, :trace_id, :parent, "
            f":ts, :agent, :target, :status, :verify, :summary, :idem, {'CAST(:stamp AS JSONB)' if is_pg else ':stamp'})"
        ),
        {
            "stamp_id": stamp.stamp_id, "trace_id": stamp.trace_id, "parent": stamp.parent_trace_id,
            "ts": stamp.timestamp_utc, "agent": stamp.agent.agent_id, "target": stamp.scope.target_uri,
            "status": stamp.handoff_context.status.value, "verify": stamp.work_summary.verification_status.value,
            "summary": stamp.work_summary.intent, "idem": stamp.idempotency_key, "stamp": stamp.model_dump_json(),
        },
    )
    if table:
        if not pk_column:
            raise ValueError("pk_column is required when table is given")
        t, k = _ident(table), _ident(pk_column)
        res = conn.execute(
            text(f"UPDATE {t} SET last_agent_id = :a, last_agent_timestamp_utc = :ts, last_agent_summary = :s, "
                 f"last_agent_trace_id = :tr WHERE {k} = :pk"),
            {"a": stamp.agent.agent_id, "ts": stamp.timestamp_utc, "s": stamp.work_summary.intent,
             "tr": stamp.trace_id, "pk": pk_value},
        )
        if res.rowcount == 0:
            raise LookupError(f"{table}.{pk_column}={pk_value!r} not found; nothing was stamped")
