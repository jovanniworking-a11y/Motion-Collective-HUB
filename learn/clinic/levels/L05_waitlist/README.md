# The waitlist · 100 XP
Cancellations happen. When one does, the first person on the waitlist gets offered the slot.

Write in `quest.py`:
1. A class `Waitlist` with `add(pid)` (no duplicates: adding someone already waiting does nothing), `next()` (removes and
   returns the first pid, or `None` if empty) and `len(waitlist)`.
2. `cancel(appts, appt_id, waitlist)`: remove that appointment from `appts`; raise `KeyError` if there's no such id.
   Return the pid to offer the slot to (`waitlist.next()`), or `None`.

<details><summary>Hint</summary>

`collections.deque` is a fast queue (`append`, `popleft`). For `len()`, define `__len__`.
</details>
