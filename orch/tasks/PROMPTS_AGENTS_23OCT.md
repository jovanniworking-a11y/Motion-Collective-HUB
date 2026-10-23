# What to tell every agent · Fri 23 Oct 2026 (7 days to doors)
Copy the **Facts block** first, then that agent's block. Every agent: drafts only, never spend / send / post / publish, no guest names (pass numbers only), no venue address, label every number confirmed / estimate / open.

---
## Facts block (paste into every agent first)
```
MOTION · Devil's Night · AFTERIMAGE 001 · Fri 30 Oct 2026 · doors 9 PM, last entry 12:30, last pour 1:45, hard stop 2 AM · invite-only, 70 numbered passes (001–070), cap 70 (confirmed).
Lineup (locked, no set times on promo): iamariology b2b raymixes → Rohan Rali b2b Shubh Samtani (11:00 PM–12:15 AM) → HE//THEY · co.b b2b NiiON (credit exactly). Glamz canceled 20 Oct — that name goes in no copy.
Money: DJ fees $475 confirmed = HE//THEY $300 + Rohan $175 (Shubh Samtani unpaid), paid by Jovanni. CDJs $345 confirmed, paid by Jovanni. Pool $498 = 3 × $166 (Haven received; Alex + Jovanni promised). Pool spend $381.13 estimate, buffer $116.87 estimate. Retired, never quote: pool $450, buffer $68.87, $391.42, $171.88, $58.58.
Approved 23 Oct: matchbox v2 ×100 (Express), 5 Fujifilm disposable cameras (lab: Lago Vista Film Lab). Cap 01 cut; towels/stickers/matchboxes release after the event.
Code: everything is on main (repo jovanniworking-a11y/Motion-Collective-HUB). Lock file: orch/context/CURRENT_LOCK.md wins over older docs. Board: orch/tasks/BOARD.md (task IDs are never reused; new ones start at T-041).
Rules: drafts only; no spend/send/post/publish without Jovanni; no guest names or venue address anywhere; label numbers confirmed/estimate/open; red is an accent only, never a tint.
```

---
## → Cursor (code seat)
```
Claude Code is back. Your acting-orchestrator role ends; Claude chat owns the SoT again. Pull main. It now has: the 2FA login (panel + API, fails closed on Vercel), CI (.github/workflows/ci.yml: API on SQLite + Postgres, live-ops tests, panel typecheck/lint/unit/build/e2e), the Live Ops desk (PR #9), Jerry's occupancy bridge (PR #10, files were base64 — now decoded, mock added), cap 70 everywhere, money from the 23 Oct lock, ops/RUNBOOK.md.
PR #7 (counts-only occupancy pipeline) is superseded by #9/#10 — close it with a one-line note, don't merge.
Your queue, one cursor/<task> branch each, merged only when CI is green:
T-041 Live Ops desk: when the counter service is offline, show "Counter offline — use the door phone" in one line (no dashes in every tile). Add a Playwright test.
T-042 Phone width: the bottom nav has 10 items; at 390 px make the active item scroll into view and keep 44 pt targets. Screenshot 390 px + 1280 px in the outbox.
Write orch/tasks/outbox/T-0xx_result.md for each. Never deploy; Jovanni does.
```

## → Grok · Jerry (backend, FORGE lane)
```
Status 23 Oct: your occupancy bridge + zone counter are merged to main (live-ops/counter/). The four files arrived base64-encoded in the repo — Claude Code decoded them and wrote the missing mock_occupancy_api.py and tests/conftest.py; 55 live-ops tests pass. Next:
1. Send the zone_counter tests you mentioned (fake detector, zone assignment, window stats, CSV schema). They are not in the repo. Plain text files, not base64.
2. Fader engine: confirm live-ops/fader/server.py meets your spec (−3 dBFS tanh limiter, 1 Hz peak meter over WebSocket). Write the physical bypass doc as live-ops/fader/BYPASS.md (DJM Booth Out → PA direct, 30-second restore).
3. Mark every hardware test HANDS-ON 29 OCT. Gist ≤150 tokens: LANE/backend, DONE/BLOCKED, files, test result, open questions.
```

## → Grok · Chaka (frontend, LUMEN lane)
```
Status 23 Oct: the Live Ops desk (/live-ops), HQ dashboard (/hq) and browser counter (/counter-demo) are merged to main inside the ops panel, behind a 2FA login. The LAN dashboard is live-ops/dashboard/index.html (door view ?view=door). Next:
1. Door view: giant occupancy n/70, SPACE LEFT, one action ("Hold the door — at cap"), colour + icon + text for every state. ≥44 pt, no typing.
2. Fader iPad UI (live-ops/fader/index.html): one big fader, peak meter, a locked "bypass" instruction card.
3. TouchDesigner: follow live-ops/touchdesigner/NETWORK.txt; dark, monochrome, red ≤10%, never a red tint. 1280×1280 free-license cap.
Return complete files with paths, plain text (no base64). Gist ≤150 tokens.
```

