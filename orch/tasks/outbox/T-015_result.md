# T-015 result — Studio `_t2.py` rebuild

**Seat:** cursor · **Model:** Composer · **Timestamp:** 2026-10-20T16:23:51Z  
**Branch:** `cursor/t015-t2-rebuild`  
**Inputs:** `orch/context/studio/_err.py` (ARGS), consumers `_chk*.py`/`_night2.py`/`_all2.py`, `orch/AGENTS.md`, kickoff brief 20 Oct, `orch/context/DRIVE_INDEX.md` (T-009 menu).  
**Output:** this file + pointers below.

## What done
- Recreated `orch/context/studio/_t2.py` with `ARGS` (exact set from `_err.py`) and `boot(pg)` (load Studio, clear localStorage, wait for `window.__studio`). Repo-relative paths; three.js from CDN (optional `MOTION_THREE_ROOT`).
- De-hardcoded `test_studio.py` and `_err.py` (removed `/home/claude/motion/...` paths).
- Smoke: `_t2.py smoke`, `_chk4.py`, `_night2.py` — all exit 0, no page errors.
- Ran T-009 drink-spot + stock sims end-to-end (`_t009_drinks.py`).
- Root `AGENTS.md` standing orders committed on this branch as draft; **permanent merge is Claude/Jovanni’s call**.

## Files produced
| Path | Note |
|---|---|
| `orch/context/studio/_t2.py` @ `3db1a23b3a32e3a2b0e984ea1794c5e2a653816f` | blob SHA; commit `94ae199` (fix after docstring split marker) |
| `orch/context/studio/test_studio.py` | portable paths + CDN |
| `orch/context/studio/_err.py` | portable paths; ARGS unchanged |
| `orch/context/studio/_t009_drinks.py` | T-009 runner |
| `orch/context/studio/_t009_drinks.json` | drink/stock artifact |
| `orch/context/studio/_night2.json` | night tour means (from smoke) |
| `AGENTS.md` | standing orders (draft on branch) |
| `orch/tasks/inbox/T-015_studio-t2-rebuild.md` | inbox brief |
| `orch/tasks/outbox/T-017_plan.md` | Night-Of Ops plan-only pointer |

## How verified
| Check | Pointer | Result |
|---|---|---|
| `_t2` smoke | `orch/tasks/outbox/_t015_smoke_t2.log` | `studio.ok=true`, items=10, errors=[] · label **confirmed** |
| `_chk4` | `orch/tasks/outbox/_t015_smoke_chk4.log` | ballCheck grid returned; EXIT 0 |
| `_night2` | `orch/tasks/outbox/_t015_smoke_night2.log` + `_night2.json` | baths 1\|2 chapters + totals; errors=[] |
| T-009 | `orch/tasks/outbox/_t009_run.log` + `_t009_drinks.log` / `_t009_drinks.json` | optimizeDrinks win ±4.6% (ok); stock plan baths 1\|2 · label **estimate** |

## Proposed SoT changes
- Note that Studio Playwright helper `_t2.py` is restored (path above); agents should run Studio scripts from `orch/context/studio/`.
- T-009: sim cocktail pours (estimate) under planned 150 menu at medium/spread — baths2 ~124.6 vs menu 150 (delta −25.4). Menu remains **confirmed**; Studio `MIX` still models dispenser share as former “jj” ratio — Claude may want SoT note that lemonade/paloma map onto that share until Studio copy is updated.
- Cap 70: brief says confirmed 20 Oct; SoT/AGENTS still mention working cap ~50 / under review — Claude to reconcile.

## Questions for Jovanni
1. Merge root `AGENTS.md` standing orders permanently, or keep Claude-only filing?
2. Update Studio UI copy from “jungle juice” → lemonade/Paloma (code still uses `serves:'jj'` internally)?
3. Cap for night-of: **70 confirmed** (brief 20 Oct) vs living-room ~50 working — which number for ops panel defaults?
4. `SOFTWARE_SPEC.md` not found in repo (searched workspace + ops branches) — where should Night-Of Ops Vite PWA spec live?

## Receipt
- seat: cursor · model: Composer · ts: 2026-10-20T16:23:51Z  
- input: `_err.py`, studio consumers, DRIVE_INDEX, kickoff brief  
- output: `orch/tasks/outbox/T-015_result.md` · branch `cursor/t015-t2-rebuild` · `_t2.py` blob `3db1a23…`
