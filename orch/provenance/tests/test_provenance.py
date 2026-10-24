# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_42acd449ed8244ae]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from provenance import (
    AgentIdentity,
    ApprovalRequired,
    AuthorityExceeded,
    CapabilityTier,
    Condition,
    DelegationContract,
    HandoffStatus,
    LeaseConflict,
    LeaseManager,
    Ledger,
    PreconditionFailed,
    StaleWrite,
    StampWriteError,
    VerificationFailed,
    VerificationStatus,
    agent_work,
    content_hash_text,
    file_content_hash,
    hydrate_agent_context,
    parse_trailers,
    read_inline,
    rolling_state_summary,
    strip_provenance,
    track_agent_work,
)
from provenance.__main__ import export_schemas, main as cli
from provenance.breadcrumbs import apply_inline, check_commit_message, format_trailers
from provenance.db import record_db_work, shadow_columns_ddl
from provenance.models import GENESIS_HASH, ProvenanceStamp

PY_OK = f"{sys.executable} -c 'import sys; sys.exit(0)'"
PY_FAIL = f"{sys.executable} -c 'import sys; print(\"2 failed\"); sys.exit(1)'"


def write(repo: Path, rel: str, body: str) -> Path:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    return p


# ---------------------------------------------------------------- happy path + breadcrumbs
def test_stamp_on_exit_writes_inline_block_and_ledger(repo, me):
    p = write(repo, "src/pay.py", '"""Payments."""\nimport time\n')
    with track_agent_work("src/pay.py", agent=me, intent="Extract retry backoff", repo_root=repo, verify=[PY_OK]) as w:
        p.write_text('"""Payments."""\nimport time\n\ndef backoff(n):\n    return 2 ** n\n')
        w.action("Added exponential backoff helper")
        w.do_not_repeat("Do not use synchronous urllib3 Retry here")
        w.next("Cover backoff() in tests")
    text_now = p.read_text()
    lines = text_now.splitlines()
    assert lines[0].startswith("# @agent-provenance [") and "[status:completed/verified_passed]" in lines[0]
    assert lines[1].startswith("# @summary: Extract retry backoff") and lines[2].startswith("# @handoff: Cover backoff()")
    assert strip_provenance(text_now).startswith('"""Payments."""')
    (stamp,) = Ledger(repo).iter_entries()
    assert stamp.scope.post_state_hash == file_content_hash(p)      # breadcrumb is hash-neutral
    assert stamp.scope.pre_state_hash != stamp.scope.post_state_hash
    assert stamp.work_summary.verification_status == VerificationStatus.verified_passed
    assert stamp.prev_entry_hash == GENESIS_HASH and stamp.entry_hash.startswith("sha256:")
    assert read_inline(text_now)["trace"] == stamp.trace_id


def test_restamp_replaces_block_not_appends(repo, me):
    p = write(repo, "src/a.ts", '"use client";\nexport const x = 1;\n')
    for n in (2, 3):
        with track_agent_work("src/a.ts", agent=me, intent=f"bump x to {n}", repo_root=repo):
            p.write_text(strip_provenance(p.read_text()).replace(f"x = {n-1}", f"x = {n}"))
    t = p.read_text()
    assert t.count("@agent-provenance") == 1 and t.splitlines()[0].startswith("// @agent-provenance")
    assert '"use client";' in t.splitlines()[3]
    assert len(list(Ledger(repo).iter_entries())) == 2


def test_shebang_doctype_and_css_placement(repo, me):
    sh = write(repo, "run.sh", "#!/bin/sh\necho hi\n")
    html = write(repo, "page.html", "<!doctype html>\n<html></html>\n")
    css = write(repo, "s.css", "a{color:red}\n")
    for p in (sh, html, css):
        rel = p.relative_to(repo).as_posix()
        with track_agent_work(rel, agent=me, intent=f"touch {rel}", repo_root=repo):
            p.write_text(p.read_text() + "\n")
    assert sh.read_text().startswith("#!/bin/sh\n# @agent-provenance")
    assert html.read_text().lower().startswith("<!doctype html>\n<!-- @agent-provenance")
    assert css.read_text().startswith("/* @agent-provenance") and " */\n" in css.read_text()
    for p in (sh, html, css):
        assert strip_provenance(p.read_text()).strip().endswith(p.read_text().strip().splitlines()[-1])


