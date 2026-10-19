import sqlite3
def run(q):
    c = sqlite3.connect(":memory:"); q.init(c)
    p1 = q.add_patient(c, "Jane", "Test", "1990-05-17", "(512) 555-0142")
    p2 = q.add_patient(c, "x'); DROP TABLE patients;--", "Test", "1985-01-01", "(512) 555-0199")
    assert q.get_patient(c, p1) == {"pid": p1, "first": "Jane", "last": "Test", "dob": "1990-05-17", "phone": "(512) 555-0142"}, f"get_patient: got {q.get_patient(c, p1)}"
    assert q.get_patient(c, p2)["first"].startswith("x')"), "the injection attempt should be stored as plain text (use ? placeholders)"
    assert q.get_patient(c, 999) is None, "a missing patient -> None"
    q.add_appt(c, "A2", p2, "2026-10-21T14:00", 30); q.add_appt(c, "A1", p1, "2026-10-21T10:00", 30); q.add_appt(c, "A3", p1, "2026-10-22T10:00", 30)
    assert q.appts_on(c, "2026-10-21") == [("2026-10-21T10:00", "A1", p1, 30), ("2026-10-21T14:00", "A2", p2, 30)], f"appts_on: got {q.appts_on(c, '2026-10-21')}"
