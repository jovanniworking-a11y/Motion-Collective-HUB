# The front desk sign · 50 XP
Dr. Kim opens Monday to Friday, 9:00 to 17:00. Closed for lunch 12:00–13:00. Closed weekends.

Write in `quest.py`:
1. `greeting(name)` → `"Welcome to Dr. Kim's Clinic, Jane!"`
2. `is_open(day, hour)`: `day` is `"Mon"`…`"Sun"`, `hour` is 0–23. True only on weekdays, 9 ≤ hour < 17, and not during lunch (hour 12).
3. `sign(day, hour)` → `"OPEN"` or `"CLOSED"` (use `is_open`).

<details><summary>Hint</summary>

`day in ("Sat", "Sun")`, and remember `and` / `or` / `not`. f-strings: `f"Welcome ..., {name}!"`.
</details>
