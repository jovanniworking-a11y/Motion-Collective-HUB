"""@track_agent_work: the Read-Before-Write / Stamp-On-Exit loop as a context manager and decorator.

    with track_agent_work("apps/ops-panel/src/lib/api.ts", agent=me, intent="Same-origin API base",
                          verify=["npm --prefix apps/ops-panel run -s typecheck"]) as work:
        print(work.briefing.to_prompt())          # step 1 + 2: prior work and hard constraints
        ... edit the file ...
        work.action("Switched apiBase() to same-origin in the browser")
        work.next("Re-run the e2e suite after the next deploy")
    # on exit (step 3): verify -> stamp inline breadcrumb -> append ledger, atomically

Failure handling
- Exception in the body      -> the file is restored byte-for-byte (compensating rollback) and a
                                 `reverted` stamp with the reason goes to the ledger + dead letter.
- Verification fails          -> on_verify_fail="revert" (default) restores and stamps `reverted`;
                                 "keep" leaves the change and stamps `partial`.
- Ledger write fails          -> the artifact is restored and StampWriteError is raised
                                 (no mutation without provenance).
- Idempotency key already done -> `work.already_done` is True; the body should return immediately.
"""
from __future__ import annotations

import contextvars
import functools
import inspect
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Sequence

from .breadcrumbs import apply_inline, comment_style
from .contracts import (
    ApprovalRequired,
    AuthorityExceeded,
    PostconditionFailed,
    PreconditionFailed,
    authorize,
    check_all,
    require_approval,
    validate_inputs,
)
from .hashing import content_hash_bytes
from .hydrate import HydrationBriefing, hydrate_agent_context
from .leases import LeaseManager
from .ledger import Ledger, find_repo_root
from .models import (
    AgentIdentity,
    CapabilityTier,
    DelegationContract,
    HandoffContext,
    HandoffStatus,
    ProvenanceStamp,
    Scope,
    SurfaceType,
    VerificationStatus,
    WorkSummary,
    new_id,
)
from .verify import VerificationResult, run_gate

_current_trace: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("agent_trace", default=None)


class StampWriteError(RuntimeError):
    """The provenance stamp could not be written; the artifact mutation was rolled back."""


class VerificationFailed(RuntimeError):
    """The verification gate failed and the change was rolled back (on_verify_fail='revert')."""


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class WorkSession:
    target_uri: str
    trace_id: str
    briefing: HydrationBriefing
    already_done: bool = False
    prior_stamp: Optional[ProvenanceStamp] = None
    actions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    dont_repeat: list[str] = field(default_factory=list)
    directives: list[str] = field(default_factory=list)
    _status_override: Optional[HandoffStatus] = None
    _reason: Optional[str] = None
    _post_bytes: Optional[bytes] = None
    _tool_calls: int = 0
    _max_tool_calls: int = 10**9
    result: Any = None

    # recording API used by the agent while it works
    def action(self, text: str) -> None:
        self.actions.append(text)

    def tool(self, name: str, summary: str) -> None:
        self._tool_calls += 1
        if self._tool_calls > self._max_tool_calls:
            raise BudgetExceeded(f"tool-call budget of {self._max_tool_calls} exhausted")
        self.actions.append(f"{name}: {summary}")

    def assume(self, text: str) -> None:
        self.assumptions.append(text)

    def do_not_repeat(self, text: str) -> None:
        self.dont_repeat.append(text)

    def next(self, text: str) -> None:
        self.directives.append(text)

    def mark_partial(self, reason: str) -> None:
        self._status_override, self._reason = HandoffStatus.partial, reason

    def mark_blocked(self, reason: str) -> None:
        self._status_override, self._reason = HandoffStatus.blocked, reason

    def set_post_state(self, content: bytes) -> None:
        """For non-file surfaces (db rows, tickets): hand over the new state so it can be hashed."""
        self._post_bytes = content


def _surface_for(target_path: str, explicit: Optional[SurfaceType]) -> SurfaceType:
    if explicit:
        return explicit
    if "://" in target_path:
        return SurfaceType.state_node
    return SurfaceType.doc_section if Path(target_path).suffix.lower() in {".md", ".markdown"} else SurfaceType.code_file


