# Automation plan · one front door for Jovanni (24 Oct 2026)
Goal: Jovanni talks to **one** channel. Everything else is dispatched, checked and queued for his OK without him relaying between apps. The house rules don't change.

## Today (from the repo)
- **Jovanni relays copy-paste between about 10 seats:**
  - Claude chat, Claude Code, Cursor, Codex (PC), ChatGPT, Gemini
  - 3 Grok bots (Jerry, Chaka, Bartholomew)
  - Pip
  - file links on muse.ai
- **Already automatic:**
  - CI, hygiene and link checks on every push (`.github/workflows/`)
  - the daily 8:52 check-in (Tally RSVPs + board)
  - Pip's inbox/RSVP watches
- **What breaks in the relay:**
  - Jerry's bridge landed in git base64-encoded, so it couldn't run until it was decoded.
  - Bots work from stale facts (Bartholomew still had pool $450).
  - Three seats did parallel versions of the same occupancy work (PRs #7, #9, #10).

## The plan: one front door, one approval queue
1. **Front door: this Claude Code session.** Jovanni says what he wants. Claude splits it, writes the brief, and dispatches it.
2. **Dispatch without relay:**
   - **Code:** a Claude Code cloud session per task, working on its own branch and opening a pull request. It replaces the Cursor + Grok relay.
   - **Checks:** CI gates every pull request. A review session reads each diff, replacing the Bartholomew relay.
   - **Data:** scheduled tasks here use the connectors this session already has: Tally, Gmail, Calendar, Drive/Sheets/Docs, GitHub.
3. **One approval queue.** Anything that spends, sends, posts, publishes or names a person becomes a **draft** in `orch/tasks/APPROVALS.md` and in the daily digest. Nothing leaves until Jovanni says OK.
4. **Facts are generated, not retyped.** Every prompt starts with a facts block built from `orch/context/CURRENT_LOCK.md`. Bots can't go stale, and the hygiene scan still blocks retired numbers and canceled names.
5. **One digest a day**, the 8:52 check-in expanded to cover:
   - RSVPs and new vendor or artist emails (flag only)
   - CI and open pull requests
   - what other agents pushed
   - the approval queue
   - the three most urgent decisions

## Lane by lane
| Work | Today | Automated | Needs |
|---|---|---|---|
| Repo code (panel, API, live-ops) | Cursor + Grok bots via phone relay | Claude Code child sessions, one per task; PR + CI; merged when green | A standing OK to merge green PRs, or Jovanni taps merge |
| Code review / audit | Bartholomew via relay | Review session on every PR, findings in the PR | — |
| Drive sheet audit | Gemini via Pip | Scheduled Claude task with the Sheets connector (report only) | — |
| Copy (captions, DMs, neighbour note) | ChatGPT | Claude drafts straight into the approval queue | Jovanni's OK before anything is sent or posted |
| Video / reel review | Gemini | Claude frame analysis (as on 24 Oct); Gemini optional for long clips | — |
| Budget workbook | Codex on the PC | Move the workbook to Google Sheets so it can be edited via the connector; Codex only for PC-only files | Jovanni moves or shares the file |
| RSVPs, inbox, calendar watch | Pip + daily check-in | Daily digest here (flag only) | — |
| Orders (matchbox, towels, cameras, CDJs) | Jovanni / Pip | Stay human: they spend money | Jovanni |
| Instagram insights | Not connected | Not possible from here yet | An Instagram connector, or screenshots |
| Hardware (camera, DJM, projector) | Crew, 29 Oct | Stays hands-on | Crew |

## Stays with Jovanni by design
Money out, public posts, messages to people, final lineup and creative calls, logins and 2FA, hardware tests.

## Costs (labelled)
- **Claude Code sessions and scheduled tasks:** draw on Jovanni's existing Claude plan. No new spend (confirmed: no API key needed). They do use plan usage (estimate).
- **ChatGPT / Grok / Gemini automation:** needs their paid API keys, which is spend. **Not recommended before 30 Oct.** Collapse those lanes into Claude instead.
- **Anthropic API key for in-panel agent chat:** billed. Optional; the Pro bridge works without it.

## Decisions for Jovanni
1. Make this Claude Code session the front door? (yes / no)
2. Standing rule for code: may Claude merge a pull request once CI and review are green? (yes / ask each time)
3. Retire the Grok relay and Cursor relay for repo code? (yes / keep Cursor as backup)
4. Move the budget workbook to Google Sheets? (yes / no)
