# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_577ec9774d894738]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Provenance coverage: every file an agent branch changes must carry a current stamp.

A file is covered when the ledger has a stamp on it whose post_state_hash equals the file's hash
now (breadcrumbs excluded). An edit made without the SDK/CLI leaves the hash unmatched, so the gate
turns "silent drift" into a failed check on agent branches. Lane ownership is checked too.
"""
from __future__ import annotations

import fnmatch
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .hashing import file_content_hash
from .ledger import Ledger
from .registry import Registry

EXEMPT = (".agent/*", ".agent/**", "*package-lock.json", "*.lock", "*/pnpm-lock.yaml", "orch/provenance/schema/*")


def _git(root: Path, *args: str) -> list[str]:
    out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def changed_files(root: Path, base: str) -> list[str]:
    """Added/modified/renamed files vs the merge-base with `base`, including uncommitted and untracked ones."""
    mb = _git(root, "merge-base", base, "HEAD")[0]
    files = set(_git(root, "diff", "--name-only", "--diff-filter=ACMR", mb))
    files |= set(_git(root, "ls-files", "--others", "--exclude-standard"))
    return sorted(f for f in files if (root / f).is_file() and not any(fnmatch.fnmatch(f, g) for g in EXEMPT))


@dataclass
class CoverageReport:
    files: int = 0
    uncovered: list[str] = field(default_factory=list)
    lane: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.uncovered and not self.lane


def check_coverage(root: Path, files: list[str], ledger: Ledger, registry: Registry) -> CoverageReport:
    hashes: set[tuple[str, str]] = set()
    last_agent: dict[str, str] = {}
    for st in ledger.iter_entries():  # append order: the last stamp on a file wins
        path = st.scope.target_uri.split("#", 1)[0]
        if st.scope.post_state_hash:
            hashes.add((path, st.scope.post_state_hash))
        last_agent[path] = st.agent.agent_id
    rep = CoverageReport(files=len(files))
    for f in files:
        if (f, file_content_hash(root / f)) not in hashes:
            rep.uncovered.append(f)
        elif registry.entries and not registry.may_write(last_agent[f], f):
            rep.lane.append(f"{f}: last stamped by {last_agent[f]}, outside its lane")
    return rep
