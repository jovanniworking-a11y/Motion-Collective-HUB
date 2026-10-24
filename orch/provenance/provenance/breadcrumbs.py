# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_6baf428c517c455f]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Surface adapters: where a stamp is written at the site of work.

(a) Source/config files: one compact block (3 content lines) at the top, replaced on each stamp.
(b) Markdown/HTML docs: a machine AGENT_LOG comment plus a visible work-log table at the bottom.
(c) Git commits/PRs: Agent-* trailers.
(d) Databases: see db.py (outbox table + shadow columns, same transaction).

Inline blocks are pointers, never the payload: they carry the trace id and the full stamp lives in
`.agent/ledger.jsonl`. Files with no comment syntax (JSON, lockfiles, binaries) get ledger-only stamps.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from .hashing import WORKLOG_BEGIN, WORKLOG_END, strip_provenance
from .models import ProvenanceStamp

_HASH_STYLE = {".py", ".sh", ".bash", ".zsh", ".yml", ".yaml", ".toml", ".rb", ".r", ".pl", ".ps1", ".cfg", ".ini", ".env.example", ".dockerfile", ".mk"}
_SLASH_STYLE = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt", ".swift", ".c", ".h", ".cc", ".cpp", ".cs", ".scss", ".dart"}
_DASH_STYLE = {".sql", ".lua", ".hs"}
_CSS_STYLE = {".css"}
_DOC_STYLE = {".md", ".markdown"}
_HTML_STYLE = {".html", ".htm", ".xml", ".svg", ".vue"}
_NAMED_HASH = {"Dockerfile", "Makefile", ".gitignore", ".gitattributes", "requirements.txt"}

WORKLOG_MAX_ROWS = 10


def comment_style(path: Path) -> Optional[str]:
    """'hash' | 'slash' | 'dash' | 'css' | 'markdown' | 'html' | None (ledger-only)."""
    name, suf = path.name, path.suffix.lower()
    if name in _NAMED_HASH or suf in _HASH_STYLE:
        return "hash"
    if suf in _SLASH_STYLE:
        return "slash"
    if suf in _DASH_STYLE:
        return "dash"
    if suf in _CSS_STYLE:
        return "css"
    if suf in _DOC_STYLE:
        return "markdown"
    if suf in _HTML_STYLE:
        return "html"
    return None


def _one_line(s: str, limit: int = 150) -> str:
    s = " ".join(s.split())
    s = s.replace("*/", "* /").replace("-->", "- ->")
    return s if len(s) <= limit else s[: limit - 1] + "…"


def _short_ts(ts: str) -> str:
    return ts[:19] + "Z"  # 2026-10-24T20:32:23Z


def inline_lines(stamp: ProvenanceStamp) -> tuple[str, str, str]:
    head = (f"@agent-provenance [{_short_ts(stamp.timestamp_utc)}] [agent:{stamp.agent.agent_id}] "
            f"[status:{stamp.handoff_context.status.value}/{stamp.work_summary.verification_status.value}] [trace:{stamp.trace_id}]")
    summary = "@summary: " + _one_line(stamp.work_summary.intent)
    directives = stamp.handoff_context.next_agent_directives or stamp.handoff_context.do_not_repeat
    handoff = "@handoff: " + (_one_line(directives[0]) if directives else "none")
    return head, summary, handoff


def render_inline_block(stamp: ProvenanceStamp, style: str) -> str:
    head, summary, handoff = inline_lines(stamp)
    if style == "hash":
        return f"# {head}\n# {summary}\n# {handoff}\n"
    if style == "slash":
        return f"// {head}\n// {summary}\n// {handoff}\n"
    if style == "dash":
        return f"-- {head}\n-- {summary}\n-- {handoff}\n"
    if style == "css":
        return f"/* {head}\n * {summary}\n * {handoff}\n */\n"
    if style == "html":
        return f"<!-- {head}\n     {summary}\n     {handoff}\n-->\n"
    raise ValueError(f"no inline block for style {style!r}")


def _insertion_index(lines: list[str], style: str) -> int:
    """Keep the things that must stay first: shebang, Python encoding line, HTML doctype, XML prolog."""
    i = 0
    if lines and lines[0].startswith("#!"):
        i = 1
    if style == "hash" and i < len(lines) and re.match(r"^#.*coding[:=]", lines[i]):
        i += 1
    if style == "html" and lines:
        first = lines[0].lstrip().lower()
        if first.startswith("<!doctype") or first.startswith("<?xml"):
            i = 1
    return i


def apply_inline(text: str, stamp: ProvenanceStamp, style: str, previous: Optional[str] = None) -> str:
    """Replace any existing inline block with the new one (one block per file, newest wins).

    `previous` is the artifact before this agent's edit; Markdown work-log rows are carried over from
    it if the agent rewrote the file without the log region.
    """
    if style == "markdown":
        return apply_markdown_worklog(text, stamp, previous=previous)
    body = strip_provenance(text) if "@agent-provenance" in text else text
    lines = body.splitlines(keepends=True)
    at = _insertion_index(lines, style)
    return "".join(lines[:at]) + render_inline_block(stamp, style) + "".join(lines[at:])


