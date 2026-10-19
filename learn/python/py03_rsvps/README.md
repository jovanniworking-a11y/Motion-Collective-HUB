# py03 · RSVPs per day
Tally exports a CSV. We want to know which day the RSVPs (and the heads they bring) came in, to see which post worked.

`rsvps_sample.csv` is made-up data. Fill in `exercise.py`:
1. `load(path)`: read the CSV into a list of dicts (`csv.DictReader`), with `heads` as an int.
2. `heads_per_day(rows)`: a dict `{"2026-10-15": 7, ...}` of total heads per date (the date is the first 10 characters of `submitted_at`).
3. `best_day(rows)`: the date with the most heads.