def test_markdown_worklog_rows_and_hash_neutral(repo, me):
    p = write(repo, "docs/spec.md", "# Spec\n\nBody.\n")
    for n in range(12):
        with track_agent_work("docs/spec.md", agent=me, intent=f"edit {n}", repo_root=repo):
            p.write_text(strip_provenance(p.read_text()) + f"line {n}\n")
    t = p.read_text()
    assert t.count("<!-- AGENT_WORKLOG:BEGIN -->") == 1 and "<!-- AGENT_LOG {" in t
    rows = [l for l in t.splitlines() if l.startswith("| 20")]
    assert len(rows) == 10 and "edit 11" in rows[0]                      # newest first, capped
    last = list(Ledger(repo).iter_entries())[-1]
    assert file_content_hash(p) == last.scope.post_state_hash
    assert json.loads(t.split("<!-- AGENT_LOG ")[1].split(" -->")[0])["trace"] == last.trace_id


def test_json_gets_ledger_only(repo, me):
    p = write(repo, "cfg.json", '{"a": 1}\n')
    with track_agent_work("cfg.json", agent=me, intent="set a=2", repo_root=repo):
        p.write_text('{"a": 2}\n')
    assert p.read_text() == '{"a": 2}\n'
    assert len(list(Ledger(repo).iter_entries())) == 1


# ---------------------------------------------------------------- failure recovery
def test_exception_rolls_back_and_dead_letters(repo, me):
    p = write(repo, "src/b.py", "x = 1\n")
    with pytest.raises(ZeroDivisionError):
        with track_agent_work("src/b.py", agent=me, intent="risky change", repo_root=repo) as w:
            p.write_text("x = 2\n")
            w.do_not_repeat("Dividing by the guest count crashes when the door list is empty")
            1 / 0
    assert p.read_text() == "x = 1\n"
    (s,) = Ledger(repo).iter_entries()
    assert s.handoff_context.status == HandoffStatus.reverted and "ZeroDivisionError" in s.handoff_context.failure_reason
    dl = (repo / ".agent" / "dead_letter.jsonl").read_text()
    assert "risky change" in dl and "door list is empty" in dl


def test_new_file_removed_on_rollback(repo, me):
    with pytest.raises(RuntimeError):
        with track_agent_work("src/new.py", agent=me, intent="create file", repo_root=repo):
            write(repo, "src/new.py", "y = 1\n")
            raise RuntimeError("boom")
    assert not (repo / "src/new.py").exists()


def test_verification_failure_reverts_by_default(repo, me):
    p = write(repo, "src/c.py", "ok = True\n")
    with pytest.raises(VerificationFailed):
        with track_agent_work("src/c.py", agent=me, intent="break it", repo_root=repo, verify=[PY_FAIL]):
            p.write_text("ok = False\n")
    assert p.read_text() == "ok = True\n"
    s = list(Ledger(repo).iter_entries())[-1]
    assert s.handoff_context.status == HandoffStatus.reverted
    assert s.work_summary.verification_status == VerificationStatus.verified_failed
    assert "rc=1" in s.work_summary.verification_evidence


def test_verification_failure_keep_marks_partial(repo, me):
    p = write(repo, "src/d.py", "a = 1\n")
    with track_agent_work("src/d.py", agent=me, intent="wip", repo_root=repo, verify=[PY_FAIL], on_verify_fail="keep"):
        p.write_text("a = 2\n")
    s = list(Ledger(repo).iter_entries())[-1]
    assert s.handoff_context.status == HandoffStatus.partial and "a = 2" in p.read_text()


def test_ledger_failure_rolls_back_the_mutation(repo, me, monkeypatch):
    p = write(repo, "src/e.py", "v = 1\n")

    def boom(self, stamp):
        raise OSError("disk full")

    monkeypatch.setattr(Ledger, "append", boom)
    with pytest.raises(StampWriteError):
        with track_agent_work("src/e.py", agent=me, intent="change v", repo_root=repo):
            p.write_text("v = 2\n")
    assert p.read_text() == "v = 1\n"


