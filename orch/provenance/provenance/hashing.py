# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_567b9c04de1b4546]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Content hashing that ignores provenance breadcrumbs.

The hash of an artifact is taken over its content with every provenance region removed, so:
- writing or replacing a breadcrumb never changes the artifact's hash;
- if anyone edits the real content after the last stamp, the current hash no longer matches the
  stamp's post_state_hash and hydration reports DRIFT (tamper/unlogged change).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional

# Inline code block: a run of comment lines whose first line carries "@agent-provenance".
_INLINE_START = re.compile(r"^\s*(#|//|--|/\*|<!--)\s*@agent-provenance\b")
_INLINE_CONT = re.compile(r"^\s*(#|//|--|\*|<!--)?\s*@(summary|handoff|hash)\b|^\s*\*/\s*$|^\s*-->\s*$")
WORKLOG_BEGIN = "<!-- AGENT_WORKLOG:BEGIN -->"
WORKLOG_END = "<!-- AGENT_WORKLOG:END -->"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


_PREAMBLE = re.compile(r"^(#!|#.*coding[:=]|\s*<!doctype|\s*<\?xml)", re.I)  # lines the SDK keeps above the block


def strip_provenance(text: str) -> str:
    """Remove the inline breadcrumb block (top of file) and the work-log region (end of file).

    Both are matched only where the SDK writes them, so code, tests or docs that merely mention
    the markers or show an example block are left alone.
    """
    start = text.rfind("\n" + WORKLOG_BEGIN + "\n")
    if start == -1 and text.startswith(WORKLOG_BEGIN + "\n"):
        start = 0
    if start != -1:
        end = text.find("\n" + WORKLOG_END, start)
        if end != -1 and not text[end + 1 + len(WORKLOG_END):].strip():
            text = text[:start].rstrip("\n") + "\n"
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines) and i < 2 and _PREAMBLE.match(lines[i]):
        i += 1
    if i < len(lines) and _INLINE_START.match(lines[i]):
        j = i + 1
        while j < len(lines) and _INLINE_CONT.match(lines[j]) and lines[j].strip():
            j += 1
        return "".join(lines[:i] + lines[j:])
    return text


def content_hash_text(text: str) -> str:
    # Trailing newlines are normalised so appending/removing a breadcrumb region is hash-neutral.
    body = strip_provenance(text).rstrip("\n") + "\n"
    return sha256_bytes(body.encode("utf-8"))


def content_hash_bytes(data: bytes) -> str:
    try:
        return content_hash_text(data.decode("utf-8"))
    except UnicodeDecodeError:
        return sha256_bytes(data)  # binary: hashed raw, never stamped inline


def file_content_hash(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return content_hash_bytes(path.read_bytes())
