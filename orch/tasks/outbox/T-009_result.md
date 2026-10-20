# T-009 result — drink-spot / stock sims (150-cocktail menu)

**Seat:** cursor · **Timestamp:** 2026-10-20T16:23:51Z · **Branch:** `cursor/t015-t2-rebuild`  
**Inputs:** `orch/context/DRIVE_INDEX.md` (90 lemonade + 60 Paloma, confirmed 16 Oct), `orch/context/studio/index.html` (`MIX`, `optimizeDrinks`), T-015 `_t2.py` boot.  
**Output:** `orch/context/studio/_t009_drinks.json` · logs under `orch/tasks/outbox/_t009_*`.

## What done
- Ran `optimizeDrinks()` (SwiftShader) — winning layout: dispensers on island · beer upper-right · White Claw cart upper-right. Score 55.81 ±4.6% @ n=5 · **ok** (ci within ±5%).
- Mapped MIX.jj=0.60 dispenser share → lemonade/paloma 90/60 for stock estimates (geometry model unchanged).
- `nightStats(20)` baths 1|2, arr=spread, drinks=medium.

## Stock plan (estimate)
| Baths | Our pours | Cocktail pours (→ lem/pal) | Beer | Seltzer | vs menu 150 |
|---|---|---|---|---|---|
| 1 | 184.1 | 110.5 (66.3 / 44.2) | 40.5 | 33.1 | delta −39.5 |
| 2 | 207.8 | 124.6 (74.8 / 49.9) | 45.7 | 33.1→37.4 | delta −25.4 |

Menu counts **confirmed**; sim pours **estimate**. Source: `_t009_drinks.json`.

## Proposed SoT changes
- Record drink-spot winner (island dispensers) as current Studio default already matches island jj.
- Flag that planned 150 cocktails > medium/spread sim cocktail pours — buffer or heavier profile TBD by Jovanni.

## Questions
- Re-run with drinks=heavy / arr=early before locking buy list?
- Treat menu 150 as hard stock (confirmed) and ignore lower sim mean?

## Receipt
cursor · Composer · 2026-10-20T16:23:51Z · in: DRIVE_INDEX + studio · out: `_t009_drinks.json`
