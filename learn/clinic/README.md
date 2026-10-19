# Clinic Quest 🩺

You're building the software for **Dr. Kim's private pain-medicine clinic** (consults, follow-ups and procedure days): front desk, patient cards, the appointment book,
waitlist, reminders, billing, a database, reports, and finally a working front-desk app. Each level is one real piece.
Pass a level, earn XP, climb from **Intern** to **Founder**.

```bash
python learn/clinic/play.py          # the map: your XP, rank and next quest
python learn/clinic/play.py 3        # check level 3 (shows exactly what's wrong)
```

Each level folder has a `README.md` (the story and the rules), `quest.py` (you write the code where you see `...`) and
`check.py` (don't edit it). Try for 20 minutes before opening the hint at the bottom of the README.

## Play it in the browser
Clinic Quest Academy: https://claude.ai/artifact/SZagbUUpFwRw9n8iT5sMW2 (built from `learn/clinic/academy/`: edit `lessons.json` or a level, then `python learn/clinic/academy/build.py`).
Every level: **1 · Lesson** (the university lecture behind it), **2 · Code** (Python runs and is checked right in the page, same checks as `play.py`), **3 · PowerShell** (a practice terminal). Levels 8, 11 and 12 run on your PC.

## The 3D model
A cute clay model of the clinic flow (clinic day and procedure day): https://claude.ai/artifact/QaEhjZG1UeZqQAC843T5EH (source `learn/clinic/model/index.html`).
Tap a room to see what happens there, what goes wrong, and which level of this game automates it.

## Ranks
| XP | Rank |
|---|---|
| 0 | 🩺 Intern |
| 300 | 💉 Resident |
| 700 | 🥼 Attending |
| 1200 | 🏥 Chief of Staff |
| 1800 | 👑 Founder (all levels cleared) |

## Patient privacy (read this, it's the real-world rule)
- Every patient in this game is made up (Patient 01, Jane Test…). **Never put real patient information in this repo, in git, or in a chat with an AI.**
- A real clinic system in the US handles protected health information under **HIPAA**: it needs secure, compliant hosting,
  access controls, audit logs and signed agreements with vendors. When you build the real one for Dr. Kim, plan that part
  with someone who has done it before (or use an established, compliant clinic platform and build around it).

## The map
| Lvl | Quest | You learn | XP |
|---|---|---|---|
| 1 | The front desk sign | strings, if/else | 50 |
| 2 | Patient cards | dicts, dates, validation | 75 |
| 3 | The appointment book | rules, errors, no double-booking | 100 |
| 4 | Open slots | loops over time | 100 |
| 5 | The waitlist | queues, classes | 100 |
| 6 | Reminders | text templates, time windows | 75 |
| 7 | Billing | money in cents, formatting | 125 |
| 8 | The filing cabinet | SQLite database | 150 |
| 9 | Monday report | CSV, counting, rates | 125 |
| 10 | 👹 BOSS: the front-desk app | putting it all together | 250 |
| 11 | ⭐ Bonus: predict no-shows | machine learning from scratch | 200 |
| 12 | ⭐ Bonus: ship a feature with Claude Code | directing AI | 300 |
| 13 | ⭐ Bonus: procedure day | readiness checklist, room schedule | 150 |
