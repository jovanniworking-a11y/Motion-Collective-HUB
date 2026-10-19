# Open slots · 100 XP
Patients call and ask "what do you have on Wednesday?" Answer instantly.

Write `free_slots(appts, day, minutes=30)` in `quest.py`: every start time (as `"HH:MM"`, in order) on `day` (a `datetime.date`)
where an appointment of `minutes` could be booked, stepping every 15 minutes from 9:00. Use the same rules as level 3.

You can reuse your level-3 code: `from _lib import level` then `level(3).book(...)` on a copy of the list
(a booking that raises means that slot isn't free).

<details><summary>Hint</summary>

Loop `t` from 9:00 to 16:45 in steps of 15 minutes; try `book(list(appts), 0, t, minutes)`; keep `t.strftime("%H:%M")` when it doesn't raise.
</details>
