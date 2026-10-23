from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

# services/api/app/config.py → parents[3] = repo root (preserved in Docker layout)
REPO_ROOT = Path(os.environ.get("MOTION_REPO_ROOT", "")).resolve() if os.environ.get("MOTION_REPO_ROOT") else Path(__file__).resolve().parents[3]
ORCH_ROOT = REPO_ROOT / "orch"
BOARD_PATH = ORCH_ROOT / "tasks" / "BOARD.md"
INBOX_DIR = ORCH_ROOT / "tasks" / "inbox"
OUTBOX_DIR = ORCH_ROOT / "tasks" / "outbox"
STUDIO_DIR = ORCH_ROOT / "context" / "studio"

# Cloud MVP: set MOTION_DATA_DIR=/tmp/motion-api-data (ephemeral) or a mounted volume.
# On Vercel the code directory is read-only; only /tmp is writable.
_default_data = Path("/tmp/motion-api-data") if os.environ.get("VERCEL") else Path(__file__).resolve().parents[1] / "data"
DATA_DIR = Path(os.environ.get("MOTION_DATA_DIR", str(_default_data))).expanduser().resolve()
USAGE_DB = DATA_DIR / "usage.sqlite3"
LAYOUT_STORE = DATA_DIR / "studio_layout.json"
CHAT_STORE = DATA_DIR / "agent_chats.json"
# Muse platform DB: override with DATABASE_URL=postgresql+psycopg://... for Postgres.
# Night-of on the venue laptop sets MOTION_DB_LOCAL=1 and ignores DATABASE_URL (Neon).
DATABASE_URL = (os.environ.get("DATABASE_URL", "") or os.environ.get("POSTGRES_URL", "")).strip()
LOCAL_DATABASE_URL = "postgresql+psycopg://motion@127.0.0.1:5432/motion"


def database_url_from_env(environ: Mapping[str, str] | None = None) -> str:
    """Resolve the platform database URL.

    MOTION_DB_LOCAL=1 forces localhost Postgres and does not read DATABASE_URL.
    MOTION_DB_LOCAL_URL may replace the default local URL. Its host must be
    localhost. Any other host is refused so a Neon string cannot sneak through.
    """
    env = os.environ if environ is None else environ
    flag = str(env.get("MOTION_DB_LOCAL", "")).strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        override = str(env.get("MOTION_DB_LOCAL_URL", "")).strip()
        if not override:
            return LOCAL_DATABASE_URL
        if not _is_localhost_postgres(override):
            raise ValueError("MOTION_DB_LOCAL_URL must be postgres on localhost")
        return override
    return str(env.get("DATABASE_URL", "") or env.get("POSTGRES_URL", "")).strip()


def _is_localhost_postgres(url: str) -> bool:
    from sqlalchemy.engine.url import make_url

    try:
        parsed = make_url(url)
    except Exception as exc:
        raise ValueError("MOTION_DB_LOCAL_URL is not a database URL") from exc
    host = (parsed.host or "").lower()
    return parsed.drivername.startswith("postgres") and host in {"localhost", "127.0.0.1", "::1"}

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
SIM_EXECUTE = os.environ.get("MOTION_SIM_EXECUTE", "").strip() in {"1", "true", "yes"}

# Comma-separated panel origins (local + Vercel/Railway URLs in cloud).
_cors_default = "http://localhost:3000,http://127.0.0.1:3000"
CORS_ORIGINS = [
    o.strip()
    for o in os.environ.get("MOTION_API_CORS", _cors_default).split(",")
    if o.strip()
]

DATA_DIR.mkdir(parents=True, exist_ok=True)
