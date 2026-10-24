# Universal Agent Work Provenance · architecture (v1.0, 24 Oct 2026)

Every place an agent reads, changes or runs work carries a machine-readable, time-ordered stamp. The next agent can rebuild context, check preconditions and keep going without a human handoff.

Code: `orch/provenance/provenance/` (Python 3.12+, pydantic v2). CLI: `python3 orch/provenance/agent.py`. Schemas: `orch/provenance/schema/`. Tests: `orch/provenance/tests/` (run in CI).

## 1. System design

```mermaid
sequenceDiagram
    participant J as Jovanni (approvals only)
    participant O as Orchestrator (Claude Code front door)
    participant W as Worker agent (code / research / QA / ops)
    participant L as Lease manager (.agent/leases)
    participant H as Hydrator (HydrateAgentContext)
    participant V as Verification gate (CI commands)
    participant P as Provenance ledger (.agent/ledger.jsonl)

    O->>W: DelegationContract (objective, allowed_targets, tier, pre/postconditions, DoD, verify cmds, budget)
    W->>W: authorize(tier, target) + validate inputs
    alt tier = external_side_effect
        W->>J: needs .agent/approvals/<key>.json (spend / send / post / publish)
    end
    W->>L: acquire lease(target, ttl) + heartbeat
    W->>H: read-before-write (stamps on target + deps)
    H-->>W: <prior_agent_work> briefing, hard constraints, open directives, DRIFT flag
    W->>W: do the work (record actions, assumptions, do_not_repeat, next steps)
    W->>V: run verification commands + postconditions
    alt verification failed
        W->>W: compensating rollback (restore bytes)
        W->>P: reverted stamp + dead letter (why it failed)
    else passed
        W->>W: write inline breadcrumb (atomic replace)
        W->>P: append chained stamp (fsync); on failure, restore artifact
    end
    W->>L: release lease
    W-->>O: stamp + trace_id; commit carries Agent-* trailers
    O->>P: rolling STATE.md (compaction) for the next delegation
```

**Components**

| Component | File | Role |
|---|---|---|
| Orchestrator | this Claude Code session | Splits asks, issues `DelegationContract`s, reviews stamps, merges green PRs |
| Worker | any agent (Claude Code child session, Cursor, Codex, Grok, scripts) | Does one contract. Python agents use `track_agent_work`; others use the CLI `stamp` |
| Lease manager | `leases.py`, `remote.py` | O_EXCL lease files (one host) or the shared API lease table (`MOTION_LEASE_URL`), TTL + heartbeat thread, takeover after expiry, `StaleWrite` on an ETag (content hash) mismatch |
| Hydrator | `hydrate.py` | Read-before-write briefing, integrity check (`ok` / `DRIFT` / `untracked` / `external`), rolling state summary |
| Verification gate | `verify.py`, `contracts.py` | Commands must exit 0 and postconditions must hold; otherwise roll back or mark partial |
| Ledger | `ledger.py` | Append-only JSONL, hash-chained, union-mergeable, dead-letter file, idempotency lookup |
| Surface adapters | `breadcrumbs.py`, `db.py` | Inline blocks, Markdown work log, git trailers, DB outbox + shadow columns |

## 2. Closing the seven autonomy gaps

