"""Typed data models for the Universal Agent Work Provenance protocol (v1.0).

Three wire objects:
- ProvenanceStamp     one immutable record per agent action on one target
- DelegationContract  what an orchestrator hands a sub-agent (I/O, pre/postconditions, DoD, authority)
- HandoffDirective    one concrete instruction left for the next agent

All timestamps are ISO-8601 UTC with millisecond precision and a trailing "Z".
All content hashes are "sha256:<64 hex>" over the artifact with provenance breadcrumbs stripped,
so stamping a file never changes its own hash (see hashing.py).
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PROVENANCE_VERSION = "1.0"
HASH_PATTERN = r"^sha256:[0-9a-f]{64}$"
GENESIS_HASH = "sha256:" + "0" * 64
_ID = r"^[a-z0-9][a-z0-9._-]{1,63}$"
_TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$")

# Guest data never goes into the ledger (house rule). Cheap, conservative guards.
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_utc(ts: str) -> datetime:
    if not _TS.match(ts):
        raise ValueError(f"not an ISO-8601 UTC timestamp ending in Z: {ts!r}")
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def assert_no_personal_data(text: str, field: str) -> str:
    if _EMAIL.search(text) or _PHONE.search(text):
        raise ValueError(f"{field} looks like it contains an email or phone number; guest data stays out of the ledger")
    return text


class SurfaceType(str, Enum):
    code_file = "code_file"
    doc_section = "doc_section"
    database_row = "database_row"
    issue_ticket = "issue_ticket"
    pull_request = "pull_request"
    git_commit = "git_commit"
    state_node = "state_node"


class VerificationStatus(str, Enum):
    verified_passed = "verified_passed"
    verified_failed = "verified_failed"
    unverified = "unverified"


class HandoffStatus(str, Enum):
    completed = "completed"
    partial = "partial"
    blocked = "blocked"
    reverted = "reverted"


class CapabilityTier(str, Enum):
    """Bounded authority. Ordered: read < sandbox_write < mutate_shared < external_side_effect."""

    read = "read"
    sandbox_write = "sandbox_write"
    mutate_shared = "mutate_shared"
    external_side_effect = "external_side_effect"  # spend / send / post / publish: needs a human approval record

    @property
    def rank(self) -> int:
        return ["read", "sandbox_write", "mutate_shared", "external_side_effect"].index(self.value)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=False, str_strip_whitespace=True)


class AgentIdentity(_Strict):
    agent_id: str = Field(pattern=_ID, description="Stable id of the worker, e.g. 'claude-code' or 'grok-jerry'")
    role: str = Field(min_length=2, max_length=64, description="Capability/role, e.g. 'backend-builder'")
    model: Optional[str] = Field(default=None, max_length=64, description="Optional. Leave empty in this repo (house rule: no model ids in pushed artifacts).")
    session_id: str = Field(min_length=1, max_length=80)
    parent_delegation_id: Optional[str] = Field(default=None, max_length=80)


class Scope(_Strict):
    surface_type: SurfaceType
    target_uri: str = Field(min_length=1, max_length=400, description="Repo-relative path (+ optional #L10-L20) or scheme URI, e.g. db://motion/sim_runs/42")
    pre_state_hash: Optional[str] = Field(default=None, pattern=HASH_PATTERN)
    post_state_hash: Optional[str] = Field(default=None, pattern=HASH_PATTERN)

    @property
    def path(self) -> str:
        return self.target_uri.split("#", 1)[0]


class WorkSummary(_Strict):
    intent: str = Field(min_length=3, max_length=240)
    actions_taken: list[str] = Field(default_factory=list, max_length=25)
    verification_status: VerificationStatus = VerificationStatus.unverified
    verification_evidence: str = Field(default="", max_length=800)

    @field_validator("actions_taken")
    @classmethod
    def _short(cls, v: list[str]) -> list[str]:
        out = []
        for a in v:
            a = " ".join(a.split())
            if not a:
                continue
            out.append(assert_no_personal_data(a[:240], "actions_taken"))
        return out

    @field_validator("intent", "verification_evidence")
    @classmethod
    def _clean(cls, v: str, info) -> str:
        return assert_no_personal_data(" ".join(v.split()), info.field_name)


class HandoffContext(_Strict):
    status: HandoffStatus
    assumptions_made: list[str] = Field(default_factory=list, max_length=20)
    do_not_repeat: list[str] = Field(default_factory=list, max_length=20)
    next_agent_directives: list[str] = Field(default_factory=list, max_length=20)
    failure_reason: Optional[str] = Field(default=None, max_length=800)

    @field_validator("assumptions_made", "do_not_repeat", "next_agent_directives")
    @classmethod
    def _lines(cls, v: list[str], info) -> list[str]:
        return [assert_no_personal_data(" ".join(x.split())[:300], info.field_name) for x in v if x and x.strip()]


class ProvenanceStamp(_Strict):
    provenance_version: Literal["1.0"] = PROVENANCE_VERSION
    stamp_id: str = Field(default_factory=lambda: new_id("stp"))
    trace_id: str = Field(default_factory=lambda: new_id("tr"), description="Causal id of this unit of work")
    parent_trace_id: Optional[str] = Field(default=None, description="Trace that caused this one (delegation or nesting)")
    delegation_id: Optional[str] = None
    idempotency_key: Optional[str] = Field(default=None, max_length=160)
    timestamp_utc: str = Field(default_factory=utc_now_iso)
    capability_tier: CapabilityTier = CapabilityTier.mutate_shared
    agent: AgentIdentity
    scope: Scope
    work_summary: WorkSummary
    handoff_context: HandoffContext
    # Filled by the ledger on append (tamper-evident causal chain).
    prev_entry_hash: Optional[str] = Field(default=None, pattern=HASH_PATTERN)
    entry_hash: Optional[str] = Field(default=None, pattern=HASH_PATTERN)

    @field_validator("timestamp_utc")
    @classmethod
    def _ts(cls, v: str) -> str:
        parse_utc(v)
        return v

    @model_validator(mode="after")
    def _consistency(self) -> "ProvenanceStamp":
        s, v = self.handoff_context.status, self.work_summary.verification_status
        if s == HandoffStatus.completed and v == VerificationStatus.verified_failed:
            raise ValueError("a completed stamp cannot carry verified_failed; use partial or reverted")
        if s in (HandoffStatus.blocked, HandoffStatus.reverted) and not self.handoff_context.failure_reason:
            raise ValueError(f"status {s.value} needs handoff_context.failure_reason (the dead-letter 'why')")
        return self

    def canonical(self, *, without_entry_hash: bool = True) -> str:
        """Deterministic JSON used for hashing (sorted keys, no whitespace)."""
        data = self.model_dump(mode="json", exclude={"entry_hash"} if without_entry_hash else set())
        import json

        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class Condition(_Strict):
    """A machine-checkable pre/postcondition (see contracts.evaluate)."""

    kind: Literal["file_exists", "file_absent", "file_hash_equals", "command_succeeds", "ledger_status_is", "no_drift"]
    target: str = Field(min_length=1, max_length=400)
    expected: Optional[str] = Field(default=None, max_length=400)
    description: str = Field(default="", max_length=240)


class Budget(_Strict):
    max_wall_seconds: int = Field(default=1800, ge=1, le=86400)
    max_tool_calls: int = Field(default=200, ge=1, le=100000)


class Escalation(_Strict):
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Below this self-rated confidence, stop and escalate")
    escalate_to: str = Field(default="orchestrator", max_length=64)
    always_escalate_tiers: list[CapabilityTier] = Field(default_factory=lambda: [CapabilityTier.external_side_effect])


class DelegationContract(_Strict):
    delegation_id: str = Field(default_factory=lambda: new_id("del"))
    parent_trace_id: Optional[str] = None
    issued_by: str = Field(pattern=_ID)
    issued_at_utc: str = Field(default_factory=utc_now_iso)
    assigned_role: str = Field(min_length=2, max_length=64)
    objective: str = Field(min_length=5, max_length=600)
    inputs: dict[str, Any] = Field(default_factory=dict)
    input_schema: Optional[dict[str, Any]] = Field(default=None, description="JSON Schema the inputs must satisfy")
    output_schema: Optional[dict[str, Any]] = Field(default=None, description="JSON Schema the worker's result must satisfy")
    allowed_targets: list[str] = Field(min_length=1, description="Glob patterns the worker may touch, e.g. 'apps/ops-panel/src/**'")
    max_capability_tier: CapabilityTier = CapabilityTier.mutate_shared
    preconditions: list[Condition] = Field(default_factory=list)
    postconditions: list[Condition] = Field(default_factory=list)
    definition_of_done: list[str] = Field(min_length=1)
    verification_commands: list[str] = Field(default_factory=list, description="Commands that must all exit 0 before commit")
    lease_ttl_seconds: int = Field(default=900, ge=30, le=86400)
    deadline_utc: Optional[str] = None
    budget: Budget = Field(default_factory=Budget)
    escalation: Escalation = Field(default_factory=Escalation)

    @field_validator("issued_at_utc", "deadline_utc")
    @classmethod
    def _ts(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            parse_utc(v)
        return v

    def allows(self, target_path: str) -> bool:
        from fnmatch import fnmatch

        return any(fnmatch(target_path, pat) for pat in self.allowed_targets)


class HandoffDirective(_Strict):
    directive_id: str = Field(default_factory=lambda: new_id("hd"))
    from_trace_id: str
    from_agent_id: str = Field(pattern=_ID)
    to_role: str = Field(min_length=2, max_length=64)
    target_uri: str = Field(min_length=1, max_length=400)
    instruction: str = Field(min_length=5, max_length=600)
    preconditions: list[Condition] = Field(default_factory=list)
    priority: Literal["p0", "p1", "p2"] = "p1"
    created_at_utc: str = Field(default_factory=utc_now_iso)
    deadline_utc: Optional[str] = None
