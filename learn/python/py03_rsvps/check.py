import os
def run(m):
    rows = m.load(os.path.join(os.path.dirname(__file__), "rsvps_sample.csv"))
    assert len(rows) == 7 and isinstance(rows[0]["heads"], int), "load: 7 rows, heads as int"
    assert m.heads_per_day(rows) == {"2026-10-15": 3, "2026-10-16": 4, "2026-10-17": 10, "2026-10-18": 1}, f"heads_per_day: got {m.heads_per_day(rows)}"
    assert m.best_day(rows) == "2026-10-17", "best_day"