def _write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.agent-{os.getpid()}.tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _restore(path: Path, pre: Optional[bytes]) -> None:
    if pre is None:
        path.unlink(missing_ok=True)
    else:
        _write_atomic(path, pre)


@contextmanager
def track_agent_work(
    target_uri: str,
    *,
    agent: AgentIdentity,
    intent: str,
    repo_root: Optional[Path] = None,
    surface_type: Optional[SurfaceType] = None,
    contract: Optional[DelegationContract] = None,
    verify: Sequence[str] = (),
    capability_tier: CapabilityTier = CapabilityTier.mutate_shared,
    idempotency_key: Optional[str] = None,
    parent_trace_id: Optional[str] = None,
    pre_state: Optional[bytes] = None,
    on_verify_fail: str = "revert",
    inline: bool = True,
    lease_ttl: Optional[float] = None,
    dependencies: Sequence[str] = (),
    ledger: Optional[Ledger] = None,
) -> Iterator[WorkSession]:
    if on_verify_fail not in ("revert", "keep"):
        raise ValueError("on_verify_fail must be 'revert' or 'keep'")
    root = Path(repo_root) if repo_root else find_repo_root()
    led = ledger or Ledger(root)
    path_part = target_uri.split("#", 1)[0]
    is_file = "://" not in path_part
    path = root / path_part if is_file else None
    trace_id = new_id("tr")
    parent = parent_trace_id or _current_trace.get() or (contract.parent_trace_id if contract else None)
    surface = _surface_for(path_part, surface_type)
    started = time.monotonic()

    def stamp(status: HandoffStatus, verification: VerificationResult, pre_hash, post_hash, reason=None,
              session: Optional[WorkSession] = None) -> ProvenanceStamp:
        s = session
        return ProvenanceStamp(
            trace_id=trace_id, parent_trace_id=parent, delegation_id=contract.delegation_id if contract else None,
            idempotency_key=idempotency_key, capability_tier=capability_tier,
            agent=agent if not contract else agent.model_copy(update={"parent_delegation_id": contract.delegation_id}),
            scope=Scope(surface_type=surface, target_uri=target_uri, pre_state_hash=pre_hash, post_state_hash=post_hash),
            work_summary=WorkSummary(intent=intent, actions_taken=(s.actions if s else []),
                                     verification_status=verification.status, verification_evidence=verification.evidence),
            handoff_context=HandoffContext(status=status, assumptions_made=(s.assumptions if s else []),
                                           do_not_repeat=(s.dont_repeat if s else []),
                                           next_agent_directives=(s.directives if s else []), failure_reason=reason),
        )

    unverified = VerificationResult(VerificationStatus.unverified)

    # ---- authority, approval, contract preconditions: refuse early, record why
    try:
        authorize(contract, capability_tier, path_part)
        if contract:
            validate_inputs(contract)
        if capability_tier == CapabilityTier.external_side_effect:
            require_approval(root, idempotency_key)
        if contract and contract.preconditions:
            failed = [r for r in check_all(contract.preconditions, root, led) if not r.ok]
            if failed:
                raise PreconditionFailed("; ".join(r.detail for r in failed))
    except (AuthorityExceeded, ApprovalRequired, PreconditionFailed) as exc:
        led.append(stamp(HandoffStatus.blocked, unverified, None, None, reason=f"{exc.__class__.__name__}: {exc}"))
        raise

    # ---- idempotency: completed before -> hand back the prior stamp, do nothing
    if idempotency_key and (prior := led.find_idempotent(idempotency_key)):
        b = hydrate_agent_context(target_uri, repo_root=root, ledger=led, dependencies=dependencies)
        yield WorkSession(target_uri, prior.trace_id, b, already_done=True, prior_stamp=prior)
        return

    leases = LeaseManager(root)
    ttl = lease_ttl or (contract.lease_ttl_seconds if contract else 900)
    token = _current_trace.set(trace_id)
    try:
        with leases.held(path_part, agent.agent_id, ttl=ttl):
            briefing = hydrate_agent_context(target_uri, repo_root=root, ledger=led, dependencies=dependencies)
            pre_bytes = path.read_bytes() if (path and path.exists()) else pre_state
            pre_hash = content_hash_bytes(pre_bytes) if pre_bytes is not None else None
            session = WorkSession(target_uri, trace_id, briefing)
            if contract:
                session._max_tool_calls = contract.budget.max_tool_calls

            def rollback(reason: str, verification: VerificationResult) -> None:
                if path is not None:
                    _restore(path, pre_bytes)
                led.append(stamp(HandoffStatus.reverted, verification, pre_hash, pre_hash, reason=reason, session=session))

            try:
                yield session
            except BaseException as exc:  # noqa: BLE001 - every failure gets a compensating rollback + dead letter
                rollback(f"{exc.__class__.__name__}: {exc}"[:780], unverified)
                raise

            if contract and time.monotonic() - started > contract.budget.max_wall_seconds:
                session.mark_partial(f"wall-clock budget {contract.budget.max_wall_seconds}s exceeded")

            # ---- verification gate (deterministic, before commit)
            commands = [*(contract.verification_commands if contract else []), *verify]
            verification = run_gate(commands, cwd=root)
            post_failed = []
            if contract and contract.postconditions and verification.status != VerificationStatus.verified_failed:
                post_failed = [r for r in check_all(contract.postconditions, root, led) if not r.ok]
            if verification.status == VerificationStatus.verified_failed or post_failed:
                why = verification.evidence if not post_failed else "postconditions: " + "; ".join(r.detail for r in post_failed)
                if on_verify_fail == "revert":
                    rollback(f"verification failed: {why}"[:780], verification)
                    raise PostconditionFailed(why) if post_failed else VerificationFailed(why)
                session.mark_partial(f"verification failed, change kept: {why}"[:780])
                if verification.status != VerificationStatus.verified_failed:
                    verification = VerificationResult(VerificationStatus.verified_failed, verification.checks)

            # ---- post state
            if path is not None:
                post_bytes = path.read_bytes() if path.exists() else None
            else:
                post_bytes = session._post_bytes
            post_hash = content_hash_bytes(post_bytes) if post_bytes is not None else None

            status = session._status_override or HandoffStatus.completed
            if status == HandoffStatus.completed and verification.status == VerificationStatus.verified_failed:
                status = HandoffStatus.partial
            final = stamp(status, verification, pre_hash, post_hash, reason=session._reason, session=session)

            # ---- step 3: atomic commit of artifact breadcrumb + ledger entry
            style = comment_style(path) if (path is not None and inline and post_bytes is not None) else None
            stamped_bytes = None
            if style:
                try:
                    text = post_bytes.decode("utf-8")
                    prev_text = pre_bytes.decode("utf-8", errors="replace") if pre_bytes is not None else None
                    stamped_bytes = apply_inline(text, final, style, previous=prev_text).encode("utf-8")
                except UnicodeDecodeError:
                    stamped_bytes = None
            try:
                if stamped_bytes is not None:
                    _write_atomic(path, stamped_bytes)
                session.prior_stamp = led.append(final)
            except BaseException as exc:  # noqa: BLE001
                if path is not None:
                    _restore(path, pre_bytes)
                raise StampWriteError(f"stamp write failed, mutation rolled back: {exc}") from exc
    finally:
        _current_trace.reset(token)


def agent_work(target_uri: Optional[str] = None, *, target_arg: Optional[str] = None, **kw) -> Callable:
    """Decorator form. The wrapped function may accept `work` to record actions; returns its result,
    or the prior stamp when the idempotency key was already completed.

        @agent_work("orch/tasks/BOARD.md", agent=me, intent="Update RSVP line", idempotency_key="rsvp-2026-10-24")
        def update(work): ...
    """
    def deco(fn: Callable) -> Callable:
        wants_work = "work" in inspect.signature(fn).parameters

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            uri = target_uri or (kwargs.get(target_arg) if target_arg else None)
            if uri is None and target_arg:
                uri = inspect.signature(fn).bind_partial(*args, **kwargs).arguments.get(target_arg)
            if not uri:
                raise ValueError("agent_work needs target_uri or target_arg")
            with track_agent_work(uri, **kw) as work:
                if work.already_done:
                    return work.prior_stamp
                result = fn(*args, work=work, **kwargs) if wants_work else fn(*args, **kwargs)
                work.result = result
            return result

        return wrapper

    return deco
