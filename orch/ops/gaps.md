# Gaps: meeting findings checked against the repo
Checked Mon 19 Oct 2026, 11 PM CT. Paths are relative to the repo root. "SoT" = `orch/context/SOURCE_OF_TRUTH_latest.md`.
Verdicts: ✅ confirmed · ⚠️ partly true / needs a correction · ❌ the repo contradicts it.

## A. The meeting's problems, verified

### A1. Gmail/Drive/Calendar lookups on both Claude chat and Claude Code ✅
- `CLAUDE.md:8`: Claude Code gets "Drive/Gmail/Calendar lookups".
- `orch/README_ORCHESTRATION.md:29`: Claude (the orchestrator) has the "Gmail/Drive/Calendar/Figma/Tally connectors".
- `orch/context/project_docs/02 … Toolkit.md:4-9`: the connectors are listed as the Claude Project's.
- Extra drift: README_ORCHESTRATION.md:3 and :26-32 do not list **Claude Code** as a worker at all. TEMPLATE.md:2 owner options are only "Codex | ChatGPT | Gemini | Claude".

### A2. Codex brief vs Claude Code brief on the Studio and workbooks ✅
For Codex:
- `orch/AGENTS.md:13` "Your main code asset: the Room Studio".
- `README_ORCHESTRATION.md:30`: Codex gets Room Studio changes and Playwright tests, sims, and the budget workbook rebuild.
- `hub/registry.csv`: every studio and budget item has owner = Codex.

For Claude Code:
- `CLAUDE.md:8`: Claude Code gets "Room Studio changes, spreadsheets/builders".
- `CLAUDE.md:12`: Codex is limited to "files that only exist on the PC".

### A3. Vendor pricing on both Gemini and ChatGPT ✅
- `orch/GEMINI.md:5`: "large research sweeps — vendor pricing (Austin), rental availability".
- `README_ORCHESTRATION.md:31` and `CLAUDE.md:10`: ChatGPT does vendor price checks.
- `orch/workers/chatgpt_custom_instructions.md:4`: "vendor/price research".
- Also: `web/seed.json` gives T-006 (pricing) to **Claude**.

### A4. Nobody owns the calendar ✅
- No brief has a "track dates / remind" duty.
- `02 … Toolkit.md:9`: Google Calendar is listed as "Put deadlines on the calendar (no MOTION events exist yet)".
- Toolkit `:37-41` lists "Scheduled tasks worth setting up" (Monday check-in, 23 Oct, 28 Oct, 30 Oct morning) with no owner.
- Dates do exist as data: `web/seed.json` → `meta.home.dates`, the Logistics Control deadlines, and task due fields. But nothing pushes them to people.

### A5. Nobody watches the inbox or RSVPs ✅ / ⚠️
✅ What holds up:
- No brief assigns inbox or Tally watching.
- The RSVP count in SoT:8 (14 RSVPs / 39 heads, 18 Oct) was a one-off pull.
- `data/metrics.csv:24` `rsvps` is still empty.
- Doc 12:43 only offers reconciling RSVPs "if you share the sheet".

⚠️ Correction:
- **The board is not really blocked on Glamz's answer.** He said yes on 16 Oct (SoT:21), went solo on 17 Oct (SoT:20), and plays free per 18 Oct (SoT:5). The approved flyer `final_v6` already names GLAMZ.
- BOARD.md T-007 "blocked on Glamz" is **stale**, not waiting on anyone.
- What is still truly waiting:
  - Glamz's credit wording (CLAUDE.md:19).
  - His set times, which are "assumed" (SoT:20).
- **Rapid Ric's gear list is genuinely outstanding:** SoT:219, Logistics Control Control #4, and seed.json Control #4 (owner Haven, due 20 Oct).

### A6. The closed loop has tools but no owner ✅ (with a nuance)
- The loop is in README.md:40-45, data/DEBRIEF_TEMPLATE.md:3 and hub.py `compare`.
- BOARD.md and seed.json tasks contain **zero** post-event items.
- Nuance: `hub/registry.csv:38` lists the debrief template with owner "Claude". So a nominal owner exists, but there is no task, no date and no counter named for the night.
- Playbook doc 07 §16 adds: a thank-you within 48 h, a recap within a week, and seeding the next event. None of these is staffed.

### A7. Brief drift (Glamz) ✅, with one correction
Files that still say Glamz is unconfirmed:
- `orch/AGENTS.md:8`: "Glamz unconfirmed"
- `README_ORCHESTRATION.md:36`: "Glamz is unconfirmed"
- `chatgpt_custom_instructions.md:3,5`: "Glamz unconfirmed"
- `DRIVE_INDEX.md:6-7`: "Glamz b3b if confirmed"
- `project_docs/00 …:48`: "still not actually confirmed"

