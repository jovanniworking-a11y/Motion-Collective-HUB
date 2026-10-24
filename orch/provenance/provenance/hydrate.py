"""Read-before-write: rebuild context from prior stamps and brief the incoming agent compactly.

    briefing = HydrateAgentContext("apps/ops-panel/src/lib/api.ts")
    system_prompt += briefing.to_prompt()

Step 1 (provenance scan): ledger entries for the target and its dependencies + the inline breadcrumb.
Step 2 (negative constraints): every do_not_repeat / assumption becomes a hard constraint.
Integrity: if the file's current content hash differs from the last stamp's post_state_hash, the
file was changed by a human or an unlogged process since then -> integrity="DRIFT".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from .breadcrumbs import read_inline
from .hashing import file_content_hash
from .ledger import Ledger, find_repo_root
from .models import HandoffStatus, ProvenanceStamp


@dataclass
class HydrationBriefing:
    target_uri: str
    entries: list[ProvenanceStamp] = field(default_factory=list)
    integrity: str = "unknown"          # ok | DRIFT | untracked | missing | external
    current_hash: Optional[str] = None
    last_stamped_hash: Optional[str] = None
    inline: Optional[dict] = None

    @property
    def latest(self) -> Optional[ProvenanceStamp]:
        return self.entries[-1] if self.entries else None

    @property
    def hard_constraints(self) -> list[str]:
        out: list[str] = []
        for s in reversed(self.entries):
            for x in s.handoff_context.do_not_repeat:
                if (line := f"DO NOT: {x}") not in out:
                    out.append(line)
            if s.handoff_context.failure_reason and s.handoff_context.status in (HandoffStatus.reverted, HandoffStatus.blocked):
                line = f"FAILED BEFORE ({s.agent.agent_id}, {s.timestamp_utc[:10]}): {s.work_summary.intent} — {s.handoff_context.failure_reason}"
                if line not in out:
                    out.append(line[:300])
        return out

    @property
    def assumptions(self) -> list[str]:
        out: list[str] = []
        for s in reversed(self.entries):
            for x in s.handoff_context.assumptions_made:
                if x not in out:
                    out.append(x)
        return out

    @property
    def open_directives(self) -> list[str]:
        """Directives from the newest stamp (older ones are superseded by whoever stamped after)."""
        return list(self.latest.handoff_context.next_agent_directives) if self.latest else []

    def to_prompt(self, max_chars: int = 1800) -> str:
        head = f'<prior_agent_work target="{self.target_uri}" entries="{len(self.entries)}" integrity="{self.integrity}">'
        lines = [head]
        if self.integrity == "DRIFT":
            lines.append("! Content changed after the last stamp (human or unlogged edit). Re-read the file before trusting prior notes.")
        for s in self.entries:
            lines.append(f"- {s.timestamp_utc[:16]}Z {s.agent.agent_id} ({s.agent.role}) "
                         f"{s.handoff_context.status.value}/{s.work_summary.verification_status.value} "
                         f"[{s.trace_id}]: {s.work_summary.intent}")
        if not self.entries:
            lines.append("- no prior agent work recorded")
        if hc := self.hard_constraints:
            lines.append("<hard_constraints>")
            lines += [f"- {c}" for c in hc]
            lines.append("</hard_constraints>")
        if a := self.assumptions:
            lines.append("<assumptions_to_recheck>")
            lines += [f"- {x}" for x in a]
            lines.append("</assumptions_to_recheck>")
        if d := self.open_directives:
            lines.append("<open_directives>")
            lines += [f"- {x}" for x in d]
            lines.append("</open_directives>")
        lines.append("</prior_agent_work>")
        text = "\n".join(lines)
        if len(text) <= max_chars:
            return text
        # Compaction: keep header, drift note, constraints and directives; trim the history list oldest-first.
        hist = [l for l in lines if l.startswith("- ") and "Z " in l[:20]]
        while hist and len(text) > max_chars:
            lines.remove(hist.pop(0))
            text = "\n".join(lines)
        return text[: max_chars - 20] + "\n</prior_agent_work>" if len(text) > max_chars else text


def hydrate_agent_context(target_uri: str, *, repo_root: Optional[Path] = None, ledger: Optional[Ledger] = None,
                          last_n: int = 5, dependencies: Iterable[str] = ()) -> HydrationBriefing:
    root = Path(repo_root) if repo_root else find_repo_root()
    led = ledger or Ledger(root)
    entries = led.entries_for(target_uri, limit=last_n, dependencies=dependencies)
    b = HydrationBriefing(target_uri=target_uri, entries=entries)
    path_part = target_uri.split("#", 1)[0]
    if "://" in path_part:
        b.integrity = "external"
        return b
    p = root / path_part
    if not p.exists():
        b.integrity = "missing" if entries else "untracked"
        return b
    if p.is_file():
        b.current_hash = file_content_hash(p)
        try:
            b.inline = read_inline(p.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            b.inline = None
    exact = [s for s in entries if s.scope.path == path_part and s.scope.post_state_hash]
    if not exact:
        b.integrity = "untracked"
        return b
    b.last_stamped_hash = exact[-1].scope.post_state_hash
    b.integrity = "ok" if b.current_hash == b.last_stamped_hash else "DRIFT"
    return b


# The name used in the protocol docs.
HydrateAgentContext = hydrate_agent_context


def rolling_state_summary(ledger: Ledger, *, max_targets: int = 60) -> str:
    """Layer 3 compaction: one line per target (latest state) + every open directive. Feeds STATE.md."""
    latest: dict[str, ProvenanceStamp] = {}
    for s in ledger.iter_entries():
        latest[s.scope.path] = s
    rows = sorted(latest.values(), key=lambda s: s.timestamp_utc, reverse=True)[:max_targets]
    out = ["# Agent state (generated from .agent/ledger.jsonl, do not edit by hand)", "",
           "| Target | Last UTC | Agent | Status | Intent |", "|---|---|---|---|---|"]
    for s in rows:
        out.append(f"| `{s.scope.path}` | {s.timestamp_utc[:16]}Z | {s.agent.agent_id} | "
                   f"{s.handoff_context.status.value}/{s.work_summary.verification_status.value} | {s.work_summary.intent[:90]} |")
    open_d = [(s, d) for s in rows for d in s.handoff_context.next_agent_directives]
    out += ["", "## Open directives", ""]
    out += [f"- `{s.scope.path}` ({s.trace_id}): {d}" for s, d in open_d] or ["- none"]
    blocked = [s for s in rows if s.handoff_context.status in (HandoffStatus.blocked, HandoffStatus.reverted)]
    out += ["", "## Blocked / reverted (read before retrying)", ""]
    out += [f"- `{s.scope.path}` {s.handoff_context.status.value}: {s.handoff_context.failure_reason}" for s in blocked] or ["- none"]
    return "\n".join(out) + "\n"
