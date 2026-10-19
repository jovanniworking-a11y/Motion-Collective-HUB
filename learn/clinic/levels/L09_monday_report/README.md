# Monday report · 125 XP
Every Monday Dr. Kim wants to know: which weekday has the most no-shows, and when is the clinic busiest?

`history_sample.csv` is made-up appointment history (`start,status` where status is `kept`, `no-show` or `cancelled`).

Write in `quest.py`:
1. `load(path)` → list of dicts with `start` as a `datetime`.
2. `no_show_rate(rows)` → `{"Mon": 0.25, ...}`: no-shows ÷ (kept + no-shows) per weekday, rounded to 2 decimals.
   Ignore cancelled ones. Only include weekdays that appear.
3. `busiest_hour(rows)` → the hour (int) with the most kept appointments (ties: the earliest hour).
