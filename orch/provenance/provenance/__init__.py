# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_e216c583dcfc4b47]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""MOTION Universal Agent Work Provenance (v1.0).

Read before write, stamp on exit. See orch/provenance/ARCHITECTURE.md and WORKER_PROMPT.md.
"""
from .breadcrumbs import commit_trailers, format_trailers, parse_trailers, read_inline
from .contracts import (
    ApprovalRequired,
    AuthorityExceeded,
    ContractViolation,
    PostconditionFailed,
    PreconditionFailed,
)
from .hashing import content_hash_bytes, content_hash_text, file_content_hash, strip_provenance
from .hydrate import HydrateAgentContext, HydrationBriefing, hydrate_agent_context, rolling_state_summary
from .leases import Lease, LeaseConflict, LeaseManager, StaleWrite
from .coverage import CoverageReport, changed_files, check_coverage
from .privacy import find_guest_names
from .registry import Registry
from .remote import LeaseServiceError, RemoteLeaseManager, lease_manager_for
from .ledger import ChainReport, Ledger, LedgerError
from .models import (
    PROVENANCE_VERSION,
    AgentIdentity,
    Budget,
    CapabilityTier,
    Condition,
    DelegationContract,
    Escalation,
    HandoffContext,
    HandoffDirective,
    HandoffStatus,
    ProvenanceStamp,
    Scope,
    SurfaceType,
    VerificationStatus,
    WorkSummary,
    utc_now_iso,
)
from .tracker import StampWriteError, VerificationFailed, WorkSession, agent_work, track_agent_work
from .verify import VerificationResult, run_gate

__all__ = [name for name in dir() if not name.startswith("_")]
