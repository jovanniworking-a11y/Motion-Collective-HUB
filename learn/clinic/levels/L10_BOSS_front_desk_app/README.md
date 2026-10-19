# 👹 BOSS: the front-desk app · 250 XP
Put it together: a little command app the front desk can actually use. It reuses your code from levels 3, 4 and 5.

Write `run(commands)` in `quest.py`: it takes a list of command strings and returns a list of output lines.
| Command | Output |
|---|---|
| `book PID YYYY-MM-DD HH:MM MIN` | `booked A1 2026-10-21 10:00 (30 min) for patient 1` or `error: <the ValueError message>` |
| `schedule YYYY-MM-DD` | one line per appointment, in time order: `10:00 A1 patient 1 (30 min)`, or `no appointments` |
| `free YYYY-MM-DD` | `free: 10:30 10:45 ...` (30-minute slots, from level 4) or `free: none` |
| `wait PID` | `patient 7 is on the waitlist (1 waiting)` |
| `cancel ID` | `cancelled A1` plus, if someone is waiting, a second line `offer the slot to patient 7`; unknown id: `error: no appointment A9` |
| anything else | `error: unknown command` |

Then (not checked, for real): add a `main()` that reads commands from `input()` in a loop, so the front desk can type them.

<details><summary>Hint</summary>

Keep one `appts` list and one `Waitlist` for the whole run. `line.split()` breaks a command into words.
`datetime.datetime.fromisoformat("2026-10-21T10:00")` builds the start.
</details>
