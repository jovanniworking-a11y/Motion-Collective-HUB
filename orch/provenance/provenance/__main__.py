"""CLI for agents that can't import Python (Cursor, Grok, Codex, shell scripts).

    python3 orch/provenance/agent.py hydrate apps/ops-panel/src/lib/api.ts
    python3 orch/provenance/agent.py stamp --target apps/ops-panel/src/lib/api.ts --agent-id cursor --role code-builder \
        --session s1 --intent "Same-origin API base" --action "apiBase() returns '' in the browser" \
        --verify "npm --prefix apps/ops-panel run -s typecheck" --next "Re-run e2e after deploy"
    python3 orch/provenance/agent.py verify-chain
    python3 orch/provenance/agent.py state            # writes .agent/STATE.md
    python3 orch/provenance/agent.py trailers <trace_id>
    python3 orch/provenance/agent.py check-commit-msg .git/COMMIT_EDITMSG
    python3 orch/provenance/agent.py schema --out orch/provenance/schema
    python3 orch/provenance/agent.py approve <key> --by jovanni --scope "order 100 matchboxes"   (humans only)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .breadcrumbs import apply_inline, check_commit_message, comment_style, format_trailers
from .contracts import approval_path
from .hashing import content_hash_bytes
from .hydrate import hydrate_agent_context, rolling_state_summary
from .ledger import Ledger, find_repo_root
from .models import (
    AgentIdentity,
    CapabilityTier,
    DelegationContract,
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
from .verify import run_gate

SCHEMA_ID = "https://motion-collective.local/schemas/provenance/{name}.schema.json"


def export_schemas(out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, model in (("provenance-stamp", ProvenanceStamp), ("delegation-contract", DelegationContract),
                        ("handoff-directive", HandoffDirective)):
        schema = model.model_json_schema(mode="serialization")
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": SCHEMA_ID.format(name=name), **schema}
        p = out / f"{name}.schema.json"
        p.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
        written.append(p)
    return written


def cmd_stamp(a, root: Path) -> int:
    """After-the-fact stamp for agents that edited a file themselves. Pre-state = last stamped hash."""
    led = Ledger(root)
    path_part = a.target.split("#", 1)[0]
    p = root / path_part
    brief = hydrate_agent_context(a.target, repo_root=root, ledger=led, last_n=1)
    pre_hash = brief.last_stamped_hash
    verification = run_gate(a.verify or [], cwd=root)
    status = HandoffStatus(a.status) if a.status else (
        HandoffStatus.partial if verification.status == VerificationStatus.verified_failed else HandoffStatus.completed)
    if status == HandoffStatus.completed and verification.status == VerificationStatus.verified_failed:
        status = HandoffStatus.partial
    post_bytes = p.read_bytes() if p.is_file() else None
    stamp = ProvenanceStamp(
        parent_trace_id=a.parent_trace, idempotency_key=a.idempotency_key,
        capability_tier=CapabilityTier(a.tier),
        agent=AgentIdentity(agent_id=a.agent_id, role=a.role, session_id=a.session),
        scope=Scope(surface_type=SurfaceType(a.surface) if a.surface else (SurfaceType.doc_section if path_part.endswith(".md") else SurfaceType.code_file),
                    target_uri=a.target, pre_state_hash=pre_hash,
                    post_state_hash=content_hash_bytes(post_bytes) if post_bytes is not None else None),
        work_summary=WorkSummary(intent=a.intent, actions_taken=a.action or [], verification_status=verification.status,
                                 verification_evidence=verification.evidence),
        handoff_context=HandoffContext(status=status, assumptions_made=a.assume or [], do_not_repeat=a.dont or [],
                                       next_agent_directives=a.next or [], failure_reason=a.reason),
    )
    original = post_bytes
    style = comment_style(p) if (post_bytes is not None and not a.no_inline) else None
    try:
        if style:
            p.write_text(apply_inline(post_bytes.decode("utf-8"), stamp, style), encoding="utf-8")
        stamped = led.append(stamp)
    except Exception:
        if style and original is not None:
            p.write_bytes(original)
        raise
    print(json.dumps({"trace_id": stamped.trace_id, "status": status.value,
                      "verification": verification.status.value, "drift_before": brief.integrity == "DRIFT"}))
    return 0 if verification.status != VerificationStatus.verified_failed else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="agent", description="MOTION agent provenance")
    sub = ap.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("hydrate"); h.add_argument("target"); h.add_argument("-n", type=int, default=5)
    h.add_argument("--dep", action="append", default=[]); h.add_argument("--max-chars", type=int, default=1800)

    s = sub.add_parser("stamp")
    s.add_argument("--target", required=True); s.add_argument("--agent-id", required=True); s.add_argument("--role", required=True)
    s.add_argument("--session", required=True); s.add_argument("--intent", required=True)
    s.add_argument("--action", action="append"); s.add_argument("--assume", action="append")
    s.add_argument("--dont", action="append", help="do-not-repeat note"); s.add_argument("--next", action="append")
    s.add_argument("--verify", action="append"); s.add_argument("--status", choices=[x.value for x in HandoffStatus])
    s.add_argument("--reason"); s.add_argument("--surface", choices=[x.value for x in SurfaceType])
    s.add_argument("--tier", default="mutate_shared", choices=[x.value for x in CapabilityTier])
    s.add_argument("--parent-trace"); s.add_argument("--idempotency-key"); s.add_argument("--no-inline", action="store_true")

    sub.add_parser("verify-chain")
    st = sub.add_parser("state"); st.add_argument("--out", default=".agent/STATE.md")
    t = sub.add_parser("trailers"); t.add_argument("trace_id")
    c = sub.add_parser("check-commit-msg"); c.add_argument("file")
    sc = sub.add_parser("schema"); sc.add_argument("--out", default="orch/provenance/schema")
    apv = sub.add_parser("approve"); apv.add_argument("key"); apv.add_argument("--by", required=True); apv.add_argument("--scope", required=True)

    a = ap.parse_args(argv)
    root = find_repo_root()
    if a.cmd == "hydrate":
        print(hydrate_agent_context(a.target, repo_root=root, last_n=a.n, dependencies=a.dep).to_prompt(a.max_chars))
        return 0
    if a.cmd == "stamp":
        return cmd_stamp(a, root)
    if a.cmd == "verify-chain":
        rep = Ledger(root).verify_chain()
        print(json.dumps({"ok": rep.ok, "entries": rep.entries, "forks": rep.forks, "problems": rep.problems}, indent=2))
        return 0 if rep.ok else 1
    if a.cmd == "state":
        out = root / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rolling_state_summary(Ledger(root)))
        print(out.relative_to(root))
        return 0
    if a.cmd == "trailers":
        hits = [s for s in Ledger(root).iter_entries() if s.trace_id == a.trace_id]
        if not hits:
            print(f"no ledger entry with trace {a.trace_id}", file=sys.stderr)
            return 1
        print(format_trailers(hits[-1]))
        return 0
    if a.cmd == "check-commit-msg":
        problems = check_commit_message(Path(a.file).read_text())
        for p in problems:
            print(f"agent-provenance: {p}", file=sys.stderr)
        return 1 if problems else 0
    if a.cmd == "schema":
        for p in export_schemas(root / a.out):
            print(p.relative_to(root))
        return 0
    if a.cmd == "approve":
        p = approval_path(root, a.key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"approved_by": a.by, "approved_at_utc": utc_now_iso(), "scope": a.scope}, indent=2) + "\n")
        print(p.relative_to(root))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
