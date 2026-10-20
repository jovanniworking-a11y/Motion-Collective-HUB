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

## Night-Of Ops
Crew phone page for Oct 30: `ops/index.html` (local / offline-capable). Hosting stays with Jovanni.

## MOTION Ops desktop
Discord-like Electron shell: `desktop/` — `npm run desktop` (root) or `python desktop/launch.py`. Loads `apps/ops-panel` when on `localhost:3000`, else Night-Of `ops/`. Additive packaging only; do not rewrite the Next app from the desktop seat.
