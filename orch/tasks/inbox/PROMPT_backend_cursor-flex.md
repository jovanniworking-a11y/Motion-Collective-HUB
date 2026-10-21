# FOR: Cursor — FLEX TAKEOVER of the backend package (Claude seat out of usage)
Pip → Jovanni hand-carry → Cursor. Written 20 Oct 2026. Supersedes PROMPT_backend_claude.md for execution; Claude ratifies on return.

**AMENDMENT (Jovanni, 20 Oct ~2:29 PM): "let Cursor merge."** The merge to main is AUTHORIZED for this package — step 3 below now ends in an actual merge by you, not just prep. Claude ratifies after the fact when its usage returns. Everything else stands.

---

Cursor — you're flexing into the orchestrator's backend package: Claude's seat is out of usage, and you built this backend, so you hold the context. Scope is everything EXCEPT the merge to main and any Source-of-Truth edit — those stay reserved for Claude's ratification (or Jovanni's one-time exception). Work on your own branches only.

VERIFIED STATE (Pip, git, 20 Oct): your FastAPI `services/api/` ("MOTION Control Plane API", uvicorn :8787, pytest, SQLite) sits on `cursor/claude-pro-bridge` @a905bcd; your T-013 architecture review + BFF constraints sit on `cursor/architecture-review-07eb` @e7b4fe8; an earlier data MVP (/api/data/*) sits unmoved on `cursor/muse-cloud-platform-c430` @220f6b6. Nothing is on main.

YOUR JOB:
1. STACK RECOMMENDATION (not ruling — Claude ratifies, Jovanni can overrule): FastAPI control plane vs the TypeScript assumption in SOFTWARE_SPEC / the data-platform briefs. One paragraph: your pick, the reason, what spec wording changes if adopted.
2. RECONCILE the two backends on the `cursor/claude-pro-bridge` branch: fold the /api/data/* endpoints from muse-cloud-platform-c430 into services/api, OR mark the data MVP superseded in its README with a one-line pointer. One backend survives. Keep the BFF constraints: no guest names (pass numbers only), no venue address in any file/endpoint, no provider keys in responses.
3. MERGE-READY PREP → MERGE (authorized, see amendment): bring services/api on claude-pro-bridge to merge state — tests green (`python3 -m pytest -q`), README run instructions accurate, no stray branches' files mixed in — then MERGE it to main yourself and name both the source commit and the merge commit in your gist.
4. T-013 COLLISION: on your branches T-013 = architecture review; on the ops board T-013 = Abraham's brief. Rename YOURS (e.g., T-013A-arch) in the outbox filenames and note the rename — don't touch the board's numbering.
5. OUTBOX GIST (orch/tasks/outbox/, per orch/AGENTS.md): recommendation, what you folded/killed, the merge-ready commit SHA, test result, what's left for DP-01..04, questions for Jovanni. Label every number confirmed / estimate / open.

Codex is simultaneously building DP-01 (new `data-platform/` folder) + T-009 sims in its own lane — it won't touch services/api; don't touch its folder. Nothing spent, sent, posted, or published.
