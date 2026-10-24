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


def strip_provenance(text: str) -> str:
    """Remove the inline breadcrumb block and any Markdown work-log region."""
    # Markdown / HTML work-log region (inclusive of markers and one trailing newline).
    while WORKLOG_BEGIN in text:
        start = text.index(WORKLOG_BEGIN)
        end = text.find(WORKLOG_END, start)
        if end == -1:
            raise ValueError("AGENT_WORKLOG:BEGIN without END marker; refusing to guess the region")
        end += len(WORKLOG_END)
        if text[end:end + 1] == "\n":
            end += 1
        # also drop the blank separator line we insert before the region
        if text[max(0, start - 2):start] == "\n\n":
            start -= 1
        text = text[:start] + text[end:]
    out: list[str] = []
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        if _INLINE_START.match(lines[i]):
            i += 1
            while i < len(lines) and _INLINE_CONT.match(lines[i]) and lines[i].strip():
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


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
