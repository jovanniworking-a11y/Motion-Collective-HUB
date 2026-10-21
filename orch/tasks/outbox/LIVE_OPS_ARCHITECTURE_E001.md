# LIVE OPS ARCHITECTURE — Devil's Night · AFTERIMAGE 001
**Date:** 21 Oct 2026 · **Status:** architecture locked for build · **Design rule (Jovanni):** Apple-like — complex behind the scenes, UI clean/simple/touch-friendly
**Extends:** `tasks-inbox/DP-04-live_BUILD_BRIEF.md` · **Research:** `LIVE_OPS_RESEARCH_BRIEF.md` (all claims source-verified there)

## The one-setup principle
One software stack, four machines, each with exactly one job. Nobody touches a node network mid-party. The crew sees two screens: the HQ dashboard (MacBook) and the door view (iPad). Everything else is plumbing.

## Machine map
| Machine | Codename | Job (one only) | Backup |
|---|---|---|---|
| 3070 Ti laptop | ENGINE | docker-wyze-bridge → Python YOLO counter → WebSocket out; TouchDesigner in Perform Mode (visuals) ← DJM USB-A audio; HDMI → projector | Counter can drop to 10 FPS or move to booth PC if TD chokes |
| Jovanni's MacBook | HQ | Dashboard web page (dark mode), zero interaction needed to read it | Haven's laptop (hot spare, same URL) |
| iPad | DOOR | Door view: giant occupancy + SPACE LEFT + one CHECK-IN button | Paper tally sheet |
| Venue booth PC | BOOTH | DJM USB-B → set recording (Audacity or OBS, free) | REC OUT analog → phone line-in |

Dashboard is a static page + WebSocket served by the counter script on ENGINE over local LAN. MacBook/iPad just open the URL. **Nothing in this stack needs the internet night-of** — verify in testing (no cloud logins, no phoning home).

Full text continues in the source file on the branch after this commit's companion files. The locked rules in this copy: one job per machine, dropout keeps the last count, door iPad is occupancy + SPACE LEFT + CHECK IN, palette void #0A0810 / bone #EDE6DA, green <55 / amber 55–64 / red ≥65, 1280×1280 TD cap, physical bypass DJM Booth Out to PA.
