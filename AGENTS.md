# AGENTS.md — MOTION Collective HUB (Cursor / coding agents)

You are a **worker** on the MOTION Collective hub. Claude (project "MOTION EFFEcts") is the orchestrator. Read `orch/AGENTS.md`, `orch/CLAUDE.md`, and `orch/context/CURRENT_LOCK.md` before changing anything. On conflict, **CURRENT_LOCK.md and root CLAUDE.md hard rules win** over older Source of Truth paragraphs.

## Standing orders
- **Provenance (read before write, stamp on exit):** before editing any file run `python3 orch/provenance/agent.py hydrate <file>`; after editing run `agent.py stamp …` and put `agent.py trailers <trace>` in the commit. Rules: `orch/provenance/WORKER_PROMPT.md`.
- **Never spend, send, post, or publish.** Drafts and local builds only. Jovanni OK required before anything goes out.
- **Label every number** `confirmed` / `estimate` / `open`.
- **Never write the venue address** or any **guest personal data** into any file, post, or page.
- Work on a branch named `cursor/<task>` (never straight onto Source-of-Truth files under `orch/context/` unless the orchestrator assigns that edit).
- Summarize every completed change in `orch/tasks/outbox/` (`T-###_result.md` format in `orch/AGENTS.md`).
- Guest data stays out of git. No YSL marks, haze/fog, or lasers in creative work. Brand type: Bodoni Moda + Jost; red ≤ 10% of frame and never as a tint on images.
- Before you finish a push, run `python3 orch/hygiene/scan.py`. If it fails, fix the hit. Do not delete `apps/`, `services/`, `desktop/`, or `hub.py` to make it pass.

## Project snapshot
- Event: **Devil's Night · AFTERIMAGE 001**, Fri 30 Oct 2026, doors 9 PM, hard stop 2 AM (Austin).
- Lineup: iamariology b2b raymixes → Rohan Rali b2b Shubh Samtani (11:00 PM–12:15 AM; Rohan $175 confirmed 23 Oct, replacing the 21 Oct "no fee"; Shubh Samtani unpaid) → HE//THEY · co.b b2b NiiON. A canceled 20 Oct act is not on this lineup and does not go in copy.
- Hub: `python hub.py` · fan site `site/` · crew hub `web/` · orchestra kit `orch/` · hygiene `orch/hygiene/`.

## MOTION Ops control plane
- UI: `apps/ops-panel` — `npm run dev` → http://localhost:3000
- API: `services/api` — `python3 -m uvicorn app.main:app --app-dir services/api --port 8787`
- Desktop: `desktop/` — `npm run desktop` (prefers panel on :3000)
Legacy phone page still at `ops/index.html` (same localStorage `motion-night-ops-v1`). Draft only.

## MOTION Ops — architecture constraints (T-013A-arch)
Read **`ARCHITECTURE.md`** before growing `apps/ops-panel`, `services/api`, or `desktop/`. Full review: `orch/tasks/outbox/T-013A-arch_architecture_review.md` (renamed; board `T-013` stays Abraham's).
- Stack: Next/React panel · Electron shell · **FastAPI BFF** · SQLite usage/jobs · keep `ops/` for night phones.
- One backend: `services/api` (includes `/api/data/*`). Do not stand up a parallel data HTTP service.
- MVP first: Night-Of + shell + thin BFF + one routed bot channel + metering. Studio live-edit/sims are a **later pane** (job queue, not UI thread).
- Router table `area → model` — never fan-out every model on every click.
- Keys server-only; no guest PII; no venue address; no spend/send/post; auth later.
- Kill: in-app coding IDE (use Cursor), `hub.py` as HTTP server.

<!-- AGENT_WORKLOG:BEGIN -->
<!-- AGENT_LOG {"v":"1.0","ts":"2026-10-24T21:04:59.859Z","agent":"claude-code","trace":"tr_d259553969a144f9","status":"completed","verify":"verified_passed","hash":"sha256:e21aa41f3b77f5495bbd5f7b21c471b9ef686f8b2c3382577559bef053da9463","ledger":".agent/ledger.jsonl"} -->

#### Agent work log
| UTC | Agent | Status | Summary | Next | Trace |
|---|---|---|---|---|---|
| 2026-10-24T21:04:59Z | claude-code | completed / verified_passed | Close the four provenance limits: shared leases, guest denylist, coverage gate, agent reg… | Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION… | `tr_d259553969a144f9` |
<!-- AGENT_WORKLOG:END -->
