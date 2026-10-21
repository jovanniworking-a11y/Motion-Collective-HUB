"""Repo link check runs with the API suite so a broken route fails pytest."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_repo_links_and_routes():
    root = Path(__file__).resolve().parents[3]
    script = root / "scripts" / "check_links.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
