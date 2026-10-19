# The filing cabinet · 150 XP
Lists vanish when the program stops. A database keeps them. Python ships with SQLite: a real database in one file.

Write in `quest.py` (use the `sqlite3` module; always use `?` placeholders, never paste values into SQL text):
1. `init(conn)`: create tables `patients(pid INTEGER PRIMARY KEY, first, last, dob, phone)` and
   `appts(id TEXT PRIMARY KEY, pid INTEGER REFERENCES patients(pid), start TEXT, minutes INTEGER)`.
2. `add_patient(conn, first, last, dob, phone)` → the new pid.
3. `get_patient(conn, pid)` → a dict like level 2's card, or `None`.
4. `add_appt(conn, appt_id, pid, start_iso, minutes)`.
5. `appts_on(conn, date_iso)` → list of `(start_iso, appt_id, pid, minutes)` for that day, sorted by time.

Why `?` placeholders: pasting text into SQL lets a "name" like `x'); DROP TABLE patients;--` wreck the database
(SQL injection). The check tries exactly that.

<details><summary>Hint</summary>

`cur = conn.execute("INSERT INTO patients(first, last, dob, phone) VALUES (?, ?, ?, ?)", (first, last, dob, phone))`, then `cur.lastrowid`.
Same day: `WHERE start LIKE ?` with `date_iso + "%"`. Call `conn.commit()` after writes.
</details>
