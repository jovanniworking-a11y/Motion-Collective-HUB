# T-012 · MOTION Ops desktop shell (Electron)

**Owner:** Cursor (Claude Code seat) · run `bc-5eb6a945`  
**Branch:** `cursor/ops-desktop-e7a0`  
**Commit:** `a2d1bee0fed25eed79fb0467225de1ea5ee51541` (desktop shell `7271e1c`)  
**Status:** draft / local only — not published

## What I did
Shipped a Discord-like desktop launcher so MOTION ops runs as a real PC window. Stack: **Electron** in a standalone `desktop/` package (own `package.json` so it does not contend with the sibling Next app in `apps/ops-panel`). Target resolver: `MOTION_OPS_URL` → Next `localhost:3000` when reachable → static Night-Of `ops/` → placeholder shell. Tray + single-instance + close-to-tray. Python `desktop/launch.py` wraps Electron (optional `MOTION_OPS_ENGINE=webview`).

## Files produced
- `desktop/package.json` — MOTION Ops Electron app + `npm run desktop` / `smoke`
- `desktop/main.js` — window, tray, static server, target hooks
- `desktop/preload.js` — small contextBridge
- `desktop/shell/fallback.html` — waiting shell if no panel/ops
- `desktop/launch.py` — Python one-command entry
- `desktop/README.md` — launch + env hooks
- `package.json` (repo root) — `npm run desktop` / `desktop:smoke`
- `README.md` / `AGENTS.md` — desktop pointers
- `orch/tasks/outbox/T-012_result.md` — this file

## How verified
- `cd desktop && npm install && npm run smoke` — main process boots, resolves target, prints `smoke OK`, exit 0 (no display required).
- Manual on a desktop PC: `npm run desktop` should open the **MOTION Ops** window; tray show/hide; Quit from tray.

## Numbers
None changed.

## Proposed SoT changes
- None. Optional later: point crew docs at `desktop/` as the PC ops entry once Jovanni accepts.

## Questions for Jovanni
1. Prefer product name **MOTION Ops** or **AFTERIMAGE Ops** on the window/tray?
2. OK to keep close-to-tray (Discord-like), or should close quit immediately?