## → Grok · Bartholomew (auditor, LEDGER lane)
```
Your money context is stale: the pool is now $498 (3 × $166), not $450; buffer $116.87 estimate; DJ fees $475 paid by Jovanni outside the pool; CDJs $345 outside the pool. Re-run audit 3 with these and say whether the "$148.52 over" projection still holds and what it includes (label each number).
Then audit 2 on what merged 23 Oct: live-ops/counter (tripwire, zone counter, bridge with retry/dead-letter), live-ops/fader, live-ops/dashboard, apps/ops-panel /live-ops. Rank by "what breaks first at midnight". Write live-ops/audits/AUDIT_23OCT.md only. Never write code.
```

## → Muse (Room Studio / sims · worker: Codex on Jovanni's PC)
```
Cap is 70 (confirmed). Drinks menu is the 150-cocktail plan (90 lemonades + 60 Palomas, dispensers on the island).
1. T-009: re-run the Studio drink-spot and stock sims for the cocktail menu at 70 guests (early/spread/late × light/medium/heavy). Report pours needed vs 150 stocked and the line at the island.
2. T-001: when the kitchen/hall and DJ-wall tape lands, enter it in the calibrate box and re-run the full sim; say whether 70 still holds (~4.8 sq ft walkable each today, estimate).
3. Post locked sim results through POST /api/data/sim_runs (insert-only) so the panel's Data page can compare them with night-of counts.
Counts and zones only — no faces, no names. Result → orch/tasks/outbox/T-009_result.md.
```

## → Codex (Jovanni's PC)
```
Pull main.
T-039: in apps/ops-panel run npm ci; from the repo root start the API (python -m uvicorn app.main:app --app-dir services/api --port 8787), the panel (npm run dev in apps/ops-panel) and the desktop shell (npm run desktop). Confirm: the window loads the panel; /night-of works with Wi-Fi off; ops/index.html opens on a phone on the same network.
T-002: budget workbook v2 (prompt in orch/tasks/PROMPTS_23OCT.md) — use pool $498, DJ $475 (HE//THEY $300 + Rohan $175, Shubh unpaid), CDJs $345 by Jovanni.
Result → orch/tasks/outbox/T-039_result.md. Don't commit .env or guest data.
```

## → Pip (coordination desk)
```
1. Matchbox v2 is approved: build from media/merch/matchbox/BUILD_SPEC_v2.md, check the proof, order 100 with Express (arrive Tue 27 Oct). Ask Jovanni first if the total is over $100.
2. When you push code, push plain files, never base64 — Jerry's bridge landed encoded and had to be decoded.
3. Verify the 23 Oct lock section in orch/context/CURRENT_LOCK.md at the hub, then close your T-003 verify flag.
4. Tell the Grok bots the new facts block above (Jerry, Chaka, Bartholomew).
```

## → Claude chat ("MOTION EFFEcts")
```
Record the 23 Oct decisions in the Source of Truth body (already in orch/context/CURRENT_LOCK.md): Glamz canceled 20 Oct; Rohan Rali b2b Shubh Samtani 11:00 PM–12:15 AM; Rohan $175 (replaces the 21 Oct "no fee"); Shubh Samtani unpaid; DJ $475; pool $498 (Haven paid; buffer $116.87 est); CDJs $345 by Jovanni; matchbox v2 + 5 cameras approved; Cap 01 cut; post-event merch. Then run the promo pass: flyer, post 5 and the reel still show the canceled act — one pass with the locked lineup, no set times.
```

## → ChatGPT (copy)
```
Drafts only. (1) Neighbour note for Fri 10/30, ends by 2 AM, contact number ____ (no address). (2) Three IG captions for the lineup post: iamariology b2b raymixes → Rohan Rali b2b Shubh Samtani → HE//THEY · co.b b2b NiiON. No set times, no canceled names, max 5 hashtags, RSVP link in bio. (3) Two short texts to the group leads who RSVP'd "6+" and 5 asking for final headcounts by Mon 26 Oct.
```

## → Gemini (video / sheets)
```
(1) Review the b2b reel (FINAL v10) against the Agent Playbook: equal stars for iamariology and raymixes, red never tints footage, no canceled act anywhere, nothing cut off at the edges. (2) Audit the Drive sheets against the facts block and list every row that still says pool $450, buffer $68.87, Rohan cut / no fee, or names the canceled act (sheet · cell · says · should say). Report only.
```