# ---------------------------------------------------------------- Markdown work log
_ROW = re.compile(r"^\| (\d{4}-\d{2}-\d{2}T[^|]+) \|")


def _existing_rows(text: str) -> list[str]:
    start = text.rfind("\n" + WORKLOG_BEGIN + "\n")
    end = text.find("\n" + WORKLOG_END, start + 1)
    if start == -1 or end == -1:
        return []
    region = text[start:end]
    return [l for l in region.splitlines() if _ROW.match(l)]


def apply_markdown_worklog(text: str, stamp: ProvenanceStamp, previous: Optional[str] = None) -> str:
    rows = _existing_rows(text) or (_existing_rows(previous) if previous else [])
    hc, ws = stamp.handoff_context, stamp.work_summary
    nxt = hc.next_agent_directives[0] if hc.next_agent_directives else "—"
    row = (f"| {_short_ts(stamp.timestamp_utc)} | {stamp.agent.agent_id} | {hc.status.value} / {ws.verification_status.value} "
           f"| {_one_line(ws.intent, 90).replace('|', '/')} | {_one_line(nxt, 70).replace('|', '/')} | `{stamp.trace_id}` |")
    rows = [row, *rows][:WORKLOG_MAX_ROWS]
    machine = json.dumps({
        "v": stamp.provenance_version, "ts": stamp.timestamp_utc, "agent": stamp.agent.agent_id,
        "trace": stamp.trace_id, "status": hc.status.value, "verify": ws.verification_status.value,
        "hash": stamp.scope.post_state_hash, "ledger": ".agent/ledger.jsonl",
    }, separators=(",", ":"))
    region = "\n".join([
        WORKLOG_BEGIN,
        f"<!-- AGENT_LOG {machine} -->",
        "",
        "#### Agent work log",
        "| UTC | Agent | Status | Summary | Next | Trace |",
        "|---|---|---|---|---|---|",
        *rows,
        WORKLOG_END,
    ])
    return strip_provenance(text).rstrip("\n") + "\n\n" + region + "\n"


# ---------------------------------------------------------------- parse back
_HEAD = re.compile(r"@agent-provenance \[(?P<ts>[^\]]+)\] \[agent:(?P<agent>[^\]]+)\] \[status:(?P<status>[^\]]+)\] \[trace:(?P<trace>[^\]]+)\]")
_AGENT_LOG = re.compile(r"<!-- AGENT_LOG (\{.*?\}) -->")


def read_inline(text: str) -> Optional[dict]:
    """Parse the newest breadcrumb in a file: {'ts','agent','status','trace', 'hash'?}."""
    m = _AGENT_LOG.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except ValueError:
            return None
    m = _HEAD.search(text)
    return m.groupdict() if m else None


# ---------------------------------------------------------------- git trailers
TRAILER_KEYS = ("Agent-Id", "Agent-Timestamp", "Agent-Trace", "Agent-Status", "Agent-Summary", "Agent-Next-Step", "Agent-Trace-URI")
REQUIRED_TRAILERS = ("Agent-Id", "Agent-Timestamp", "Agent-Trace", "Agent-Summary")


def commit_trailers(stamp: ProvenanceStamp) -> dict[str, str]:
    hc = stamp.handoff_context
    return {
        "Agent-Id": stamp.agent.agent_id,
        "Agent-Timestamp": stamp.timestamp_utc,
        "Agent-Trace": stamp.trace_id,
        "Agent-Status": f"{hc.status.value}/{stamp.work_summary.verification_status.value}",
        "Agent-Summary": _one_line(stamp.work_summary.intent, 120),
        "Agent-Next-Step": _one_line(hc.next_agent_directives[0], 120) if hc.next_agent_directives else "none",
        "Agent-Trace-URI": f".agent/ledger.jsonl#{stamp.trace_id}",
    }


def format_trailers(stamp: ProvenanceStamp) -> str:
    return "\n".join(f"{k}: {v}" for k, v in commit_trailers(stamp).items())


def parse_trailers(message: str) -> dict[str, str]:
    """Read Agent-* trailers from the last paragraph block(s) of a commit message."""
    out: dict[str, str] = {}
    for line in message.splitlines():
        m = re.match(r"^(Agent-[A-Za-z-]+):\s*(.+)$", line.strip())
        if m and m.group(1) in TRAILER_KEYS:
            out[m.group(1)] = m.group(2).strip()
    return out


def check_commit_message(message: str) -> list[str]:
    """Empty list = OK. A commit without any Agent-* trailer is a human commit and passes."""
    tr = parse_trailers(message)
    if not tr:
        return []
    problems = [f"missing trailer {k}" for k in REQUIRED_TRAILERS if k not in tr]
    if "Agent-Timestamp" in tr:
        from .models import parse_utc

        try:
            parse_utc(tr["Agent-Timestamp"])
        except ValueError as exc:
            problems.append(str(exc))
    return problems
