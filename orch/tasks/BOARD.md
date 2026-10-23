# BOARD — updated Fri 16 Oct 2026 · acting gist Tue 20 Oct 2026 · Claude Code consolidation Fri 23 Oct 2026 (7 days to doors)

## FACT / PATCH_SUMMARY (~100 tokens · AGENT_COMMS-style)
**FACT:** Cursor **acting orchestrator** (Claude chat+Code OOO through Fri 30 Oct). Backend T-018 merged to default `claude/motion-files-consolidated-dx17w2` @ `06890c5` (fold `fc419bb`, tip `9799bb6`); pytest 8/8. T-003 RECORD: metrics+SoT → pool $381.13 / buffer $68.87 (est), cap 70 (conf), DJ $475 (conf, brief-only pointer); Pip verify OPEN. T-011 VAMP midset PREP only. T-001 Fri 23 Oct tape support note filed. No spend/send/post. Abraham **T-013 untouched**.

| ID | Task | Owner | Status |
|---|---|---|---|
| T-001 | After the 16 Oct visit: enter kitchen/hall + DJ-wall measurements in Room Studio, rerun full sim (1 vs 2 baths, early/spread/late × light/med/heavy), update DEFAULT_LAYOUT + report | Codex | blocked: venue visit moved; **prep** `outbox/T-001_friday_venue_tape_support.md` (tape target Fri 23 Oct) |
| T-002 | Rebuild budget workbook with live ✓ prices, Rohan removed, +extra alcohol option; reconcile with Logistics Control "Budget" tab | Codex | ready |
| T-003 | Audit Drive sheets (Master Planning, Logistics Control, 01–05 planning) vs SoT; list contradictions | Gemini | ready · **acting RECORD cleanup done** (`outbox/T-003_sot_cleanup_changelog.md`) — **Pip verify OPEN** |
| T-004 | Review Higgsfield shots / reel against Playbook checklist | Gemini | needs clips from Jovanni |
| T-005 | Draft: Glamz confirmation text, neighbour flyer note, IG caption set (no Rohan) | ChatGPT | ready |
| T-006 | Pricing check: extra alcohol carts (Austin), ice, Sam's/Costco | ChatGPT | ready |
| T-007 | Promo pass after Glamz answers (flyer v5, post 5, reel) | Claude (+Gemini review) | blocked on Glamz |
| T-008 | Decorating + art plan, agent design review first | Claude | next |
| T-009 | Re-run Studio drink-spot/stock sims for the 150-cocktail menu (lemonade + paloma, dispensers/bulk) — menu confirmed 16 Oct | Codex | ready |
| T-010 | Flyer v5 vs v4: find out what v5 is (Glamz LATIN · TECH HOUSE row) and reconcile with lineup | Claude | open |
| T-011 | Lineup lock / VAMP mid-set if schedule fits (Jovanni standing intent) | Jovanni (+acting prep) | **PREP only** — `outbox/T-011_prep_vamp_midset.md`; blocked on VAMP reply |
| T-013 | (Abraham) | Abraham | **do not renumber / do not touch** |
| T-018 | Backend reconcile → merge FastAPI `services/api` + `/api/data/*` | Cursor (acting) | **merged** to default @ `06890c5` — `outbox/T-018_merge_receipt.md` |

## Claude Code consolidation · Fri 23 Oct
Ready-to-paste prompts: `orch/tasks/PROMPTS_23OCT.md`. A daily check-in at 8:52 AM Austin time pulls RSVPs and refreshes this section.

### Decisions waiting on Jovanni
| ID | Decision | Why it blocks |
|---|---|---|
| D-1 | **The $175 slot.** DJ fees of $475 were recorded as committed on 20 Oct (HE//THEY $300 + $175). Jovanni said on 19 Oct that **Rohan Rali is back at $175 for 11:00–12:15**, but that is **Glamz's confirmed slot** (he plays free). Options: Rohan takes it and Glamz moves to the 9 PM b3b; Rohan gets another slot; or Rohan stays out. The SoT still says "Rohan is off". | Set times, promo (no unconfirmed names), camera money (it came from Rohan's cut) |
| D-2 | Who pays the CDJ rental ($345, confirmed quote)? | Budget |
| D-3 | Approve matchbox v2 (`media/merch/matchbox/`) before ordering. Express is needed to arrive Tue 27 Oct. | Merch arrives in time |
| D-4 | Buy the 5 Fujifilm cameras and pick a developing lab | Camera program |

### Money update (19–23 Oct, from Jovanni)
| Item | Amount | Label |
|---|---|---|
| Pool, now 3 × $166 = **$498** (was 3 × $150 = $450) | | confirmed (plan) |
| Haven $166 | received | confirmed |
| Alex $166 / Jovanni $166 | promised | open |
| Pool spend (T-003 live figure) | $381.13 | estimate |
| **Buffer with $498** | **$116.87** | estimate |
| Merch: Cap 01 | cut | confirmed |
| New merch: artist towels, stickers, matchboxes (released after the event) | ~$200–310 | estimate |
| Matchboxes ×100 (Zazzle, 15% code) | $73.02 + shipping | confirmed at design time |

### RSVPs (Tally, 23 Oct): **20 unique · 49+ heads** · last RSVP Tue 20 Oct (Aryan submitted twice; counted once) · cap 70

### New tasks
| ID | Task | Owner | Status |
|---|---|---|---|
| T-019 | Matchbox v2: build in the Zazzle customizer from `media/merch/matchbox/BUILD_SPEC_v2.md`, then send the proof to Jovanni. **Don't check out.** | Pip | ready |
| T-020 | Artist towels ×6–7: a printed order was due about 22–23 Oct; otherwise DIY fallback | Jovanni | **late: decide today** |
| T-021 | Post the b2b reel + mood board edit (RSVP push) | Jovanni | ready |
| T-022 | SoT update: pool $498 (Haven paid), merch change, D-1 outcome | Claude chat | waiting on D-1 |
| T-023 | Group-size DMs: Johan "6+", Aamer 5 (drafts: ChatGPT prompt) | Jovanni | ready |
