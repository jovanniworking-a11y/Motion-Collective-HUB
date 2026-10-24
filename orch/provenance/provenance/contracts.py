# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_1d738f91acc1407c]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Delegation contracts: machine-checkable pre/postconditions and I/O schema validation."""
from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .hashing import file_content_hash
from .models import CapabilityTier, Condition, DelegationContract


class ContractViolation(RuntimeError):
    pass


class PreconditionFailed(ContractViolation):
    pass


class PostconditionFailed(ContractViolation):
    pass


class AuthorityExceeded(ContractViolation):
    pass


class ApprovalRequired(ContractViolation):
    """External side effects (spend / send / post / publish) need a human approval record first."""


@dataclass
class ConditionResult:
    condition: Condition
    ok: bool
    detail: str


def evaluate(cond: Condition, root: Path, ledger=None) -> ConditionResult:
    p = root / cond.target.split("#", 1)[0]
    if cond.kind == "file_exists":
        return ConditionResult(cond, p.exists(), f"{cond.target} {'exists' if p.exists() else 'is missing'}")
    if cond.kind == "file_absent":
        return ConditionResult(cond, not p.exists(), f"{cond.target} {'is absent' if not p.exists() else 'exists'}")
    if cond.kind == "file_hash_equals":
        cur = file_content_hash(p)
        return ConditionResult(cond, cur == cond.expected, f"hash {str(cur)[:19]}… vs expected {str(cond.expected)[:19]}…")
    if cond.kind == "command_succeeds":
        try:
            rc = subprocess.run(shlex.split(cond.target), cwd=root, capture_output=True, timeout=600).returncode
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return ConditionResult(cond, False, f"{cond.target}: {exc.__class__.__name__}")
        return ConditionResult(cond, rc == 0, f"{cond.target} → rc={rc}")
    if cond.kind in ("ledger_status_is", "no_drift"):
        from .hydrate import hydrate_agent_context

        b = hydrate_agent_context(cond.target, repo_root=root, ledger=ledger, last_n=1)
        if cond.kind == "no_drift":
            return ConditionResult(cond, b.integrity in ("ok", "untracked"), f"integrity={b.integrity}")
        st = b.latest.handoff_context.status.value if b.latest else "none"
        return ConditionResult(cond, st == cond.expected, f"latest status={st}")
    return ConditionResult(cond, False, f"unknown condition kind {cond.kind}")


def check_all(conds: list[Condition], root: Path, ledger=None) -> list[ConditionResult]:
    return [evaluate(c, root, ledger) for c in conds]


def validate_inputs(contract: DelegationContract) -> None:
    if contract.input_schema:
        import jsonschema

        try:
            jsonschema.Draft202012Validator(contract.input_schema).validate(contract.inputs)
        except jsonschema.ValidationError as exc:
            raise ContractViolation(f"inputs do not match input_schema: {exc.message}") from exc


def validate_output(contract: DelegationContract, output: Any) -> None:
    if contract.output_schema:
        import jsonschema

        try:
            jsonschema.Draft202012Validator(contract.output_schema).validate(output)
        except jsonschema.ValidationError as exc:
            raise PostconditionFailed(f"output does not match output_schema: {exc.message}") from exc


def authorize(contract: Optional[DelegationContract], tier: CapabilityTier, target_path: str) -> None:
    if contract is None:
        return
    if tier.rank > contract.max_capability_tier.rank:
        raise AuthorityExceeded(f"tier {tier.value} exceeds contract max {contract.max_capability_tier.value}")
    if not contract.allows(target_path):
        raise AuthorityExceeded(f"{target_path} is outside allowed_targets {contract.allowed_targets}")


def approval_path(root: Path, key: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in key)
    return root / ".agent" / "approvals" / f"{safe}.json"


def require_approval(root: Path, key: Optional[str]) -> dict:
    """An approval is a JSON file a human writes: {"approved_by": "jovanni", "approved_at_utc": "...", "scope": "..."}."""
    if not key:
        raise ApprovalRequired("external_side_effect work needs an idempotency_key that names the approval")
    p = approval_path(root, key)
    if not p.exists():
        raise ApprovalRequired(f"no approval record at {p.relative_to(root)}; a human must approve before any spend/send/post/publish")
    import json

    rec = json.loads(p.read_text())
    if not rec.get("approved_by"):
        raise ApprovalRequired(f"{p.relative_to(root)} has no approved_by")
    return rec