def test_idempotency_key_skips_completed_work(repo, me):
    p = write(repo, "board.md", "# Board\n")
    calls = []

    @agent_work("board.md", agent=me, intent="add RSVP line", repo_root=repo, idempotency_key="rsvp-2026-10-24")
    def update(work):
        calls.append(1)
        p.write_text(strip_provenance(p.read_text()) + "RSVPs: 20\n")
        return "done"

    assert update() == "done"
    again = update()
    assert isinstance(again, ProvenanceStamp) and len(calls) == 1
    assert strip_provenance(p.read_text()).count("RSVPs: 20") == 1


# ---------------------------------------------------------------- authority + contracts
def test_external_side_effect_needs_human_approval(repo, me):
    with pytest.raises(ApprovalRequired):
        with track_agent_work("zazzle://order/matchbox", agent=me, intent="order matchboxes", repo_root=repo,
                              capability_tier=CapabilityTier.external_side_effect, idempotency_key="order-matchbox-100"):
            pytest.fail("body must not run")
    assert list(Ledger(repo).iter_entries())[-1].handoff_context.status == HandoffStatus.blocked


def test_external_side_effect_runs_with_approval(repo, me):
    appr = repo / ".agent" / "approvals"
    appr.mkdir(parents=True)
    (appr / "order-1.json").write_text(json.dumps({"approved_by": "jovanni", "approved_at_utc": "2026-10-24T12:00:00.000Z"}))
    with track_agent_work("zazzle://order/1", agent=me, intent="place approved order", repo_root=repo,
                          capability_tier=CapabilityTier.external_side_effect, idempotency_key="order-1") as w:
        w.set_post_state(b'{"order":"placed"}')
    s = list(Ledger(repo).iter_entries())[-1]
    assert s.handoff_context.status == HandoffStatus.completed and s.scope.post_state_hash


def test_contract_scope_and_preconditions(repo, me):
    write(repo, "apps/x.ts", "export {}\n")
    c = DelegationContract(issued_by="claude-code", assigned_role="frontend", objective="Touch only apps/",
                           allowed_targets=["apps/**"], definition_of_done=["typecheck passes"],
                           preconditions=[Condition(kind="file_exists", target="apps/x.ts")],
                           max_capability_tier=CapabilityTier.mutate_shared)
    with pytest.raises(AuthorityExceeded):
        with track_agent_work("services/api/main.py", agent=me, intent="out of scope", repo_root=repo, contract=c):
            pass
    bad = c.model_copy(update={"preconditions": [Condition(kind="file_exists", target="apps/missing.ts")]})
    with pytest.raises(PreconditionFailed):
        with track_agent_work("apps/x.ts", agent=me, intent="needs missing file", repo_root=repo, contract=bad):
            pass
    with track_agent_work("apps/x.ts", agent=me, intent="in scope", repo_root=repo, contract=c) as w:
        (repo / "apps/x.ts").write_text("export const y = 1;\n")
    s = list(Ledger(repo).iter_entries())[-1]
    assert s.delegation_id == c.delegation_id and s.agent.parent_delegation_id == c.delegation_id


def test_nested_work_links_parent_trace(repo, me):
    write(repo, "a.py", "a=1\n"); write(repo, "b.py", "b=1\n")
    with track_agent_work("a.py", agent=me, intent="outer", repo_root=repo) as outer:
        with track_agent_work("b.py", agent=me, intent="inner", repo_root=repo) as inner:
            (repo / "b.py").write_text("b=2\n")
        (repo / "a.py").write_text("a=2\n")
    by_intent = {s.work_summary.intent: s for s in Ledger(repo).iter_entries()}
    assert by_intent["inner"].parent_trace_id == by_intent["outer"].trace_id


def test_guest_data_is_refused(repo, me):
    write(repo, "n.md", "x\n")
    with pytest.raises(Exception):
        with track_agent_work("n.md", agent=me, intent="Text guest at 512-555-0199", repo_root=repo):
            pass


# ---------------------------------------------------------------- leases
def test_lease_conflict_expiry_and_stale_write(repo):
    lm = LeaseManager(repo)
    a = lm.acquire("src/x.py", "agent-a", ttl=0.3)
    with pytest.raises(LeaseConflict):
        lm.acquire("src/x.py", "agent-b", ttl=5)
    time.sleep(0.35)
    b = lm.acquire("src/x.py", "agent-b", ttl=5)          # expired -> takeover
    with pytest.raises(LeaseConflict):
        lm.heartbeat(a)                                     # a lost it
    lm.release(b)
    p = write(repo, "src/x.py", "v=1\n")
    with pytest.raises(StaleWrite):
        lm.acquire("src/x.py", "agent-c", expected_hash=content_hash_text("v=0\n"), file_path=p)


