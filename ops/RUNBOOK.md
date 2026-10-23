# Night-of runbook · MOTION Ops · Fri 30 Oct 2026
One page. Crew only. Draft. No guest names, no venue address — in the app, in logs, or on screens.

## The one rule that matters
**Counts live on the device that took them** (browser storage, key `motion-night-ops-v1`). Two phones checking in passes = two separate counts. **One door device owns check-in.** Other phones use Show / Welfare only.

## Which surface
| Surface | Use it for | Needs |
|---|---|---|
| **Door phone · `ops/` page** (preferred on the night) | Pass check-in 001–070, run of show, welfare rounds, budget | Loaded once online, then works offline |
| Ops panel (`apps/ops-panel`) on the laptop or deployed URL | Same Night-Of tab + agents, usage, activity | Login (name + password + 6-digit code) when deployed |
| Paper pass list 001–070 | Fallback if the door phone dies | A pen. Copy counts back afterwards |

## Thursday 29 Oct (setup, 15 min)
1. Pick the **door phone** (charged, brightness up, auto-lock off) and a **backup phone**.
2. On both, open the ops page **online** once, then add it to the home screen. Turn on airplane mode and reload: the Door tab must still load. If it doesn't, reload online once more and retry.
3. On the backup only: open **Clock → Jump to event night** and rehearse a few check-ins, then **Reset**, so the night starts from 0.
4. If using the deployed panel: each crew login is set up (`apps/ops-panel/DEPLOY_LOGIN.md`) and the authenticator code works. Never share a password in a group chat.
5. Print the paper pass list 001–070 (numbers only) and tape it inside the door clipboard.

## Friday 30 Oct
| Time | Who | What |
|---|---|---|
| 20:30 | Alex | Crew briefing: who holds the door phone, who runs welfare rounds, who owns the master fader |
| 20:45 | Door | Door phone: Door tab shows **0 of 70**. If not, Reset (only before doors) |
| 21:00 | Door | Doors. Tap each pass number on entry. Wrong tap → **Undo last** |
| every 30 min | Welfare lead | Welfare tab → log the round. The 12:30 collision (last entry + fader + welfare) needs cover assigned before 12:15 |
| at cap | Door | At **70** the count tile turns hot and Room left shows 0. Passes stop at 070, so anyone without a pass number waits for Jovanni's call |
| 00:30 | Door | Last entry. Door phone stays on the door |
| 01:45 / 02:00 | Water lead / Jovanni + Alex | Last pour, then the called last song and hard stop |

## If something breaks
- **Phone dies / app won't load:** switch to the backup phone **and** start writing numbers on the paper list from that moment. Don't re-enter old check-ins on the backup.
- **Wi-Fi drops:** nothing to do — the page works offline. The "offline · local" chip is normal.
- **Deployed panel shows "Login is not configured":** settings missing on the host. Use the door phone page; fix after the night.
- **Login locked (5 wrong codes):** wait 15 minutes, or use the door phone page.

## 02:00 shutdown (5 min)
1. Door phone: **Export log** (downloads a JSON of pass numbers, counts and welfare rounds — no names). Send it to Alex privately, never to a group or git.
2. Alex fills `data/metrics.csv`: `guests_total` (unique passes), `guests_peak` (count at midnight), `no_show_rate`, `incidents`, `drinks_left_at_close`.
3. On every crew device: **Reset** check-ins and **Clear log** for welfare. On the deployed panel: **log out** (also clears the offline copy).
4. Paper list: count it into the metrics, then shred it.