`CLAUDE.md:19` says "Glamz confirmed 16 Oct and plays SOLO … credit wording still to confirm".

⚠️ Correction to the minutes: root CLAUDE.md does **not** say "plays free". "Plays free, no fee (confirmed 18 Oct)" is in **SoT:5**. The commit "Glamz free confirmed" is dated 18 Oct.

### A8. Grok not in the system ✅
There is no mention of Grok anywhere in the repo.

### A9. Higgsfield and Adobe Express have no briefs ⚠️
- True that they have no worker brief, no board rows and no task format: they appear only in `CLAUDE.md:13-14`.
- But Higgsfield does have a prompt / shot-direction doc: `project_docs/06 … Higgsfield Video Direction.md`.

### A10. ChatGPT owns T-005 / T-006 ⚠️
- True in `orch/tasks/BOARD.md:8-9`.
- But `web/seed.json` (what the live web hub shows) assigns T-005 and T-006 to **Claude**.
- So the two boards disagree. See B3.

## B. Additional gaps I found

1. **🔴 The repo is public, but it is treated as private.**
   - GitHub API: `private: false`.
   - It contains Jovanni's licensed MP3s (`media/audio/licensed/*.mp3`; its README says "This repo is private. Don't share these files").
   - It contains a final reel with the song.
   - It contains Drive file IDs (DRIVE_INDEX.md) and the apartment's complex name and full 3D floor plan, plus Rock n Roll Rentals pickup details.
   - The address itself is not in the repo, which is good.
   - **Decision needed:** make the repo private, or remove the files. I did not change anything.
2. **The file protocol is unused.** `orch/tasks/inbox/`, `outbox/` and `done/` contain only `.gitkeep`. No `T-###.md` briefs or results exist, so the "workflow" is in chats, not files.
3. **There are two task boards that disagree.**
   - `BOARD.md` (16 Oct) vs `web/seed.json`:
     - T-005 and T-006 have different owners.
     - T-009 is "ready" in one and "blocked: needs menu confirmed" in the other. The menu was confirmed 16 Oct (SoT:14).
   - Human Control items exist only in seed.json.
   - `hub.py board` reads only BOARD.md.
4. **The SoT contradicts itself.** It is a 14 Oct body with 16 and 18 Oct sections stacked on top:
   - Header "16 Oct update wins" (SoT:2), but there is an 18 Oct section.
   - The 17 Oct "solo" line (SoT:20) sits above the 16 Oct "b3b" line (SoT:21).
   - "70 numbered passes" (SoT:38) vs a cap of 50.
   - Night rules still say "No phones on the dance floor" (SoT:251) and "refill the jungle juice" (SoT:254). Both were superseded on 18 and 16 Oct.
   - Costume prize "$20–50, TBD" in Open items (SoT:216) vs $40 decided (SoT:22).
   - `project_docs/00` is an older 14 Oct copy with none of the updates.
5. **Public-facing drift:** `site/index.html` (fan site) policy still says "Phones down on the dance floor". The 18 Oct decision is that phones are fine and the event is officially recorded. `CAMERA_PROGRAM.md:5` still says the cameras "fit the phones-away rule" and recommends XP2, but option D (Fujifilm) was decided.
6. **Capacity is unresolved and probably over.**
   - There are 61 named guests and 39 RSVP heads, against a working cap of 50 and about 36 safe in the living room.
   - The kitchen and hall measurement never got recorded: SoT:17 says the visit moved, SoT:23 says "today after all", and the Venue tab is all TBD.
   - Because of that, T-001 is still blocked.
7. **Roles are unfilled, and Jovanni is a single point of failure.**
   - In `web/seed.json` roles, these are empty: door/ID/welfare lead (sober), second sober host, photographer, CDJ renter.
   - Jovanni is assigned master fader, water, cleanup, judging, part-time door, crowd recording and CDJ pickup (SoT:7).
   - The sober door helper is still open (SoT:6).
8. **Money not in the budget:**
   - Cameras (about $135–275) are not in the pool.
   - Extra alcohol (about $97–103) is unconfirmed.
   - Sims say a medium-drinking crowd needs about 180–230 pours vs 150 cocktails plus BYOB, and T-009 has not been rerun.
   - All budget workbooks are marked `stale` in the registry.
