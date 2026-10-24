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
