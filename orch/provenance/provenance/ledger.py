# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_6beb08a5a8484a0d]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Append-only, tamper-evident work ledger: `.agent/ledger.jsonl`.

Each line is one ProvenanceStamp. On append the ledger sets:
- prev_entry_hash: entry_hash of the last line in this file (or GENESIS_HASH)
- entry_hash: sha256 of the stamp's canonical JSON (everything except entry_hash)

Verification treats the file as a causal DAG rather than a strict chain, because the ledger is
merged with git's `union` driver (see .gitattributes): two branches may both append after the same
parent. Every entry must (a) hash to its own entry_hash and (b) point at genesis or at an entry
that appears earlier in the file. Editing any line breaks (a); deleting a referenced line breaks (b).
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Optional

from .hashing import sha256_bytes
from .models import GENESIS_HASH, HandoffStatus, ProvenanceStamp

LEDGER_REL = Path(".agent") / "ledger.jsonl"
DEAD_LETTER_REL = Path(".agent") / "dead_letter.jsonl"


class LedgerError(RuntimeError):
    pass


class LedgerLockTimeout(LedgerError):
    pass


def find_repo_root(start: Optional[Path] = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for cand in [p, *p.parents]:
        if (cand / ".git").exists() or (cand / ".agent").is_dir():
            return cand
    return p


class _FileLock:
    """Portable advisory lock using an O_EXCL lockfile (works on Linux, macOS and Windows)."""

    def __init__(self, path: Path, timeout: float = 10.0, stale_after: float = 60.0):
        self.path, self.timeout, self.stale_after = path, timeout, stale_after
        self._fd: Optional[int] = None

    def __enter__(self) -> "_FileLock":
        deadline = time.monotonic() + self.timeout
        self.path.parent.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                self._fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self._fd, f"{os.getpid()} {time.time()}".encode())
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > self.stale_after:
                        self.path.unlink(missing_ok=True)  # holder died; reclaim
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() > deadline:
                    raise LedgerLockTimeout(f"could not lock {self.path} within {self.timeout}s")
                time.sleep(0.02)

    def __exit__(self, *exc) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        self.path.unlink(missing_ok=True)


def compute_entry_hash(stamp: ProvenanceStamp) -> str:
    return sha256_bytes(stamp.canonical(without_entry_hash=True).encode("utf-8"))


@dataclass
class ChainReport:
    ok: bool
    entries: int = 0
    forks: int = 0
    problems: list[str] = field(default_factory=list)


class Ledger:
    def __init__(self, repo_root: Optional[Path] = None, path: Optional[Path] = None):
        self.root = Path(repo_root) if repo_root else find_repo_root()
        self.path = Path(path) if path else self.root / LEDGER_REL
        self.dead_letter_path = self.path.parent / DEAD_LETTER_REL.name
        self._lock_path = self.path.with_suffix(".lock")

    # ---------------------------------------------------------------- write
    def append(self, stamp: ProvenanceStamp) -> ProvenanceStamp:
        """Chain, hash and durably append one stamp. Returns the stamped copy. Raises on any failure."""
        with _FileLock(self._lock_path):
            prev = self._last_entry_hash() or GENESIS_HASH
            chained = stamp.model_copy(update={"prev_entry_hash": prev, "entry_hash": None})
            chained = chained.model_copy(update={"entry_hash": compute_entry_hash(chained)})
            line = chained.model_dump_json(exclude_none=False) + "\n"
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
            try:
                os.write(fd, line.encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
            if chained.handoff_context.status in (HandoffStatus.blocked, HandoffStatus.reverted):
                self._dead_letter(chained)
            return chained

    def _dead_letter(self, stamp: ProvenanceStamp) -> None:
        rec = {
            "timestamp_utc": stamp.timestamp_utc,
            "trace_id": stamp.trace_id,
            "agent_id": stamp.agent.agent_id,
            "target_uri": stamp.scope.target_uri,
            "status": stamp.handoff_context.status.value,
            "intent": stamp.work_summary.intent,
            "failure_reason": stamp.handoff_context.failure_reason,
            "do_not_repeat": stamp.handoff_context.do_not_repeat,
        }
        with open(self.dead_letter_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def _last_entry_hash(self) -> Optional[str]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            return None
        with open(self.path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            pos = fh.tell()
            buf = b""
            while pos > 0:
                step = min(4096, pos)
                pos -= step
                fh.seek(pos)
                buf = fh.read(step) + buf
                lines = [l for l in buf.split(b"\n") if l.strip()]
                if len(lines) >= 2 or pos == 0:
                    break
        lines = [l for l in buf.split(b"\n") if l.strip()]
        if not lines:
            return None
        try:
            return json.loads(lines[-1])["entry_hash"]
        except (ValueError, KeyError) as exc:
            raise LedgerError(f"last ledger line is not a valid stamp: {exc}") from exc

    # ---------------------------------------------------------------- read
    def iter_entries(self) -> Iterator[ProvenanceStamp]:
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as fh:
            for n, raw in enumerate(fh, 1):
                if not raw.strip():
                    continue
                try:
                    yield ProvenanceStamp.model_validate_json(raw)
                except Exception as exc:  # noqa: BLE001 - surface the line number
                    raise LedgerError(f"ledger line {n} is not a valid ProvenanceStamp: {exc}") from exc

    def entries_for(self, target_uri: str, *, limit: Optional[int] = None,
                    dependencies: Iterable[str] = ()) -> list[ProvenanceStamp]:
        """Chronological entries whose target path equals, or sits under, target_uri or a dependency."""
        wanted = [u.split("#", 1)[0].rstrip("/") for u in (target_uri, *dependencies)]

        def hit(stamp: ProvenanceStamp) -> bool:
            p = stamp.scope.path.rstrip("/")
            return any(p == w or p.startswith(w + "/") for w in wanted)

        found = [s for s in self.iter_entries() if hit(s)]
        found.sort(key=lambda s: s.timestamp_utc)
        return found[-limit:] if limit else found

    def find_idempotent(self, key: str) -> Optional[ProvenanceStamp]:
        for s in self.iter_entries():
            if s.idempotency_key == key and s.handoff_context.status == HandoffStatus.completed:
                return s
        return None

    def get_trace(self, trace_id: str) -> list[ProvenanceStamp]:
        return [s for s in self.iter_entries() if s.trace_id == trace_id or s.parent_trace_id == trace_id]

    def verify_chain(self) -> ChainReport:
        rep = ChainReport(ok=True)
        if not self.path.exists():
            return rep
        seen: set[str] = set()
        parents: dict[str, int] = {}
        with open(self.path, encoding="utf-8") as fh:
            for n, raw in enumerate(fh, 1):
                if not raw.strip():
                    continue
                rep.entries += 1
                try:
                    stamp = ProvenanceStamp.model_validate_json(raw)
                except Exception as exc:  # noqa: BLE001
                    rep.ok = False
                    rep.problems.append(f"line {n}: invalid stamp ({exc.__class__.__name__})")
                    continue
                if compute_entry_hash(stamp) != stamp.entry_hash:
                    rep.ok = False
                    rep.problems.append(f"line {n}: entry_hash mismatch (line edited after append) trace={stamp.trace_id}")
                prev = stamp.prev_entry_hash
                if prev != GENESIS_HASH and prev not in seen:
                    rep.ok = False
                    rep.problems.append(f"line {n}: prev_entry_hash points at a missing or later entry (deleted/reordered)")
                parents[prev] = parents.get(prev, 0) + 1
                if stamp.entry_hash:
                    seen.add(stamp.entry_hash)
        rep.forks = sum(1 for c in parents.values() if c > 1)
        return rep