9. **Audio backup is open.** If Rapid Ric falls through, the plan is a Rock n Roll Rentals quote (SoT:7), which hasn't been requested.
10. **Neighbour notice status is unknown.** It was scheduled 16 Oct (SoT:223) with the moved visit. The Toolkit says to "confirm neighbours told" by 23 Oct.
11. **Venue checks still open:**
    - Bed 3 occupant consent for opening that bath (Venue tab "Confirm").
    - Breakers.
    - Smoke detectors.
    - Ceiling and mirror-ball anchor.
12. **Content calendar has dates but no owner.** DRAFTS_18OCT.md schedules posts on Mon 19, Tue 20, Wed 21 and Wed 28, all "needs OK".
13. **Overdue or stale items on the board:**

    | Item | Due / status |
    |---|---|
    | T-005 | due 17 Oct |
    | T-010 | due 18 Oct |
    | Tell Rohan | due 17 Oct |
    | Cap order | "by about 12 Oct, past due" (SoT:220) |
    | Costume prize task | still open in seed.json, but already decided |
    | Glamz Control #1 | still "open" in seed.json, but answered |
14. **Studio tooling is broken off the original machine.** The registry marks `studio-test` as needs-path-fix (hard-coded `/home/claude`) and `studio-sims` as missing-file (`_t2.py` is absent).
15. **No inbox or task routing for Claude Code, Higgsfield or Adobe** (see A1 and A9).
16. **Rides and safety plan:** "Rides confirmed" is listed as a night rule (SoT:253), but no owner or check is recorded. The welfare contact number is not assigned.

## C. Upcoming deadlines, all America/Chicago
"(derived)" means I calculated it from repo rules, not that the repo states the date.

| Date | Deadline / event | Owner in repo | Source |
|---|---|---|---|
| **Overdue** | T-005 (17 Oct), T-010 (18 Oct), tell Rohan (17 Oct), cap order (~12 Oct), venue visit (TBD) | ChatGPT/Claude, Claude, Jovanni, Jovanni, Jovanni | seed.json, SoT:220 |
| Mon 19 Oct (today) | T-003 Drive audit · T-006 price check · call cap vendors · post the updated flyer draft (needs OK) | Gemini · ChatGPT/Claude · Jovanni · Jovanni | seed.json; DRAFTS_18OCT |
| Tue 20 Oct | T-002 budget workbook · Rapid Ric gear list and booth cable · confirm the cocktail menu and price carts · camera story post (only if cameras are bought) | Codex · Haven · Jovanni · Jovanni | seed.json; DRAFTS_18OCT |
| Wed 21 Oct | T-008 decor / art plan · lineup post 5 v2 (no times) | Claude · Jovanni OK | seed.json; DRAFTS_18OCT |
| Thu 22 Oct | Name the CDJ renter and pickup owner (SoT 18 Oct says Jovanni picks up) | Jovanni | seed.json; SoT:7 |
| Fri 23 Oct | **pay HE//THEY** · assign all roles · close the invite list and confirm neighbours told | Jovanni | seed.json meta; Toolkit:39 |
| Sun 25 Oct | Costume prize amount (stale: $40 already decided) | Jovanni | seed.json |
| Mon 26 Oct | weekly Monday check-in | — | seed.json; Toolkit:38 |
| **Tue 27–Thu 29 Oct** | **CDJ pickup window** (stores close 6 PM Fri) | renter TBD | SoT:182 |
| Wed 28 Oct | Rules carousel post (needs OK) · fallback USB + final gear check | Jovanni | DRAFTS_18OCT; Toolkit:40 |
| **Thu 29 Oct** | **Buy liquor** (package stores closed Sunday; SoT says buy by Thu) | Alex | SoT:119; seed.json |
| **Fri 30 Oct** | Event day:<br>• Morning: run-of-show check (Toolkit:41) and ice run (day-of)<br>• 6:00 PM load-in (Alex)<br>• 7:00 build and cable check<br>• 7:45 sound check<br>• 8:30 crew briefing<br>• 9:00 doors<br>• midnight peak count<br>• 12:30 last entry<br>• 1:30 costume winner<br>• 1:45 last pour and camera count-in<br>• 2:00 hard stop<br>• 2–3 AM load-out | see Run of Show | Logistics Control |
| Sat 31 Oct | Drop the 5 cameras at the lab | Jovanni | CAMERA_PROGRAM.md:22,67 |
| Sun 1 Nov, ~2 AM | **48 h debrief deadline** (derived: 48 h after the 2 AM 31 Oct hard stop) · thank-you story/DM within 48 h | unowned | README:43; Playbook §16 |
| **Mon 2 Nov** | **Return the CDJs** · scans back (est.) · IG follower count snapshot ("10.16 vs 11.02") | renter TBD | SoT:182; metrics.csv:25 |
| ~Fri 6 Nov | Recap post within a week (derived) | unowned | Playbook §16 |
