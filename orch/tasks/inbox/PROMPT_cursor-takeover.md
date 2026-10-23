# FOR: Cursor — ACTING ORCHESTRATOR TAKEOVER (Claude out until next week)
Pip → Jovanni hand-carry → Cursor. Written 20 Oct 2026. Runs alongside the backend flex package (PROMPT_backend_cursor-flex.md, as amended — merge authorized).

---

Cursor — Claude's seats (chat + Code, one usage pool) are out until next week. Per the failover roster you are the flex for Claude Code, and Jovanni is extending you into an ACTING role for the orchestration lane until Claude returns. Plan as if Claude is dark through the event (Fri 30 Oct); if it resets early, hand back cleanly.

## What you take over
1. **The backend package** (already yours: stack recommendation, reconcile the two backends, merge services/api to main — authorized).
2. **Repo code + Studio support** (Claude Code's lane): including Studio help for T-001 once Friday's venue tape lands (Codex runs the sims; you own code changes).
3. **ACTING Source-of-Truth editor** — bounded charter below.
4. **DP-02 backend API work** (was Claude Code's brief) — it folds into your services/api lane; don't build a second API.

## The acting-editor charter (non-negotiable)
- You RECORD decisions; you do not ORIGINATE them. SoT changes come only from: Jovanni's calls, Alex's board decisions, or verified facts with a source pointer (commit, message, measurement).
- **Every SoT edit ships with a change-log entry** in `orch/tasks/outbox/` (what changed, why, source pointer) so Claude can audit and ratify on return.
- Pip verifies every SoT edit at the hub before the board treats it as settled. If Pip flags it, it waits.
- Nothing spent, sent, posted, or published. Numbers labelled confirmed / estimate / open. No guest names (pass numbers only), no venue address, in any file.

## This week's queue (in order)
1. Backend package → merge (see its prompt).
2. **T-003 cleanup:** the retired figures still sitting in metrics.csv and the SoT's 13-Oct layer ($391.42, $171.88, $58.58, DJ-$300-only, cap-50) get replaced by the reconciled state (pool spend $381.13 / buffer $68.87 estimates; cap 70 confirmed; DJ fees $475 committed) — with a change-log entry citing the reconciliation.
3. **T-011 lineup lock:** substance waits on DJ VAMP's schedule reply (Pip's inbox watch flags it the hour it lands; Jovanni's standing intent: if VAMP can play, he fits into the mid set). When it lands + Jovanni confirms, you run the merge; until then, prep the diff so it's one step.
4. Friday's venue tape (23 Oct) → support T-001 inputs (Alex/Jovanni measure; Codex sims; your code).

## Handback
Keep a single running gist, `orch/tasks/outbox/ACTING-ORCHESTRATOR_log.md`: every action, every edit, every open question for Claude. That file IS the handback — Claude resumes from it without a meeting.

Questions and blockers route to Pip (hub), not to Jovanni's chat, unless they're money, safety, or plan-invalidating — those go straight up with the verified facts.
