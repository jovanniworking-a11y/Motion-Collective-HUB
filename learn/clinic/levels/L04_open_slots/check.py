import datetime as dt
def run(q):
    day = dt.date(2026, 10, 21)
    appts = [{"id": "A1", "pid": 1, "start": dt.datetime(2026, 10, 21, 9, 0), "minutes": 60},
             {"id": "A2", "pid": 2, "start": dt.datetime(2026, 10, 21, 14, 0), "minutes": 30}]
    got = q.free_slots(appts, day, 30)
    want = ["10:00", "10:15", "10:30", "10:45", "11:00", "11:15", "11:30", "13:00", "13:15", "13:30", "14:30", "14:45",
            "15:00", "15:15", "15:30", "15:45", "16:00", "16:15", "16:30"]
    assert got == want, f"free_slots for 30 min: expected {want}, got {got}"
    assert q.free_slots([], dt.date(2026, 10, 24)) == [], "Saturday has no slots"
    assert len(q.free_slots([], day, 60)) == 9 + 13, "an empty Wednesday, 60-minute slots: 9:00-11:00 and 13:00-16:00"
