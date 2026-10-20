from __future__ import annotations

import os
from pathlib import Path

# services/api/app/config.py → parents[3] = repo root (preserved in Docker layout)
REPO_ROOT = Path(os.environ.get("MOTION_REPO_ROOT", "")).resolve() if os.environ.get("MOTION_REPO_ROOT") else Path(__file__).resolve().parents[3]
ORCH_ROOT = REPO_ROOT / "orch"
BOARD_PATH = ORCH_ROOT / "tasks" / "BOARD.md"
INBOX_DIR = ORCH_ROOT / "tasks" / "inbox"
OUTBOX_DIR = ORCH_ROOT / "tasks" / "outbox"
STUDIO_DIR = ORCH_ROOT / "context" / "studio"

# Cloud MVP: set MOTION_DATA_DIR=/tmp/motion-api-data (ephemeral) or a mounted volume.
_default_data = Path(__file__).resolve().parents[1] / "data"
DATA_DIR = Path(os.environ.get("MOTION_DATA_DIR", str(_default_data))).expanduser().resolve()
USAGE_DB = DATA_DIR / "usage.sqlite3"
LAYOUT_STORE = DATA_DIR / "studio_layout.json"
CHAT_STORE = DATA_DIR / "agent_chats.json"
# Muse platform DB: override with DATABASE_URL=postgresql+psycopg://... for Postgres.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

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
