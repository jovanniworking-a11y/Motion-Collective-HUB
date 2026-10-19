# The appointment book · 100 XP
The heart of the clinic. One doctor, so **no two appointments can overlap**.

An appointment is a dict: `{"id": "A1", "pid": 1, "start": datetime, "minutes": 30}`.

Write `book(appts, pid, start, minutes)` in `quest.py`. It appends a new appointment to the list `appts` and returns it.
IDs go `A1, A2, …` (one more than the number already in the book). Raise `ValueError` if:
- `minutes` isn't 15, 30, 45 or 60
- `start` isn't on a quarter hour (:00, :15, :30, :45)
- the clinic is closed at any point of it (use your rules from level 1: weekdays 9–17, lunch 12–13)
- it overlaps any existing appointment (touching is fine: 10:00–10:30 and 10:30–11:00 don't overlap)

<details><summary>Hint</summary>

`end = start + datetime.timedelta(minutes=minutes)`. Two ranges overlap when `a_start < b_end and b_start < a_end`.
The lunch rule: the appointment must end by 12:00 or start at 13:00 or later. `start.strftime("%a")` gives `"Mon"`.
</details>
