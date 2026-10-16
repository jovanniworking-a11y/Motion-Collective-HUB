# AGENTS.md — MOTION · Devil's Night · AFTERIMAGE 001 (for Codex and any coding agent)

You are a **worker**. Claude is the orchestrator. Read `README_ORCHESTRATION.md` first, then take your task from `tasks/inbox/`. Put results in `tasks/outbox/`. Do not edit `context/`.

## The project in 10 lines
- MOTION is a six-friend Austin party collective (creative director Jovanni; PM Alex; Haven). First event: **Devil's Night · AFTERIMAGE 001**, **Fri 30 Oct 2026**, doors 9 PM, hard stop 2 AM, in a **Rio 3BD/2BA apartment**, invite-only, **70 numbered passes** (cap under review — living room measured 14 ft × 18 ft 1 in = 253 sq ft; working cap ~50).
- Crowd: **UT Austin college students** — liberal on smoking (balcony cannabis/cigs, free cigs outside, vapes OK inside), part BYOB, arrivals/drinking pace unknown for a first event.
- Lineup: **HE//THEY** (headliner, $300, confirmed), opener slot open (Rohan Rali cut 14 Oct), **Glamz** unconfirmed; local friends set iamariology b2b raymixes.
- Money: pool $450 (Jovanni/Haven/Alex $150 each); DJs paid by Jovanni; CDJ-2000NXS2 ×2 + DJM-900NXS2 rented from Rock n Roll Rentals $345. Gear/lighting PA from Rapid Ric (unconfirmed list).
- Brand: night #060B13, ice #BFDDF0 / #58C4F0, red #FF3B30 (accent ≤10%), oxblood #A13B42. Type: Bodoni Moda (set opsz) + Jost.
- Full facts: `context/SOURCE_OF_TRUTH_latest.md` (wins on conflicts), then `context/project_docs/`, `context/drive/`.

## Your main code asset: the Room Studio
`context/studio/index.html` — single-file three.js r147 app (published at https://claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV). Real Rio geometry (plan px, `FT_PX=0.875/12`; tape: DJ wall = 14 ft), 0.5 ft nav grid, agent-based crowd sim (Dijkstra), ±5% @95% CI pipeline (`screen`/`refine`/`markTies`, seeds `1000+k*7919`, MIN_RUNS 5, MAX_RUNS 30), sound model, flow-arrow overlay, 9-chapter "night tour", optimizers (`optimizeSound`, `optimizeDrinksCore`, `optimizeBins`, `optimizeBallCore`, `optimizeEverything`).
- Locked defaults live in `DEFAULT_LAYOUT` (DJ rig, drink dispensers on island, cooler/cart upper-right, bins incl. counter bins, ball hook above DJ). localStorage key `afterimage-studio-v8`.
- Crowd profile `SCEN`: smoke 0.5, balcony gap 25–45 min, arrivals early/spread/late, drinks light/medium/heavy, baths 1|2 (Bed 3 bath at plan [640,214], +20 s walk).
- **Tests:** Playwright + Chromium (SwiftShader). Scripts in `context/studio/` (`_all2.py <baths>`, `_night2.py`, `_err.py`, `test_studio.py`). Swap the CDN three.js for a local build when testing offline. Don't run `playwright install`; use the preinstalled Chromium.
- Gotchas learned: never put a `//` comment inside a one-line object literal; ball optimizer must not skip odd grid cells; judge bins over the **whole night**, not the 45-min peak.

## Decisions already made (don't relitigate)
Square-to-wall + locked placements (no arbitrary rotation) · DJ table on the long left wall toward the balcony end · eye-triptych wall behind DJ · drinks served from the island · **Bed 3's bath opens to guests** (avg restroom wait ~25 → ~2 min) · trash/recycling pairs: floor by island + counters (low counter, stove) — no bin by the front door · mirror ball **hung** (anchor TBD, never Command hooks) · hall opening kept clear for the guest bath.

## Open items you may be asked about
Glamz fee/availability; opener slot 9:30–11 PM; costume prize amount; artists' clips; Rapid Ric cables + lights; Cap 01 colourway + quotes; capacity after the **16 Oct kitchen+hall measurement** (also tape the DJ wall and recalibrate the Studio); mirror-ball rigging; **re-run budget workbook** with live prices; proposed extra alcohol (~$97 w/ tax: 3rd vodka JJ, 2nd Miller Lite 30-pk, 2nd White Claw 24-pk, +~$6 ice) — unconfirmed; to verify on site: Bed 3 door position, Bed 3 occupant consent, front-door location, 9 ft ceiling.

## Output format
Result file `tasks/outbox/T-###_result.md`: what you did · files produced (paths) · how you verified · **Proposed SoT changes** · questions for Jovanni. Keep it short.
