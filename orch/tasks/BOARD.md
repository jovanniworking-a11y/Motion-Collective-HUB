# BOARD — updated Fri 23 Oct 2026 (main's 21 Oct lock merged with Jovanni's 23 Oct decisions · 7 days to doors)
**Read first:** `orch/context/CURRENT_LOCK.md` (lineup + money in force). Task IDs are never reused: T-019–T-022 are main's 21 Oct results in `outbox/`; Claude Code's 23 Oct tasks are T-030+.
| ID | Task | Owner | Status |
|---|---|---|---|
| T-001 | After the venue visit: enter kitchen/hall + DJ-wall measurements in Room Studio, rerun full sim (1 vs 2 baths, early/spread/late × light/med/heavy), update DEFAULT_LAYOUT + report | Codex | blocked: venue visit moved, date TBD |
| T-002 | Rebuild budget workbook with live prices. Rohan Rali is on the lineup at no fee (21 Oct), so his DJ fee stays out. Reconcile with Logistics Control "Budget" tab | Codex | ready |
| T-003 | Audit Drive sheets (Master Planning, Logistics Control, 01–05 planning) vs SoT; list contradictions | Gemini | ready |
| T-010 | Flyer v5 vs v4 Glamz row | Claude | closed 21 Oct: Glamz canceled 20 Oct. Do not bill her |
| T-011 | Lineup lock / VAMP mid-set if schedule fits (Jovanni standing intent) | Jovanni (+acting prep) | **PREP only** — `outbox/T-011_prep_vamp_midset.md`; blocked on VAMP reply |
| T-013 | (Abraham) | Abraham | **do not renumber / do not touch** |
| T-018 | Backend reconcile → merge FastAPI `services/api` + `/api/data/*` | Cursor (acting) | **merged** to default @ `06890c5` — `outbox/T-018_merge_receipt.md` |
| T-019–T-022 | Link audit, hygiene scan, API seat, lineup lock (21 Oct) | Cursor | done · see `outbox/T-019_result.md` … `T-022_result.md` |

## 23 Oct · Jovanni's decisions (recorded by Claude Code)
| ID | Decision | Status |
|---|---|---|
| D-1 | **Rohan Rali (b2b Shubh Samtani) plays 11:00 PM–12:15 AM; Rohan is paid $175** (confirmed 23 Oct, replaces the 21 Oct "no fee"). DJ fees $475 = HE//THEY $300 + Rohan $175. Glamz canceled 20 Oct, so no slot to fill. Shubh Samtani is not paid (23 Oct). | **decided** |
| D-2 | CDJ rental **$345, paid by Jovanni**, outside the pool. | **decided** |
| D-3 | **Matchbox v2 approved.** Pip builds it, checks the proof, orders with Express (T-030). | **approved** |
| D-4 | **Buy the 5 Fujifilm QuickSnaps.** Lab: Lago Vista Film Lab, about 1-hour C-41 (confirm hours). | **approved** · buyer Jovanni |

### Money (19–23 Oct, from Jovanni)
| Item | Amount | Label |
|---|---|---|
| Pool, 3 × $166 (was 3 × $150) | **$498** | confirmed (plan) |
| Haven $166 | received | confirmed |
| Alex $166 / Jovanni $166 | promised | open |
| Pool spend | $381.13 | estimate |
| **Buffer with $498** | **$116.87** | estimate |
| Merch: Cap 01 | cut | confirmed |
| New merch: artist towels, stickers, matchboxes (released after the event) | ~$200–310 | estimate |
| Matchboxes ×100 (Zazzle, 15% code) | $73.02 + shipping | confirmed at design time |

### RSVPs (Tally, 23 Oct): **20 unique · 49+ heads** · last RSVP Tue 20 Oct · cap 70

### 23 Oct tasks
| ID | Task | Owner | Status |
|---|---|---|---|
| T-030 | Matchbox v2 (**approved 23 Oct**): build in Zazzle from `media/merch/matchbox/BUILD_SPEC_v2.md`, check the proof against the spec, then order 100 with Express (about $73.02 + shipping). Ask Jovanni first if the total goes over $100. | Pip | **go** |
| T-031 | Artist towels ×6–7: options in the 23 Oct chat (Custom Ink 3-day Super Rush, or blank black towels plus a same-day DTF print at ATX DTF Printing) | Jovanni | **pick a vendor today** |
| T-032 | Post the b2b reel + mood board edit (RSVP push) | Jovanni | ready |
| T-033 | SoT update: pool $498 (Haven paid), merch change, Rohan back at $175, cameras and matchbox approved | Claude chat | ready (slot still open) |
| T-034 | Group-size DMs to the two group leads ("6+" and 5) (drafts: ChatGPT prompt) | Jovanni | ready |
| T-035 | MOTION Ops · CI: `.github/workflows/ci.yml` (API pytest on SQLite + Postgres; panel ci, typecheck, lint, vitest, build, e2e, login e2e) | Claude Code | **done 23 Oct** |
| T-036 | MOTION Ops · Night-Of readiness: cap 70, offline door, lineup + money from CURRENT_LOCK, Playwright e2e | Claude Code | **done 23 Oct** · `outbox/T-035_T-040_result.md` |
| T-037 | MOTION Ops · Login with 2FA (password + authenticator code) on panel and API, fails closed on Vercel. Setup: `apps/ops-panel/DEPLOY_LOGIN.md` | Claude Code → **Jovanni sets the Vercel env vars** | built 23 Oct · waiting on env vars |
| T-038 | MOTION Ops · Metering tests, money facts refreshed, current model IDs | Claude Code | **done 23 Oct** |
| T-039 | MOTION Ops · Desktop on Jovanni's PC: install, `npm run desktop`, confirm it loads the panel and works offline | Codex | ready |
| T-040 | MOTION Ops · Night-of runbook `ops/RUNBOOK.md` | Claude Code | **done 23 Oct** |
| T-041 | Live Ops desk: one-line "Counter offline — use the door phone" state + Playwright test | Cursor | ready |
| T-042 | Bottom nav at 390 px: active item scrolls into view, 44 pt targets, screenshots | Cursor | ready |

### 23 Oct · code status (Claude Code)
- Merged into the working branch, then into `main`: PR #9 (Live Ops desk, cap 70) and PR #10 (Jerry's occupancy bridge — files were base64, decoded; mock + conftest added). PR #7 is superseded by #9/#10 (close, don't merge). PRs #8 (matchbook plates, superseded by matchbox v2), #5 (log stamp) and #1 (Mochi sims/ops drafts) stay open for their owners.
- Agent prompts: `orch/tasks/PROMPTS_AGENTS_23OCT.md`.
