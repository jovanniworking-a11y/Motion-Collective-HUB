# MOTION: hospital-style org chart and routing table (DRAFT for Jovanni)
Draft, 19 Oct 2026. Nothing is changed in the repo. Following the repo rule, this is a "Proposed SoT changes" document: Claude chat merges and Jovanni approves.

## 1. The model in one picture
```
                 JOVANNI: CEO / Chief of Medicine (final say: money, publishing, names)
                                   │
          ┌────────────────────────┼─────────────────────────┐
   ALEX: human PM / run of show     │                  HAVEN / crew: floor staff
   (the night, load-in/out)         │                  (vendors: Rapid Ric, door, welfare)
                                   │
        CLAUDE CHAT: Attending / Chief of Staff (orchestrator)
        owns the chart (Source of Truth), triage, decisions, review/sign-off
                                   │
   MOCHI: Charge Nurse + Unit Clerk (ops desk: clock, inbox, board, discharge/debrief)
                                   │
 ┌───────────┬────────────┬────────────┬─────────────┬───────────────┬──────────────┐
 Claude Code  Codex        ChatGPT      Gemini        Media tools      Grok web chat
 Health IT &  Lab/Imaging  Comms &      Radiology/    (Higgsfield,     (optional
 Records      (PC sims,    Pricing      QA & Audit    Adobe Express)   research seat)
 (repo/hub)   workbooks)                              operated by Jovanni
```
**How it works, in hospital terms:**
- **Specialists lead their own cases.** Each bot owns one department and only that department. It works from a brief (`T-###.md`) and returns a result (`T-###_result.md`) with "Proposed SoT changes" and "Questions for Jovanni".
- **Anyone can suggest.** Any bot can file a **consult**: a "Proposed change" section in its result.
- **Consults go up through the desk.** Mochi collects every consult into the "Decisions to lock" list. Claude chat triages it. Jovanni signs.
- **One chart.** Only Claude chat writes the Source of Truth. Everyone else reads it.

## 2. Routing table: one owner per responsibility
| Responsibility | Single owner | Backup / reviewer | Notes / overlap resolved |
|---|---|---|---|
| Final approval: spend, send, post, name a person | **Jovanni** | — | Unchanged hard rule |
| Night-of run of show, load-in/out, crew briefing | **Alex** (human) | Mochi keeps the checklist | Per SoT:45 + Run of Show |
| Source of Truth edits, decisions, design review, triage of consults | **Claude chat** | — | Unchanged (orch/CLAUDE.md) |
| **Gmail / Drive / Calendar *lookups* for decisions** | **Claude chat** | Mochi for inbox/calendar *monitoring* | **Resolves A1:** remove "Drive/Gmail/Calendar lookups" from Claude Code (CLAUDE.md:8) |
| **Calendar / deadline layer:** countdown, reminders, nags | **Mochi** | Claude chat | Fills gap A4. Mochi drafts reminders; sending to crew needs Jovanni's OK until a standing rule exists |
| **Inbox + RSVP watching:** Glamz, Rapid Ric, vendors, Tally count | **Mochi** (once Gmail/Tally are readable) | Claude chat decides | Fills gap A5. Mochi flags; it never replies on its own |
| **Status desk:** keep BOARD.md + web hub tasks in sync, list brief drift | **Mochi** (drafts the diff) → **Claude Code** commits | Claude chat approves | Fixes the two-boards problem (gaps B3) |
| Brief maintenance (AGENTS/GEMINI/ChatGPT/README tables) | **Claude chat** decides the text · **Claude Code** commits | Mochi audits weekly | Fixes A7 drift |
| Repo, `hub.py`, `web/`, `site/`, GitHub, repo hygiene/visibility | **Claude Code** | — | |
| In-repo media renders (montages, flyers from source, sting, FX) | **Claude Code** | Gemini QA | Matches commit history |
| **Room Studio code + sims (T-001, T-009)** | **Codex** | Claude Code only if Codex is unavailable | **Resolves A2.** Matches AGENTS.md, README_ORCH:30, registry owners. Remove "Room Studio changes" from CLAUDE.md:8 |
| **Budget workbooks / builders (T-002)** | **Codex** | Mochi checks totals against the SoT | **Resolves A2.** Remove "spreadsheets/builders" from CLAUDE.md:8 |
| PC-only files, learning lab | **Codex** | — | Unchanged (CLAUDE.md:47) |
| Copy: captions, DMs, artist texts, RSVP copy | **ChatGPT** | Claude chat review | |
| **Vendor and price checks** (with URLs, confirmed/estimate) | **ChatGPT** | Mochi web-checks spot prices | **Resolves A3:** remove "vendor pricing" from GEMINI.md:5 |
| Media QA against the Playbook (reels, Higgsfield clips, flyers) | **Gemini** | — | |
| Drive sheet audits vs SoT (T-003) | **Gemini** | — | |
| Long research sweeps (noise ordinance, safety, rentals availability; *not* prices) | **Gemini** | — | |
| Higgsfield shots / Adobe Express layouts | **Jovanni operates**; briefs from Claude chat (doc 06) | Gemini QA | Gives them board presence as "Media tools" rows |
| Debrief ops: counts → metrics/lessons → `compare` | **Mochi** drafts · **Claude Code** commits CSVs · **Claude chat** merges lessons into the SoT | Alex collects night counts | Fills gap A6 |
| Free-API bulk prompting (once Gemini/Groq keys exist) | **Mochi** | Claude chat review | Keys go in `.env`, never in the repo |
| Grok web chat | Optional research seat, unassigned | — | Per the minutes. No brief needed until it's used |

