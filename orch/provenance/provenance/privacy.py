# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_bcfca88991b7498a]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Guest-name denylist. The list itself never enters git.

Sources, merged: `.agent/private/guest_names.txt` (gitignored, one name per line, refreshed from
Tally by the daily check-in) and the `GUEST_DENYLIST` env var (newline- or comma-separated; CI reads
it from an Actions secret). Each entry matches as a whole phrase, case-insensitive. Store full names;
store a single word only when that is all the guest gave, so common first names don't block work.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

DENYLIST_REL = Path(".agent/private/guest_names.txt")


def _root() -> Path:
    here = Path.cwd().resolve()
    for p in (here, *here.parents):
        if (p / ".git").exists():
            return p
    return here


@lru_cache(maxsize=8)
def _compile(entries: tuple[str, ...]) -> Optional[re.Pattern]:
    if not entries:
        return None
    alts = sorted({re.escape(e) for e in entries}, key=len, reverse=True)
    return re.compile(r"(?<![\w])(?:" + "|".join(alts) + r")(?![\w])", re.IGNORECASE)


def load_entries(root: Optional[Path] = None) -> tuple[str, ...]:
    out: list[str] = []
    path = (root or _root()) / DENYLIST_REL
    try:
        out += path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, PermissionError):
        pass
    out += re.split(r"[\n,]", os.environ.get("GUEST_DENYLIST", ""))
    return tuple(sorted({" ".join(e.split()) for e in out if e.strip() and not e.lstrip().startswith("#")}))


def find_guest_names(text: str, root: Optional[Path] = None) -> list[str]:
    """Return the denylisted names found in text (deduplicated, as they appear). Never log the list."""
    rx = _compile(load_entries(root))
    if rx is None or not text:
        return []
    return sorted({m.group(0) for m in rx.finditer(text)})


def write_denylist(names: list[str], root: Optional[Path] = None) -> Path:
    path = (root or _root()) / DENYLIST_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = sorted({" ".join(n.split()) for n in names if n.strip()})
    path.write_text("# guest names (private, gitignored). One per line.\n" + "\n".join(clean) + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path
