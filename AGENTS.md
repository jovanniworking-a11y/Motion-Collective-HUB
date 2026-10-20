# AGENTS.md — MOTION Collective HUB (Cursor / coding agents)

You are a **worker** on the MOTION Collective hub. Claude (project "MOTION EFFEcts") is the orchestrator. Read `orch/AGENTS.md` and `orch/CLAUDE.md` before changing anything. On conflict, **Source of Truth** sections win (`orch/context/SOURCE_OF_TRUTH_latest.md` and the Claude Project docs).

## Standing orders
- **Never spend, send, post, or publish.** Drafts and local builds only. Jovanni OK required before anything goes out.
- **Label every number** `confirmed` / `estimate` / `open`.
- **Never write the venue address** or any **guest personal data** into any file, post, or page.
- Work on a branch named `cursor/<task>` (never straight onto Source-of-Truth files under `orch/context/` unless the orchestrator assigns that edit).
- Summarize every completed change in `orch/tasks/outbox/` (`T-###_result.md` format in `orch/AGENTS.md`).
- Guest data stays out of git. No YSL marks, haze/fog, or lasers in creative work. Brand type: Bodoni Moda + Jost; red ≤ 10% of frame and never as a tint on images.

## Project snapshot
- Event: **Devil's Night · AFTERIMAGE 001**, Fri 30 Oct 2026, doors 9 PM, hard stop 2 AM (Austin).
- Lineup (promo order): iamariology b2b raymixes → Glamz → HE//THEY · co.b b2b NiiON. Rohan Rali is cut.
- Hub: `python hub.py` · fan site `site/` · crew hub `web/` · orchestra kit `orch/`.

## MOTION Ops control plane
- UI: `apps/ops-panel` — `npm run dev` → http://localhost:3000
- API: `services/api` — `python3 -m uvicorn app.main:app --app-dir services/api --port 8787`
- Desktop: `desktop/` — `npm run desktop` (prefers panel on :3000)
Legacy phone page still at `ops/index.html` (same localStorage `motion-night-ops-v1`). Draft only.

## MOTION Ops — architecture constraints (T-013A-arch)
Read **`ARCHITECTURE.md`** before growing `apps/ops-panel`, `services/api`, or `desktop/`. Full review: `orch/tasks/outbox/T-013A-arch_architecture_review.md` (renamed; board `T-013` stays Abraham’s).
- Stack: Next/React panel · Electron shell · **FastAPI BFF** · SQLite usage/jobs · keep `ops/` for night phones.
- One backend: `services/api` (includes `/api/data/*`). Do not stand up a parallel data HTTP service.
- MVP first: Night-Of + shell + thin BFF + one routed bot channel + metering. Studio live-edit/sims are a **later pane** (job queue, not UI thread).
- Router table `area → model` — never fan-out every model on every click.
- Keys server-only; no guest PII; no venue address; no spend/send/post; auth later.
- Kill: in-app coding IDE (use Cursor), `hub.py` as HTTP server.
