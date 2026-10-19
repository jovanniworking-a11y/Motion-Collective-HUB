import os
def run(q):
    rows = q.load(os.path.join(os.path.dirname(__file__), "history_sample.csv"))
    assert len(rows) == 15 and hasattr(rows[0]["start"], "hour"), "load: 15 rows with datetime starts"
    want = {"Mon": 0.17, "Tue": 0.0, "Wed": 0.67, "Thu": 0.0, "Fri": 0.5}
    assert q.no_show_rate(rows) == want, f"no_show_rate: expected {want}, got {q.no_show_rate(rows)}"
    assert q.busiest_hour(rows) == 10, f"busiest_hour: expected 10, got {q.busiest_hour(rows)}"