| Pillar | Mechanism here | Where |
|---|---|---|
| 1. Shared episodic + semantic state | Ledger holds every stamp. Inline breadcrumbs point at it by `trace_id`. `STATE.md` is the rolling summary. | `ledger.py`, `breadcrumbs.py`, `agent.py state` |
| 2. Delegation contracts | `DelegationContract`: JSON-Schema inputs and outputs, `allowed_targets` globs, typed `Condition` pre/postconditions, Definition of Done, verification commands, budget, deadline | `models.py`, `contracts.py` |
| 3. Concurrency + leases | Per-target lease with TTL and heartbeat. Loss of a lease is detected. Optimistic concurrency via `expected_hash` (ETag = content hash). | `leases.py` |
| 4. Deterministic verification | Gate runs real commands (pytest, tsc, link and hygiene checks). Stamps carry the evidence (`rc`, time, last output line). `completed` + `verified_failed` is rejected by the schema. | `verify.py`, `models.py` |
| 5. Bounded authority | Tiers `read < sandbox_write < mutate_shared < external_side_effect`. A contract caps the tier. External side effects need a human approval file (house rule: never spend / send / post without Jovanni). Escalation threshold lives in the contract. | `contracts.py` |
| 6. Causal failure recovery | Idempotency keys (`find_idempotent`). Byte-exact compensating rollback on exception or failed verification. A ledger-write failure undoes the mutation. Dead letter records *why*, and later briefings surface it as `FAILED BEFORE`. | `tracker.py`, `ledger.py` |
| 7. Context compaction | Raw trace (tool output) → stamp (≤25 actions, ≤800-char evidence) → `<prior_agent_work>` briefing (char-budgeted, oldest history trimmed first) → `STATE.md` (one line per target) | `hydrate.py` |

## 3. Embedding rules (where the stamp lives)

**(a) Source and config files.** One block, three lines, at the top. It goes after any shebang, Python encoding line, `<!doctype>` or `<?xml?>`, and is replaced on every stamp:
```
# @agent-provenance [2026-10-24T20:32:23.412Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_9f8a7d6c5b4a3e21]
# @summary: Extract retry backoff into an idempotent helper
# @handoff: Cover backoff() in tests | ledger: .agent/ledger.jsonl#tr_9f8a7d6c5b4a3e21
```
Comment syntax follows the extension: `#` for py, sh, yaml and toml; `//` for ts, js, go and rs; `--` for sql; `/* */` for css; `<!-- -->` for html, xml and svg. Files with no comment syntax (JSON, lockfiles, binaries) get ledger-only stamps.

**(b) Markdown and docs.** A region at the bottom holds one machine comment plus a visible table (newest first, capped at 10 rows; the full history is in the ledger):
```
<!-- AGENT_WORKLOG:BEGIN -->
<!-- AGENT_LOG {"v":"1.0","ts":"…","agent":"claude-code","trace":"tr_…","status":"completed","verify":"verified_passed","hash":"sha256:…"} -->
#### Agent work log
| UTC | Agent | Status | Summary | Next | Trace |
<!-- AGENT_WORKLOG:END -->
```

**(c) Git.** Every autonomous commit carries trailers. Get them with `agent.py trailers <trace_id>`; `agent.py check-commit-msg` is the commit-msg hook:
```
Agent-Id: claude-code
Agent-Timestamp: 2026-10-24T20:32:23.412Z
Agent-Trace: tr_9f8a7d6c5b4a3e21
Agent-Status: completed/verified_passed
Agent-Summary: Extract retry backoff into an idempotent helper
Agent-Next-Step: Cover backoff() in tests
Agent-Trace-URI: .agent/ledger.jsonl#tr_9f8a7d6c5b4a3e21
```
`git log --grep "Agent-Trace: tr_…"` finds the commit, and `git blame` plus the trailer finds the stamp.

**(d) Databases.** Use `record_db_work(conn, stamp, table=…, pk_column=…, pk_value=…)` inside the same transaction as the business write. It inserts into the `agent_work_ledger` outbox and updates the shadow columns (`last_agent_id`, `last_agent_timestamp_utc`, `last_agent_summary`, `last_agent_trace_id`; DDL via `shadow_columns_ddl`). If the stamp fails, the transaction rolls back.

