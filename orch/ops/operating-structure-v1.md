# Motion Collective operating structure, v1 (DRAFT for Jovanni)
Drafted 20 Oct 2026 by Mochi. Nothing is changed in the repo. Claude chat merges into the Source of Truth (SoT) and Jovanni approves.
Keep this out of the public Motion-Collective-HUB repo until it is private.

## 1. The three layers
1. **Who owns what** lives in one file: `orch/ROLES.md` (draft in `ROLES.md` next to this file). Every brief, board row and reminder points to it instead of restating owners.
2. **What has to happen** lives in one board: `orch/tasks/BOARD.md` is the board of record (proposed; decision 11). `web/seed.json` is generated from it, never edited by hand.
3. **When it is due** comes from the board: the daily deadline rundown reads BOARD.md each morning and reports due today, overdue and next 48 hours, with owners pulled from ROLES.md.

The briefs (`CLAUDE.md`, `orch/AGENTS.md`, `orch/GEMINI.md`, ChatGPT instructions, `README_ORCHESTRATION.md`) only describe how each worker works. They never carry facts like lineup, cap or prices. Those live only in the SoT, so the briefs cannot drift.

## 2. Task taxonomy (every task gets one phase tag and one ID)
| Phase | Tag | ID range | What goes here |
|---|---|---|---|
| Pre-event build | `PRE` | T-001 to T-019 | Venue, capacity, budget, lineup, promo, roles, gear, staffing gaps |
| Event night | `NIGHT` | N-01 to N-10 | Run of show, door double-check, welfare, incident log, night counts (T-019 sheet feeds these) |
| Post-event loop | `POST` | T-020 to T-030 | Counts, cameras, receipts, CDJ return, 48 h debrief, metrics, thank-yous, recap, lessons into SoT |
| Decisions | `DEC` | D-01 to D-12 | The 12 decisions to lock (below). A decision blocks every task that cites it |
| System | `SYS` | S-01 onward | Repo visibility, brief fixes, board sync, routine health |

Each board row: `ID | phase | task | owner (from ROLES.md) | due (CT) | blocked by | status`.
Status values only: `proposed`, `open`, `in progress`, `blocked`, `done`, `dropped`.

### Event-night modules (N-series, from the training package)
- N-01 Door double-check: two people, clicker reconciled with wristbands every 30 min, hard cap includes crew.
- N-02 Welfare: sober welfare lead plus a second sober host, recovery room, never leave an intoxicated guest alone, 911 for unresponsive, breathing trouble, seizure or head injury.
- N-03 Incident log: what, when, who, what was done, follow-up owner, written the same night, closed at the debrief.
- N-04 Night counts: door count, midnight peak, drinks left, longest restroom line, noise complaints (feeds T-020).

### Decisions to lock (DEC-series, from the org proposal)
D-01 repo visibility, D-02 org table, D-03 capacity and pass count, D-04 lineup after the Glamz change (11 PM DJ: Rohan Rawley vs DJ Bam), D-05 roles incl. welfare lead, D-06 extra alcohol, D-07 camera program, D-08 Rapid Ric fallback date, D-09 phones policy wording, D-10 content calendar, D-11 board of record, D-12 Mochi's send permissions.

## 3. How the pieces plug in
- **Daily rundown (8 AM CT):** reads BOARD.md and ROLES.md, lists due today, overdue, next 48 h, open DEC items, and any brief that disagrees with the SoT. Drafts owner nudges; sends nothing.
- **Status desk:** Mochi diffs BOARD.md against `web/seed.json` and the briefs against the SoT, and writes the diff. Claude Code commits after Claude chat approves.
- **Inbox and RSVPs:** Mochi reads and flags (Rapid Ric gear list, DJ replies, vendors, Tally count vs cap). No replies.
- **48 h debrief:** Mochi pre-fills `DEBRIEF_TEMPLATE.md` from the N-04 counts, Claude Code commits metrics, Claude chat merges lessons into the SoT.

## 4. Brief drift fix (S-02)
Current text: `orch/AGENTS.md:8` says "Glamz unconfirmed"; root `CLAUDE.md:19` says "Glamz confirmed 16 Oct".
The 12:49 AM request was to make AGENTS.md say "confirmed 16 Oct". On the 19 Oct call, though, Jovanni said Glamz is cut and the 11 PM slot goes to Rohan Rawley or DJ Bam (leaning Rohan).
**Proposed fix, pending Jovanni's pick:** remove lineup facts from AGENTS.md entirely and point it to the SoT lineup section, then have Claude chat update `CLAUDE.md:19` and the SoT to "Glamz cut (19 Oct); 11 PM slot: [Rohan Rawley | DJ Bam], TBC".

## 5. First concrete piece to put in place
`orch/ROLES.md`, the single owner table (draft in `ROLES.md`). Once Claude chat merges it, every other piece (board owners, rundown, briefs) references it.
