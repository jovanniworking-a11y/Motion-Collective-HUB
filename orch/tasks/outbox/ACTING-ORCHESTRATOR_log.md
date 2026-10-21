# Acting orchestrator log

Cursor is the acting Source-of-Truth editor until Claude returns. This file is the handback. Decisions are recorded from Jovanni’s queue (21 Oct). Nothing spent, sent, posted, or published.

## 21 Oct — seats

- Cursor owns repo code and `services/api` (the only data-platform API, `/api/data/*`).
- Codex still owns T-002 (budget workbook) and T-009 (drink sims). They are not in this tree as API work. T-009’s studio runner is on `cursor/t015-t2-rebuild` (`orch/context/studio/_t009_drinks.py`) and has not been folded. When either lands, it merges into `services/api`, not a second backend.
- Atlas owns `apps/ops-panel` and Vercel.
- Claude remains orchestrator on return. Pip verifies SoT edits before the board treats them as settled.

## 21 Oct — hygiene, then merge

- Hygiene on `cursor/file-push-2026-10-21` was failing on lineup rot and dead scratch. The clearing commit is `dfc33d4` and that commit is `origin/main`. Latest hygiene run on `main`: success (`39637971832`). Local `python3 orch/hygiene/scan.py` prints `hygiene ok`.
- Jovanni authorized the merge to `main` after that fix. The link-audit branch (`cursor/architecture-link-audit-3a45`, PR #2) is the data-platform API work still ahead of `main` (Data page, stub-sim finish, link check). Hygiene and autonomy on that PR are success. The Vercel status is failure; the build log is behind Vercel login, so the compiler error is not in this log. Atlas’s check. Merge proceeds on the authorization above.

## SoT

No new Source of Truth facts in this entry. `orch/context/CURRENT_LOCK.md` (21 Oct) still wins. Header pointer in `SOURCE_OF_TRUTH_latest.md` stays.