def test_lease_blocks_concurrent_tracked_work(repo, me):
    write(repo, "src/y.py", "y=1\n")
    other = AgentIdentity(agent_id="other-agent", role="qa", session_id="sess_2")
    with track_agent_work("src/y.py", agent=me, intent="hold lease", repo_root=repo):
        with pytest.raises(LeaseConflict):
            with track_agent_work("src/y.py", agent=other, intent="collide", repo_root=repo):
                pass


# ---------------------------------------------------------------- hydration + drift
def test_hydrate_brief_constraints_and_drift(repo, me):
    p = write(repo, "src/z.py", "z=1\n")
    with pytest.raises(ValueError):
        with track_agent_work("src/z.py", agent=me, intent="first try", repo_root=repo) as w:
            w.do_not_repeat("Do not cache the door count in memory")
            raise ValueError("cache went stale")
    with track_agent_work("src/z.py", agent=me, intent="second try", repo_root=repo) as w:
        p.write_text(strip_provenance(p.read_text()) + "z=2\n")
        w.assume("The API answers within 2 s")
        w.next("Add a test for z=2")
    b = hydrate_agent_context("src/z.py", repo_root=repo)
    assert b.integrity == "ok" and len(b.entries) == 2
    prompt = b.to_prompt()
    assert prompt.startswith('<prior_agent_work target="src/z.py" entries="2" integrity="ok">')
    assert "DO NOT: Do not cache the door count in memory" in prompt and "FAILED BEFORE" in prompt
    assert "Add a test for z=2" in prompt and "The API answers within 2 s" in prompt
    p.write_text(p.read_text() + "hand_edit = True\n")       # unlogged human edit
    assert hydrate_agent_context("src/z.py", repo_root=repo).integrity == "DRIFT"
    assert len(hydrate_agent_context("src/z.py", repo_root=repo).to_prompt(max_chars=400)) <= 400


def test_rolling_state_summary(repo, me):
    write(repo, "a.py", "a=1\n")
    with track_agent_work("a.py", agent=me, intent="first", repo_root=repo) as w:
        w.next("follow up")
    s = rolling_state_summary(Ledger(repo))
    assert "`a.py`" in s and "follow up" in s


# ---------------------------------------------------------------- ledger integrity
def test_chain_detects_edits_and_deletions(repo, me):
    for i in range(3):
        write(repo, f"f{i}.py", "x=1\n")
        with track_agent_work(f"f{i}.py", agent=me, intent=f"work {i}", repo_root=repo):
            (repo / f"f{i}.py").write_text("x=2\n")
    led = Ledger(repo)
    assert led.verify_chain().ok
    lines = led.path.read_text().splitlines()
    led.path.write_text("\n".join([lines[0], lines[1].replace("work 1", "work one"), lines[2]]) + "\n")
    rep = led.verify_chain()
    assert not rep.ok and "entry_hash mismatch" in rep.problems[0]
    led.path.write_text("\n".join([lines[0], lines[2]]) + "\n")        # delete the middle entry
    rep = led.verify_chain()
    assert not rep.ok and "missing or later entry" in rep.problems[0]


def test_union_merge_fork_is_valid(repo, me):
    write(repo, "a.py", "a=1\n")
    with track_agent_work("a.py", agent=me, intent="base", repo_root=repo):
        (repo / "a.py").write_text("a=2\n")
    led = Ledger(repo)
    base = led.path.read_text()
    # simulate two branches appending after the same parent, then git's union merge
    with track_agent_work("a.py", agent=me, intent="branch one", repo_root=repo):
        (repo / "a.py").write_text("a=3\n")
    one = led.path.read_text().splitlines()[-1]
    led.path.write_text(base)
    with track_agent_work("a.py", agent=me, intent="branch two", repo_root=repo):
        (repo / "a.py").write_text("a=4\n")
    led.path.write_text(led.path.read_text() + one + "\n")
    rep = led.verify_chain()
    assert rep.ok and rep.forks == 1