### Mochi's slot (Charge Nurse / Unit Clerk)
**What Mochi has:**
- Its own always-on computer.
- Scheduled routines.
- Web research.
- Repo read access.
- Gmail/Calendar access once Jovanni connects them.

**What Mochi does:**
1. **Clock.**
   - A daily 9 AM CT countdown: due today, overdue, next 72 h.
   - Owner nags drafted for Jovanni to forward or approve.
   - Calendar entries for every date in gaps.md §C, once Calendar is connected.
2. **Inbox + RSVP watch.**
   - Flags replies from Glamz (credit wording), Rapid Ric (gear list), Rock n Roll Rentals and the cap vendors.
   - Reports the Tally headcount against the cap every day.
   - Read and flag only. No replies.
3. **Status desk.**
   - Diffs BOARD.md against `web/seed.json` and the briefs against the SoT.
   - Publishes the "Decisions to lock" list.
   - Drafts brief updates in the TEMPLATE format.
4. **Debrief ops.**
   - Chases the night's counts.
   - Pre-fills `DEBRIEF_TEMPLATE.md`.
   - Drafts `add-metric` / `add-lesson` lines.
   - Runs `hub.py compare` on its own box.
   - Hands everything to Claude Code and Claude chat.

**What Mochi never does:**
- Edit the SoT.
- Push to the repo, unless Jovanni later grants it.
- Send or post anything without Jovanni's OK.

### Daily rhythm ("rounds")
- **9 AM: Mochi's morning report.** Countdown, inbox/RSVP movement, blockers, decisions waiting.
- **Claude chat triage.** Turns the report into decisions and new briefs.
- **Workers run their briefs.** Results go to `outbox/`.
- **Evening: Mochi updates the status desk.** Claude chat merges, and Claude Code commits.

## 3. Brief fixes to make (for Claude chat to approve)
1. `CLAUDE.md:8` → Claude Code: "Code, hub (`hub.py`, `web/`, `site/`), in-repo media renders, GitHub, committing board/data changes". Drop the Room Studio, spreadsheets and connector lookups.
2. `CLAUDE.md:12` → Codex: add "Room Studio code + sims, budget workbooks/builders".
3. `orch/GEMINI.md:5` → drop "vendor pricing" from item (3).
4. `README_ORCHESTRATION.md:26-32` → add rows for Claude Code, Mochi and Media tools.
5. `README_ORCHESTRATION.md:36`, `orch/AGENTS.md:6-9,23`, `chatgpt_custom_instructions.md:3,5` and `DRIVE_INDEX.md:6-7` → update the lineup:
   - Glamz is confirmed, solo 11:00 PM, plays free.
   - Credit wording is open.
   - Remove "opener slot open".
   - Cap: 50 working.
6. `orch/tasks/TEMPLATE.md:2` owners → add `Claude Code | Mochi | Jovanni | Alex | Haven`.
7. SoT clean-up:
   - Strike "No phones on the dance floor" (SoT:251) and "refill the jungle juice" (SoT:254).
   - Change the costume prize open item to $40.
   - Fix the 16 Oct and 17 Oct ordering.
   - Replace the header line.
8. `site/index.html` policy: replace "Phones down on the dance floor" (public-facing). This needs Jovanni's OK because it is published.
9. ChatGPT gets a fresh zip after every SoT merge. Mochi reminds.

## 4. Proposed new tasks (T-0xx, matching BOARD.md format)

