# MOTION Ops — architecture standard

**Status:** approved steer (**T-013A-arch** — architecture review; board `T-013` remains Abraham’s brief). Draft/local only. Builders on `apps/`, `services/`, `desktop/`, `ops/` follow this. Do not invent a parallel stack.

## Verdict
One Discord-like ops control plane is **in**. Ship **phased**. Do not rebuild Cursor inside Ops. Do not N+1 every model on every click.

## Standard stack

| Layer | Choice | Path |
|---|---|---|
| UI | TypeScript · Next.js · React | `apps/ops-panel` |
| Desktop shell | Electron (thin host) | `desktop/` |
| Night-Of (phones) | Static PWA, offline-capable | `ops/` |
| BFF | Python **FastAPI** | `services/api` |
| Usage / jobs | **SQLite** + job rows (worker process for sims) | `services/api/data` |
| Orchestration truth | File protocol (unchanged) | `orch/` |
| CLI catalog / learning | Keep as CLI | `hub.py` |

## Patterns we copy
- BFF + desktop shell (Discord / VS Code / Figma)
- Channel UX for crew + bots (Discord / Slack)
- Agent observability (LangSmith / Helicone-style **event log**, not vibes)
- Digital twin panel later (Studio three.js) — sims as **jobs**, not UI thread work
- Router table: `area → model` (one primary call per action; fallback on failure only)

## MVP (must exist before “full vision”)
1. Night-Of parity in `ops/` + panel  
2. Desktop loads panel or `ops/`  
3. FastAPI: health, ops read, `usage_events`, stub `agent_runs`  
4. One agent channel UI → BFF → router table  
5. Meter every routed call  

**Later:** live Studio embed, sim workers, cost charts, auth/hosted.

## Constraints (non-negotiable)
- No guest PII · no venue address in client, logs, or prompts  
- API keys **server-only** (`.env`) · never in Next public env or Electron renderer  
- Auth later; nothing public until then  
- No spend / send / post from the app  
- Label numbers `confirmed` / `estimate` / `open`  
- Kill: in-app coding IDE, hub.py-as-HTTP-server, multi-model fan-out per click  

## Ownership
- Night-critical UI can ship in `ops/` without waiting on Next.  
- Panel owns long-term crew UX.  
- BFF owns keys, routing, metering, jobs.  
- Desktop only hosts; it does not reimplement product logic.

Full review: `orch/tasks/outbox/T-013A-arch_architecture_review.md` (renamed from `T-013_architecture_review.md` to avoid colliding with board T-013).
