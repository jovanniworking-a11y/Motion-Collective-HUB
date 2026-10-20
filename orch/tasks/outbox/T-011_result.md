# T-011 · Night-Of Ops App (local)

**Owner:** Cursor (Claude Code seat)  
**Branch:** `cursor/night-of-ops-6609`  
**Status:** draft / local only — not published

## What I did
Built an offline-capable crew phone page for Oct 30: pass check-in, run-of-show with countdowns, welfare 30-min rounds + 12:30 collision alert, and a read-only budget snapshot. Added root `AGENTS.md` with standing orders. Data seeded from `data/events.csv`, `web/seed.json`, and SoT labels (no guest names, no venue address).

## Files produced
- `AGENTS.md` — root standing orders for coding agents
- `ops/index.html` — Night-Of Ops app (Door / Show / Welfare / Budget)
- `ops/data.js` — event, capacity, ROS, welfare, budget seed
- `ops/sw.js` — service worker cache shell
- `ops/manifest.webmanifest` — installable local PWA shell
- `ops/README.md` — how to serve locally
- `orch/tasks/outbox/T-011_result.md` — this file

## How verified
- Served `ops/` via `python -m http.server` and exercised DOM/logic in headless Chromium (check-in toggle, tab switch, welfare log, budget figures, clock sim mode).
- Confirmed no venue address and no guest personal data in new files.

## Numbers (labeled)
| Item | Value | Label |
|---|---|---|
| Working pass cap | 50 | estimate |
| Passes planned (SoT legacy) | 70 | open |
| Pool | $450 | confirmed |
| Pool spend | $381.13 | estimate |
| Buffer | $68.87 | estimate |
| Doors / last entry / last pour / hard stop | 9 PM / 12:30 AM / 1:45 AM / 2 AM | confirmed (ops cues) |

## Proposed SoT changes
- None required. Optional: add a SoT pointer to `ops/` as the night-of crew tool once Jovanni accepts the draft.
- Optional board row: T-011 Night-Of Ops App → done (local).

## Questions for Jovanni
1. Door list: keep **001–050** (working cap) or show **001–070** with the cap still at 50?
2. OK to host this as a private link later, or phone-only via local/Wi‑Fi serve?
3. Should welfare rounds start at crew briefing (8:30) or doors (9:00)? Currently doors → hard stop.
