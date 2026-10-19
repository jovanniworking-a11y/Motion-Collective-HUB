# Patient cards · 75 XP
Every patient gets a card. Bad data at the front desk becomes a mess later, so the card checks itself.

Write in `quest.py`:
1. `make_patient(pid, first, last, dob, phone)` → a dict with those keys. Rules (raise `ValueError` with a clear message if broken):
   - `first` and `last` not empty (strip spaces; store them with the first letter capitalised: `"jane"` → `"Jane"`)
   - `dob` is `"YYYY-MM-DD"` and a real date, not in the future
   - `phone`: keep only the digits; it must be 10 digits; store it as `"(512) 555-0142"`
2. `age(dob, today)`: whole years, `today` is a `datetime.date`. Careful with birthdays later in the year.

<details><summary>Hint</summary>

`datetime.date.fromisoformat("1990-05-17")` raises `ValueError` on a bad date. Digits only: `"".join(c for c in phone if c.isdigit())`.
Age: `today.year - d.year - ((today.month, today.day) < (d.month, d.day))`.
</details>
