# RSVP counts — AFTERIMAGE 001 (E001)

Synced: 2026-10-21 ~01:45 CT via the Tally API (form `Ekj7zA`, "AFTERIMAGE 001 — RSVP").
Sync script: `~/workspace/custom-connectors/custom.tally/bin/tally_rsvp_sync.py`
Live sheet (names live ONLY in Drive, never here): "MOTION · AFTERIMAGE 001 · RSVP Guest List".

> **Repo rule (root CLAUDE.md): "Guest data stays out of git."**
> This file carries counts and schema only. No names, no handles, no contact
> data. The named guest list lives in Jovanni's Google Drive.

## Counts
| Metric | Value | Label |
|---|---|---|
| Form submissions | 21 | confirmed |
| Unique people (deduplicated) | 20 | confirmed |
| Heads claimed (party sizes summed) | 49 | estimate ('6+' counted as 6) |
| Pass cap | 70 | confirmed |
| Spots left | 21 | estimate |
| Double RSVPs | 1 | confirmed (same name + handle, counted once) |
| Crew RSVPs via the form | 2 | confirmed |

## Schema (sheet columns)
`RSVP List` tab: Submitted (CT) | Name | Instagram handle | Party size | Pass # | Checked in | Notes
`Groups & Duplicates` tab: duplicate groups, crew RSVPs, live totals.
Pass numbers are assigned by the door team (Alex posts flex assignments); the
sync never assigns them.

## Invite-list comparison (21 Oct ~01:50 CT)
Invite list source: `MOTION_Guest_List.xlsx` (Jovanni upload) — 50 named rows,
passes 1–55 assigned (gaps: 2/17 retired dupes, 22–23 not attending), statuses:
25 Invited / 24 Confirmed-RSVP / 1 Confirmed (organizer).

| Metric | Value | Label |
|---|---|---|
| Invite-list names matched to a Tally RSVP | 10 | confirmed |
| Tally RSVPs with NO invite-list entry (need pass #) | 10 | confirmed |
| Invited but silent (Jovanni's rule: assume attending) | 22 | confirmed |
| Workbook rows marked "Invited" that DID RSVP (stale flags) | 3 | confirmed |

Headcount projection vs cap 70 (Jovanni's rule: silent friends come):

| Scenario | Extra heads | Total | vs cap 70 |
|---|---|---|---|
| Conservative (50% show × 1.5/party) | 14 | 63 | −7 (estimate) |
| Mid (75% × 2.0) | 27 | 76 | +6 (estimate) |
| Jovanni's rule (100% × 2.45 avg) | 44 | 93 | +23 (estimate) |

The workbook's Confirmed-RSVP set is stale: it hand-expands an older Tally
pull and misses 10 newer RSVPs entirely. Live comparison lives in the Drive
sheet's "Invite vs RSVP" tab, refreshed by the sync script every watch sweep.

## Notes
- Party-size question offers 1–5 plus "6+ (DM us directly for a bigger group)".
- Instagram handle is optional on the form (20 of 21 gave one).
- Push blocked: GitHub write is 403 for Pip's connector — this file needs a
  push via Cursor or Jovanni to land on main.
