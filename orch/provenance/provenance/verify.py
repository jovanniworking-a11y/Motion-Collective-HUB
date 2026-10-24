# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_2c786e3cbf064355]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Deterministic verification gate: success is proven by commands, not self-assessment."""
from __future__ import annotations

import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence, Union

from .models import VerificationStatus

Command = Union[str, Sequence[str]]


@dataclass
class CheckResult:
    command: str
    returncode: int
    seconds: float
    tail: str


@dataclass
class VerificationResult:
    status: VerificationStatus
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def evidence(self) -> str:
        if not self.checks:
            return "no verification commands given"
        parts = [f"{c.command} → rc={c.returncode} in {c.seconds:.1f}s" + (f" ({c.tail})" if c.tail else "") for c in self.checks]
        return "; ".join(parts)[:780]

    @property
    def passed(self) -> bool:
        return self.status == VerificationStatus.verified_passed


def _last_line(out: str) -> str:
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return lines[-1][:120] if lines else ""


def run_gate(commands: Sequence[Command], *, cwd: Optional[Path] = None, timeout: float = 900.0,
             stop_on_first_failure: bool = True) -> VerificationResult:
    if not commands:
        return VerificationResult(VerificationStatus.unverified)
    results: list[CheckResult] = []
    ok = True
    for cmd in commands:
        argv = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
        label = cmd if isinstance(cmd, str) else " ".join(cmd)
        t0 = time.monotonic()
        try:
            proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout)
            rc, tail = proc.returncode, _last_line(proc.stdout) or _last_line(proc.stderr)
        except FileNotFoundError as exc:
            rc, tail = 127, f"not found: {exc.filename}"
        except subprocess.TimeoutExpired:
            rc, tail = 124, f"timed out after {timeout:.0f}s"
        results.append(CheckResult(label, rc, time.monotonic() - t0, tail))
        if rc != 0:
            ok = False
            if stop_on_first_failure:
                break
    return VerificationResult(VerificationStatus.verified_passed if ok else VerificationStatus.verified_failed, results)
