from __future__ import annotations
import os
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[3]
ORCH_ROOT = REPO_ROOT / "orch"
BOARD_PATH = ORCH_ROOT / "tasks" / "BOARD.md"
INBOX_DIR = ORCH_ROOT / "tasks" / "inbox"
OUTBOX_DIR = ORCH_ROOT / "tasks" / "outbox"
STUDIO_DIR = ORCH_ROOT / "context" / "studio"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
USAGE_DB = DATA_DIR / "usage.sqlite3"
LAYOUT_STORE = DATA_DIR / "studio_layout.json"
CHAT_STORE = DATA_DIR / "agent_chats.json"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
SIM_EXECUTE = os.environ.get("MOTION_SIM_EXECUTE", "").strip() in {"1", "true", "yes"}
CORS_ORIGINS = [o.strip() for o in os.environ.get("MOTION_API_CORS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()]
DATA_DIR.mkdir(parents=True, exist_ok=True)
