import datetime as dt
def bad(fn, *a):
    try: fn(*a)
    except ValueError: return True
    return False
def run(q):
    D = lambda h, m=0, day=21: dt.datetime(2026, 10, day, h, m)        # 21 Oct 2026 is a Wednesday
    b = []
    a = q.book(b, 1, D(10), 30)
    assert a == {"id": "A1", "pid": 1, "start": D(10), "minutes": 30} and b == [a], f"book: got {a}"
    assert q.book(b, 2, D(10, 30), 30)["id"] == "A2", "touching appointments are allowed, and the next id is A2"
    assert bad(q.book, b, 3, D(10, 15), 30), "10:15-10:45 overlaps A1: should raise"
    assert bad(q.book, b, 3, D(9, 10), 15), "9:10 isn't a quarter hour: should raise"
    assert bad(q.book, b, 3, D(14), 20), "20 minutes isn't allowed"
    assert bad(q.book, b, 3, D(11, 45), 30), "11:45-12:15 runs into lunch"
    assert bad(q.book, b, 3, D(16, 45), 30), "16:45-17:15 runs past closing"
    assert bad(q.book, b, 3, D(10, 0, 24), 30), "24 Oct is a Saturday"
    assert len(b) == 2, "a rejected booking must not be added"
