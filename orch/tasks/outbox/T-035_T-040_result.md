# T-035 … T-040 result · MOTION Ops readiness (Claude Code, 23 Oct)
**Seat:** Claude Code · **Branch:** `claude/motion-files-consolidated-dx17w2` (now contains all of `main`) · Nothing spent, sent, posted or deployed.

## What I did
| ID | Done | Files |
|---|---|---|
| T-035 CI | `ci.yml`: API pytest on SQLite **and** Postgres 16; panel `npm ci`, typecheck, lint, vitest, build, Playwright smoke + Night-Of + login e2e | `.github/workflows/ci.yml` |
| T-036 Night-Of | Door cap 70 (confirmed) in panel + phone page; cap label follows the data; Rohan's set ends 00:15; budget shows pool $498 / buffer $116.87 / Rohan $175; offline-safe service worker | `apps/ops-panel/src/lib/ops-data.ts`, `NightOfClient.tsx`, `public/sw.js`, `ops/data.js`, `ops/index.html`, `e2e/nightof.spec.ts` |
| T-037 Login | Password + authenticator code on panel and API; fails closed on Vercel; `/health` public | `src/middleware.ts`, `src/lib/auth/*`, `services/api/app/auth.py`, `DEPLOY_LOGIN.md` |
| T-038 Metering | Tests: one `usage_events` row per agent call and per sim, no prompt text in usage, routing table matches `MODEL_ROUTING.md`. Assist/agent money facts refreshed. Stale model IDs → `claude-sonnet-5-5` / `claude-haiku-5-5` | `services/api/tests/test_metering.py`, `app/chat.py`, `src/lib/claude.ts` |
| T-040 Runbook | One page: one door device owns counts, Thursday setup, night timeline, failure modes, 2 AM export + wipe | `ops/RUNBOOK.md` |

Also: merged `main` (21 Oct lock, live-ops, link + hygiene checks) into the working branch; renumbered Claude Code's 23 Oct tasks to T-030…T-040 (T-019…T-022 belong to main's results); added the 23 Oct section to `orch/context/CURRENT_LOCK.md`.

## How I verified
- `python3 scripts/check_links.py` → OK · `python3 orch/hygiene/scan.py` → ok
- API: 19 passed on SQLite and 19 passed on a real Postgres 16 (row-level security on every table)
- Panel: typecheck, lint clean, 24 unit tests, `next build`, Playwright 8 passed (smoke 4 + Night-Of 4, incl. airplane-mode reload) + login 3 passed
- Phone page rendered at 390 px in headless Chromium: cap 70 (confirmed), pool $498, buffer $116.87, 70 pass buttons, no console errors

## Proposed SoT changes (Claude chat, T-033)
Record the 23 Oct lock section in the SoT body: Rohan $175 (replaces "no fee"), DJ $475, pool $498, buffer $116.87 (est), CDJs $345 by Jovanni, matchbox + cameras approved, Cap 01 cut.

## Questions for Jovanni
1. Does Shubh Samtani have a fee? (open)
2. OK to merge this branch into `main`? It is a clean fast-forward (no conflicts), and it is what puts the login on the version Vercel deploys.
3. The Vercel settings for the login (`DEPLOY_LOGIN.md`) are yours to add.
