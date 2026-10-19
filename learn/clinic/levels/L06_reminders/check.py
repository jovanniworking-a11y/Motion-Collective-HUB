import datetime as dt
def run(q):
    p = {"pid": 1, "first": "Jane", "last": "Test"}; a = {"id": "A1", "pid": 1, "start": dt.datetime(2026, 10, 21, 14, 30), "minutes": 30}
    want = "Hi Jane, this is Dr. Kim's Clinic reminding you of your appointment on Wed 21 Oct at 2:30 PM. Reply C to confirm or X to cancel."
    assert q.reminder_text(p, a) == want, f"reminder_text: got {q.reminder_text(p, a)!r}"
    now = dt.datetime(2026, 10, 20, 14, 0)
    appts = [{"id": "A1", "start": dt.datetime(2026, 10, 21, 14, 30)}, {"id": "A2", "start": dt.datetime(2026, 10, 21, 16, 0)},
             {"id": "A3", "start": dt.datetime(2026, 10, 21, 13, 0)}, {"id": "A4", "start": dt.datetime(2026, 10, 21, 12, 30)}]
    assert q.who_to_remind(appts, now) == ["A1", "A3"], f"who_to_remind: got {q.who_to_remind(appts, now)}"
