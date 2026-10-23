# ACTING ORCHESTRATOR — running handback log

**Role:** Cursor = acting orchestrator until Claude returns (plan dark through Fri 30 Oct 2026).  
**Charter:** RECORD decisions; do not ORIGINATE. SoT edits only from Jovanni/Alex/verified facts + source pointers. Every SoT edit → outbox changelog. Pip verifies at hub before settled. Nothing spent/sent/posted/published. No guest names; no venue address. DP-02 → `services/api` only; no `data-platform/` touch.

**Branch for this loop:** `cursor/acting-orchestrator-4cc7` (SoT/prep). Backend merge landed on default.

---

## 2026-10-20 — queue execution

### 1. Backend package → MERGE (authorized) — DONE

| Action | Detail |
|---|---|
| Verified tip | `cursor/backend-reconcile-c926` @ `9799bb60956831396046158a6050cf7012bc1223` |
| Fold SHA | `fc419bb71039333920a547bcd74d7026897a53a0` (FastAPI + `/api/data/*`) |
| Target | `origin/HEAD` = `claude/motion-files-consolidated-dx17w2` (no `main`/`master`) |
| Pre-merge tip | `a397cbce4f56a477d1c27cd63a1f92813b834075` |
| Merge commit | `06890c571aa3e7a2b2238b89db0962d0894badf0` |
| Push | `origin/claude/motion-files-consolidated-dx17w2` updated `a397cbc..06890c5` |
| pytest | `python3 -m pytest -q services/api` → **8 passed** (pre + post) |
| Receipt | `orch/tasks/outbox/T-018_merge_receipt.md` |

### 2. T-003 cleanup (RECORD) — DONE · Pip verify OPEN

| Action | Detail |
|---|---|
| Edited | `data/metrics.csv`, `orch/context/SOURCE_OF_TRUTH_latest.md` |
| Changelog | `orch/tasks/outbox/T-003_sot_cleanup_changelog.md` |
| Recorded | pool spend **$381.13** est · buffer **$68.87** est · cap **70** conf · DJ **$475** conf (brief; no prior repo `$475`) |
| Retired from live layers | $391.42 · $58.58 · $171.88 (as live drinks) · DJ-$300-only total · cap-50 |
| Left open | $175 fee split inside $475 · Jovanni personal-owes recompute |
| **Pip** | **flag OPEN** — verify at hub before board treats settled |

### 3. T-011 lineup / VAMP — PREP ONLY

| Action | Detail |
|---|---|
| File | `orch/tasks/outbox/T-011_prep_vamp_midset.md` |
| Status | One-step merge diff ready; **no lock** without Jovanni + VAMP reply |
| Repo note | No prior VAMP artist confirmation string found |

### 4. Friday venue tape (23 Oct) → T-001 support — PREP

| Action | Detail |
|---|---|
| File | `orch/tasks/outbox/T-001_friday_venue_tape_support.md` |
| Scope | Code support checklist when measurements land; Codex sims; API via `services/api` only |

### Also

| Action | Detail |
|---|---|
| BOARD.md | FACT/PATCH_SUMMARY gist + status rows; Abraham T-013 not renumbered |
| AGENT_COMMS file | Not found in repo; gist written on BOARD in that style anyway |

---

## Open questions (for Pip / Claude audit)

1. Confirm DJ **$475** committed total and name the $175 above HE//THEY $300.
2. Recompute Jovanni personal-owes after $475 (do not use stale $450 personal total).
3. VAMP mid-set: confirm slot vs Glamz; fee; whether $475 already includes VAMP.
4. Cap 70 vs Fri 23 Oct tape comfort — re-check after measurements, do not auto-change.
5. Claude to ratify acting SoT edits after return.

---

## Do-not list (honored)

- No force-push  
- No second API / no `data-platform/`  
- No spend/send/post/publish  
- No guest names; no venue address  
- No lineup lock without confirmation  
- No invented policy  

---

## SHAs for Claude handback (copy)

```
default_branch=claude/motion-files-consolidated-dx17w2
backend_merge_commit=06890c571aa3e7a2b2238b89db0962d0894badf0
acting_content_commit=1649ced (on cursor/acting-orchestrator-4cc7)
default_tip_after_acting_merge=66628bc6f401fc1938eb9c80cc8e6453328ef384
backend_tip=9799bb60956831396046158a6050cf7012bc1223
api_fold=fc419bb71039333920a547bcd74d7026897a53a0
acting_branch=cursor/acting-orchestrator-4cc7
pytest_services_api=8 passed
```

# Acting orchestrator log

Cursor is the acting Source-of-Truth editor until Claude returns. This file is the handback. Decisions are recorded from Jovanni’s queue (21 Oct). Nothing spent, sent, posted, or published.

## 21 Oct — seats

- Cursor owns repo code and `services/api` (the only data-platform API, `/api/data/*`).
- Codex still owns T-002 (budget workbook) and T-009 (drink sims). They are not in this tree as API work. T-009’s studio runner is on `cursor/t015-t2-rebuild` (`orch/context/studio/_t009_drinks.py`) and has not been folded. When either lands, it merges into `services/api`, not a second backend.
- Atlas owns `apps/ops-panel` and Vercel.
- Claude remains orchestrator on return. Pip verifies SoT edits before the board treats them as settled.

## 21 Oct — hygiene, then merge

- Hygiene on `cursor/file-push-2026-10-21` was failing on lineup rot and dead scratch. The clearing commit is `dfc33d4` and that commit is `origin/main`. Latest hygiene run on `main`: success (`39637971832`). Local `python3 orch/hygiene/scan.py` prints `hygiene ok`.
- Jovanni authorized the merge to `main` after that fix. PR #2 (`cursor/architecture-link-audit-3a45`) merged at `d1ac94c` (21 Oct 18:24 UTC). It carries the Data page, the stub-sim finish, the link check, and this seat note. Hygiene and autonomy on the PR were success before the merge. The Vercel status on that head was still failure; the build log is behind Vercel login. Atlas’s check. Product deploys stay off until Jovanni OKs them.

## SoT

No new Source of Truth facts in this entry. `orch/context/CURRENT_LOCK.md` (21 Oct) still wins. Header pointer in `SOURCE_OF_TRUTH_latest.md` stays.

## 21 Oct — same-origin API base

- The browser client stays same-origin. `apiBase()` returns `""` when `window` exists, and Vercel rewrites carry `/api/*`, `/health`, and `/studio/embed` to `services/api`. That is the fix for the "Failed to fetch" outage. Outside the browser the default remains `http://127.0.0.1:8787`.
- Autonomy on `main` (`9b9a5f7`) was red for one reason: `apps/ops-panel/src/lib/api.test.ts` still expected port 8787 inside jsdom. Vercel and hygiene on that commit were success. Muse's data API is unchanged.
- Local `next.config.ts` now proxies the same bare collection roots the panel calls (`/api/agents`, `/api/data`, `/api/routing`, `/api/sims`, `/api/studio`). `vercel.json` already had those exact paths.
- `160c3b0` made page navigations network-first so a deploy is not stuck on a stale bundle. `scripts/check_links.py` was still requiring every nav route in the service-worker precache list. The check now requires `/` in that list, network-first navigations, and `/api/` left uncached.
- No new Source of Truth facts.
