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
- **Cloud (primary):** `docs/CLOUD_HOSTING.md` — Vercel panel + Fly/Railway API; Pro Prompt Bridge default
- **Muse data / compare:** `docs/MUSE_DATA_PLATFORM.md` — SQLite MVP · `/api/data/*` · panel `/data`
- UI: `apps/ops-panel` — `npm run dev` → http://localhost:3000 · env `NEXT_PUBLIC_API_URL`
- API: `services/api` — `python3 -m uvicorn app.main:app --app-dir services/api --port 8787`
- Desktop: `desktop/` — **optional** Electron; cloud users open the panel URL
- Studio helper: `orch/context/studio/_t2.py` — `python3 _t2.py smoke` (unblocks `_night2` / `_all2`)
Legacy phone page still at `ops/index.html` (same localStorage `motion-night-ops-v1`). Draft only.

## Cursor online
Cloud Cursor **can push** `cursor/*` branches from this environment. If another seat’s GitHub connector cannot write, that is a connector permission — not Cursor offline. Presence receipts: `orch/tasks/outbox/T-016_cursor_online.md`.