### Pre-event staffing gaps
| ID | Task | Owner | Status |
|---|---|---|---|
| T-011 | Reconcile BOARD.md with `web/seed.json`: owners of T-005/T-006, T-009 status, close T-007's Glamz block, mark Control #1 and #5 done | Mochi (diff) → Claude Code (commit) | proposed |
| T-012 | Brief-drift fix pass (§3 items 1–7) | Claude chat → Claude Code | proposed |
| T-013 | Build the event calendar and daily countdown from gaps.md §C; reminder drafts for each owner | Mochi | proposed (Calendar connect needed) |
| T-014 | Inbox/RSVP watch: Glamz credit wording, Rapid Ric list, CDJ renter, Tally count against the cap (daily) | Mochi | proposed (Gmail/Tally access needed) |
| T-015 | Repo visibility decision: public repo holds licensed MP3s, personal finances, Drive IDs | Jovanni decides · Claude Code executes | **urgent** |
| T-016 | Capacity lock: reschedule the venue visit or decide the cap from data (61 named / 39 RSVP heads vs 50) | Jovanni + Codex (T-001) | proposed |
| T-017 | Roles fill: door/welfare (sober), second sober host, photographer, CDJ renter, camera hand-out/collection, night counter | Jovanni (Alex supports) | due Fri 23 Oct |
| T-018 | Audio backup quote (Rock n Roll Rentals PA) in case Rapid Ric falls through | ChatGPT (price) → Jovanni | proposed |
| T-019 | Night-of count sheet: one page for door count, midnight peak, drinks left, longest restroom line, incidents (from DEBRIEF_TEMPLATE) | Mochi → Alex | due Wed 28 Oct |

### Post-event closed loop
| ID | Task | Owner | Due (CT) |
|---|---|---|---|
| T-020 | Night counts: door count (unique passes), midnight peak, drinks left at load-out, longest restroom line, noise complaints, incidents | Alex (counter on T-019 sheet) · Mochi chases | Fri 30 Oct night / Sat 31 Oct 3 AM |
| T-021 | Camera count-in at 1:45 AM, lab drop-off Sat 31 Oct, pick-up/scans ~Mon 2 Nov | named crew (T-017) · Mochi reminds | Sat 31 Oct → Mon 2 Nov |
| T-022 | Receipts → actual pool spend, and cost per guest | Haven/Alex give receipts · Mochi tallies · Codex updates the workbook | Sat 31 Oct |
| T-023 | CDJ return to Rock n Roll Rentals | renter (T-017) · Mochi reminds Sun night and Mon morning | **Mon 2 Nov** |
| T-024 | 48 h debrief: fill `DEBRIEF_TEMPLATE.md`, crew input (worked / didn't / surprises / top 3 changes) | Mochi drafts · Jovanni + crew | **by Sun 1 Nov, 2 AM** |
| T-025 | `hub.py add-metric` / `add-lesson` for E001, then run `compare` | Mochi drafts lines · Claude Code commits | Sun 1 Nov |
| T-026 | Thank-you story/DM (Playbook §16), draft only | ChatGPT copy · Jovanni posts | by Sun 1 Nov |
| T-027 | Artist and vendor thank-yous and settle-up (HE//THEY paid? Glamz credit) | ChatGPT drafts · Jovanni sends | Mon 2 Nov |
| T-028 | IG follower snapshot (10.16 vs 11.02) and RSVP-to-attendance (no-show rate) | Mochi | Mon 2 Nov |
| T-029 | Recap post: official cams + film scans, opted-out faces removed; seed AFTERIMAGE 002 | Claude Code (render) · Gemini QA · Jovanni posts | ~Fri 6 Nov |
| T-030 | Lessons into SoT + Playbook; open E002 row in `events.csv`, copy metric names | Claude chat (SoT) · Claude Code (CSV) | ~Fri 6 Nov |

## 5. Decisions to lock (for Jovanni)
1. **Repo visibility.** Make it private, or strip the licensed audio, personal finances and Drive IDs. It is public today.
2. **Org.** Approve the single-owner table in §2, especially: Codex owns the Studio and workbooks, ChatGPT owns pricing, Claude chat owns connector lookups, Mochi owns the calendar, inbox watch and debrief ops.
3. **Capacity / pass count.** 50 or 70? 61 are named, against about 36 safe in the living room. Will the venue visit happen, and when?
4. **Glamz.** Credit wording, and confirm the 11:00 PM–12:15 AM set times (both "assumed").
5. **Roles.** Who takes door/welfare (sober), the second sober host, the photographer, the CDJ renter (SoT says Jovanni picks up, but is he also the renter?), the camera runner and the night counter?
6. **Extra alcohol.** Buy the ~$97–103 add-on? T-009 is still not rerun for the cocktail menu.
7. **Camera program.** Is it funded? Who buys, which lab, who drops off? Post the sign-up only after buying.
8. **Rapid Ric fallback.** The date by which we get a backup PA quote if there is no gear list.
9. **Phones policy wording.** Update the SoT night rules and the public fan site to match "phones fine, officially recorded".
10. **Content calendar.** Approve or hold the drafts dated Mon 19, Tue 20, Wed 21 and Wed 28.
11. **Board of record.** Is BOARD.md or the web hub's task list the one board? Today they disagree.
12. **Mochi's permissions.** May it send reminder texts or emails to the crew directly, or draft only?