## 4. Tamper evidence and causal order
- **Content hashes.** `pre_state_hash` and `post_state_hash` are SHA-256 over the artifact with breadcrumbs stripped, so writing a breadcrumb is hash-neutral. Any later edit outside the protocol makes hydration report `integrity="DRIFT"`.
- **Chained entries.** Each entry stores `prev_entry_hash` and its own `entry_hash` over canonical JSON. `verify-chain` flags edited lines (hash mismatch) and deleted or reordered parents.
- **Git merges.** The ledger merges with `merge=union` (`.gitattributes`). Concurrent branches create forks (two children of one parent), which are valid and counted.
- **Causal links.** `parent_trace_id` links nested and delegated work. Nested `track_agent_work` calls inherit it automatically through a context variable.

## 5. Read-before-write protocol
1. **Provenance scan.** Load the last N stamps on the target and its dependencies, plus the inline breadcrumb (`hydrate_agent_context`).
2. **Negative-constraint injection.** Every `do_not_repeat`, earlier `FAILED BEFORE` reason and assumption goes into the worker's prompt as a hard constraint. On DRIFT, re-read the file before trusting older notes.
3. **Atomic commit + stamp.** Verify, write the breadcrumb (atomic replace), then append to the ledger with fsync. If either fails, the artifact is restored.

## 6. Limits, and what now covers them
| Limit (v1.0) | Now | Where |
|---|---|---|
| Leases were file-based, one host | Set `MOTION_LEASE_URL` + `MOTION_AGENT_TOKEN` and every tracker/CLI on every machine leases through the API's lease table (row-locked, Postgres in the cloud). If the service is unreachable, work stops: no lease, no write. The panel's Activity page shows who holds what. | `remote.py`, `services/api/app/agentops.py`, `/activity` |
| PII guard caught emails and phones only | Plus a private guest-name denylist: `.agent/private/guest_names.txt` (gitignored, refreshed from Tally by the daily check-in with `agent.py denylist --stdin`) and the `GUEST_DENYLIST` secret in CI and on the API. Checked in every stamp, by the pre-commit hook (`scan-staged`) and by CI on the diff. Full names only; a single word only when that's all the guest gave. | `privacy.py`, `hooks/pre-commit` |
| Agents skipping the SDK left only DRIFT | Coverage gate: every changed file on an agent branch needs a stamp whose hash matches the file now. CI fails the branch otherwise. `agent.py stamp --changed` stamps the whole change set in one call. Human branches get a report only. | `coverage.py`, CI job `provenance-coverage` |
| `agent.model` empty, so identity was thin | Agent registry `.agent/agents.json`: seat, lane, owned globs, max tier and branch prefixes. Stamps warn outside the lane; coverage fails a file last stamped by an agent outside its lane (one writer per file). | `registry.py` |

Still true: the ledger can't stop a person or a tool with direct push rights from bypassing CI. Branch protection on `main` (required check `provenance-coverage`) closes that. Jovanni turns it on in GitHub settings. The denylist only knows names that are on it. House rule unchanged: no model ids in pushed artifacts.

<!-- AGENT_WORKLOG:BEGIN -->
<!-- AGENT_LOG {"v":"1.0","ts":"2026-10-24T21:04:59.990Z","agent":"claude-code","trace":"tr_127ba23c92ae4d44","status":"completed","verify":"verified_passed","hash":"sha256:18b213db299ff5b38fa6dba6583995b0f4a498db69f52da58df0778e24fb059d","ledger":".agent/ledger.jsonl"} -->

#### Agent work log
| UTC | Agent | Status | Summary | Next | Trace |
|---|---|---|---|---|---|
| 2026-10-24T21:04:59Z | claude-code | completed / verified_passed | Close the four provenance limits: shared leases, guest denylist, coverage gate, agent reg… | Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION… | `tr_127ba23c92ae4d44` |
| 2026-10-24T20:50:20Z | claude-code | completed / verified_passed | Blueprint: components, seven autonomy pillars, embedding rules, tamper evidence | Add a Postgres lease table if several hosts write one checkout | `tr_f425f9a4eff54327` |
<!-- AGENT_WORKLOG:END -->
