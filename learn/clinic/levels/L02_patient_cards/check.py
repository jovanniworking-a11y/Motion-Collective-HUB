import datetime
def bad(fn, *a, **k):
    try: fn(*a, **k)
    except ValueError: return True
    return False
def run(q):
    t = datetime.date(2026, 10, 19)
    p = q.make_patient(1, " jane ", "test", "1990-05-17", "512.555.0142", today=t)
    assert p == {"pid": 1, "first": "Jane", "last": "Test", "dob": "1990-05-17", "phone": "(512) 555-0142"}, f"make_patient: got {p}"
    assert bad(q.make_patient, 2, "", "Test", "1990-05-17", "5125550142", today=t), "empty first name should raise ValueError"
    assert bad(q.make_patient, 2, "Jo", "Test", "1990-02-30", "5125550142", today=t), "Feb 30 should raise ValueError"
    assert bad(q.make_patient, 2, "Jo", "Test", "2030-01-01", "5125550142", today=t), "a birthday in the future should raise ValueError"
    assert bad(q.make_patient, 2, "Jo", "Test", "1990-01-01", "555-0142", today=t), "a 7-digit phone should raise ValueError"
    assert q.age("1990-05-17", t) == 36 and q.age("1990-12-25", t) == 35, "age: check birthdays later in the year"
