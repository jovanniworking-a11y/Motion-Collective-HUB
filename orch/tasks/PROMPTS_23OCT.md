# Prompts to send · 23 Oct (copy each block into the named bot)
Rules that ride along with every prompt: never put the venue address anywhere; no unconfirmed names on promo; label every number confirmed / estimate / open; drafts only, nothing gets sent or bought.

---
## → ChatGPT · T-005 drafts (texts + DMs)
```
Write short, warm, casual texts (lowercase ok, no hashtags) for a private Austin house party "Devil's Night · AFTERIMAGE 001" on Fri 10.30.26. Never mention an address. Give 2 options each:
1) To Johan: he RSVP'd "6+" — ask for the exact headcount and names of his group by Mon 26 Oct.
2) To Aamer: confirm his group of 5 is still coming.
3) Donation DM to close friends: raising ~$350–500 for DJs, film cameras and drinks; tiers $20 supporter / $50 inner circle / $100+ founding friend; Venmo @____ (Friends & Family). No "ticket" wording.
4) Thank-you text to Haven for chipping in $166.
5) Neighbour note (printed, slid under doors): heads-up about a get-together Fri 10/30, ends by [time], contact number ____ if anything's too loud.
Keep each under 60 words.
```

## → ChatGPT · T-006 full price check
Use the full prompt sent on 20 Oct (drinks, decor, smoking, CDJs, cameras, merch, food). Paste its answer back into the Claude Code session.

## → Gemini · T-003 Drive audit
```
Open my Google Drive sheets: "Master Planning", "Logistics Control" (esp. the Budget tab) and the 01–05 planning sheets. Compare them to these current facts and list every contradiction as a table (sheet · cell/row · says · should say):
- Event: Devil's Night · AFTERIMAGE 001, Fri 30 Oct 2026, doors 9 PM, invite/RSVP only
- Lineup order: iamariology b2b raymixes (9 PM) → Glamz (11:00–12:15, plays free) → HE//THEY · co.b b2b NiiON (12:15 AM). Rohan Rali: cut 14 Oct (possible return under discussion — flag any row that names him)
- Pool: $498 = Haven $166 (paid) + Alex $166 + Jovanni $166
- DJs paid by Jovanni: HE//THEY $300
- CDJ rental $345 (2× CDJ-2000NXS2 + DJM-900NXS2, Rock n Roll Rentals)
- Merch: Cap 01 cut; new = artist towels, stickers, matchboxes (released after the event)
- No drink sales, no collection
Do not edit anything — report only.
```

## → Codex (Jovanni's PC) · T-002 budget workbook
```
Open MOTION_Budget_and_Carts.xlsx. Update it, keeping every formula live (no hardcoded totals):
1) Pool = 3 × $166 = $498 (Haven paid; Alex and Jovanni pending — add a "status" column).
2) Use the live 150-cocktail menu figures from SOURCE_OF_TRUTH_latest.md (Reconciled 20 Oct: drinks $231.13, pool spend $381.13).
3) Remove Cap 01 merch. Add a Merch tab: towels ×7, stickers ×100, matchboxes ×100 ($73.02 confirmed + shipping open), each with a label column (confirmed/estimate/open).
4) DJ line = $475 committed (HE//THEY $300 + $175 open split); add a note cell for the D-1 slot decision.
5) Summary: pool spend vs $498, buffer, Jovanni's personal total, donation gap.
Save as MOTION_Budget_v2.xlsx next to the original. Don't commit guest data anywhere.
```

## → Claude chat ("MOTION EFFEcts") · D-1 + T-014
```
Decided 23 Oct: Rohan Rali is back at $175 (confirmed). Still open: his slot. He asked for 11:00–12:15, which is Glamz's confirmed slot (plays free). Lay out the slot options (Rohan takes 11:00–12:15 and Glamz moves to the 9 PM b3b / Rohan opens before the b2b / Rohan closes after HE//THEY) with impact on set times, DJ spend (HE//THEY $300 + $175?), the camera money that came from Rohan's cut ($275 saved), and promo. Recommend one. Also record: CDJ rental $345 (confirmed), matchbox v2 approved, 5 Fujifilm cameras approved (lab: Lago Vista Film Lab). Note: on 20 Oct the acting orchestrator recorded DJ fees committed at $475 (= HE//THEY $300 + $175, split marked open) — reconcile that with whatever I pick. Then update the SoT money section: pool now $498 (3 × $166, Haven paid; spend $381.13 est → buffer $116.87), Cap 01 merch cut, new merch (towels/stickers/matchboxes, est. $200–310).
```

## → Pip · T-019 matchbox
Jovanni **approved v2 on 23 Oct**. Build from `media/merch/matchbox/BUILD_SPEC_v2.md` using the three PNGs in that folder. Match Zazzle's face template size first. Check the proof against the spec (striker strip clear, type sharp at 6–7 pt). Then order 100 with **Express** (arrive by Tue 27 Oct) using the 15% code. If the total is over $100, ask Jovanni before paying.

## → Cursor · MOTION Ops dev work (T-024 to T-027, T-029)
Full brief: `orch/tasks/inbox/DEVOPS_23OCT.md`. Paste:
```
You're a worker on MOTION Collective HUB. Read AGENTS.md, ARCHITECTURE.md and orch/tasks/inbox/DEVOPS_23OCT.md. Do T-024, then T-025, T-027, T-029, then T-026, in that order, each on its own cursor/<task> branch, merged into claude/motion-files-consolidated-dx17w2 only when tests pass. Write a T-###_result.md in orch/tasks/outbox/ for each. Never deploy, spend, send or post. No guest PII, no venue address.
```

## → Codex (Jovanni's PC) · T-028 desktop
```
Pull claude/motion-files-consolidated-dx17w2. In apps/ops-panel run npm ci (the lock file was re-synced on 23 Oct), then from the repo root start the API (python -m uvicorn app.main:app --app-dir services/api --port 8787), the panel (npm run dev in apps/ops-panel) and the desktop shell (npm run desktop). Confirm: the desktop window loads the panel; /night-of works with Wi-Fi off; ops/index.html opens on a phone on the same network. Write the result (what worked, any errors verbatim) to orch/tasks/outbox/T-028_result.md. Don't commit .env or guest data.
```
