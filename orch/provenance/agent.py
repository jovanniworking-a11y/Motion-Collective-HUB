#!/usr/bin/env python3
"""Entry point: python3 orch/provenance/agent.py <command> ... (see provenance/__main__.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from provenance.__main__ import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
