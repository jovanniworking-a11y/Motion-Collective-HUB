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

## 21 Oct — file-push build, then merge

- `cursor/file-push-2026-10-21` at `dfc33d4` had a green hygiene scan and a red Vercel status. The branch had no `vercel.json`, and `services/api/requirements.txt` had no Postgres driver.
- Jovanni restored both on that branch: `b384c81` (`vercel.json`, services + rewrites) and `c143987` (`psycopg[binary]>=3.1.0`).
- Head `c143987` went green before the merge. Vercel deployment completed. Hygiene `scan` succeeded. Autonomy `check` succeeded (link check, API pytest, panel typecheck and unit tests). Merge state was clean.
- Jovanni had authorized the merge into `main` once that build was green. PR #4 merged at `ea7f505` (21 Oct 18:57 UTC). The diff against the previous `main` was those two files only.
- Merge commit `ea7f505` itself finished green: Vercel deployment completed, hygiene `scan` succeeded, autonomy `check` succeeded.
- A later commit on `main`, `ccfd2d5` ("Fix panel API base"), is red. Autonomy fails in `apps/ops-panel/src/lib/api.test.ts`: `apiBase()` returns `""` in the browser, and the test still expects port `8787`. Vercel and hygiene on that commit succeeded. The file is Atlas's. No API change.
- No new Source of Truth facts. `orch/context/CURRENT_LOCK.md` (21 Oct) still wins.