# ---------------------------------------------------------------- git + db surfaces
def test_git_trailers_roundtrip_and_hook(repo, me):
    write(repo, "a.py", "a=1\n")
    with track_agent_work("a.py", agent=me, intent="trailer test", repo_root=repo) as w:
        (repo / "a.py").write_text("a=2\n")
        w.next("ship it")
    s = list(Ledger(repo).iter_entries())[-1]
    msg = f"Change a\n\nBody\n\n{format_trailers(s)}\n"
    tr = parse_trailers(msg)
    assert tr["Agent-Trace"] == s.trace_id and tr["Agent-Next-Step"] == "ship it"
    assert check_commit_message(msg) == []
    assert check_commit_message("human commit\n") == []
    assert "missing trailer Agent-Trace" in check_commit_message("x\n\nAgent-Id: a\nAgent-Timestamp: 2026-10-24T00:00:00.000Z\nAgent-Summary: s\n")


def test_db_outbox_and_shadow_columns_same_transaction(repo, me):
    eng = create_engine(f"sqlite:///{repo / 'db.sqlite3'}")
    with eng.begin() as conn:
        conn.execute(text("CREATE TABLE sim_runs (id INTEGER PRIMARY KEY, score REAL)"))
        for stmt in shadow_columns_ddl("sim_runs", "sqlite"):
            conn.execute(text(stmt))
        conn.execute(text("INSERT INTO sim_runs (id, score) VALUES (42, 0.5)"))
    with track_agent_work("db://motion/sim_runs/42", agent=me, intent="rescore run 42", repo_root=repo) as w:
        with eng.begin() as conn:
            conn.execute(text("UPDATE sim_runs SET score = 0.9 WHERE id = 42"))
            w.set_post_state(b"score=0.9")
    s = list(Ledger(repo).iter_entries())[-1]
    with eng.begin() as conn:
        record_db_work(conn, s, table="sim_runs", pk_column="id", pk_value=42)
        row = conn.execute(text("SELECT last_agent_id, last_agent_trace_id FROM sim_runs WHERE id=42")).one()
        assert row == (me.agent_id, s.trace_id)
        assert conn.execute(text("SELECT count(*) FROM agent_work_ledger")).scalar() == 1
    # a missing row aborts the whole transaction (no business write without its stamp)
    with pytest.raises(LookupError):
        with eng.begin() as conn:
            conn.execute(text("UPDATE sim_runs SET score = 0.1 WHERE id = 42"))
            record_db_work(conn, s.model_copy(update={"stamp_id": "stp_other"}), table="sim_runs", pk_column="id", pk_value=999)
    with eng.begin() as conn:
        assert conn.execute(text("SELECT score FROM sim_runs WHERE id=42")).scalar() == 0.9


# ---------------------------------------------------------------- schemas + CLI
def test_exported_json_schemas_validate_real_stamps(repo, me):
    import jsonschema

    paths = export_schemas(repo / "schema")
    stamp_schema = json.loads((repo / "schema" / "provenance-stamp.schema.json").read_text())
    assert stamp_schema["$schema"] == "https://json-schema.org/draft/2020-12/schema" and len(paths) == 3
    write(repo, "a.py", "a=1\n")
    with track_agent_work("a.py", agent=me, intent="schema check", repo_root=repo):
        (repo / "a.py").write_text("a=2\n")
    raw = json.loads(Ledger(repo).path.read_text().splitlines()[-1])
    jsonschema.Draft202012Validator(stamp_schema).validate(raw)


def test_cli_stamp_for_non_python_agents(repo, monkeypatch, capsys):
    monkeypatch.chdir(repo)
    write(repo, "apps/page.tsx", "export default function P() { return null }\n")
    rc = cli(["stamp", "--target", "apps/page.tsx", "--agent-id", "cursor", "--role", "frontend",
              "--session", "s1", "--intent", "Empty page component", "--action", "Added P()",
              "--verify", PY_OK, "--next", "Wire it into the nav"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "completed" and out["verification"] == "verified_passed"
    assert (repo / "apps/page.tsx").read_text().startswith("// @agent-provenance")
    assert cli(["verify-chain"]) == 0
    assert cli(["hydrate", "apps/page.tsx"]) == 0
    assert "Wire it into the nav" in capsys.readouterr().out
