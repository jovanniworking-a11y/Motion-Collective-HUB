def run(q):
    w = q.Waitlist(); w.add(7); w.add(8); w.add(7)
    assert len(w) == 2, "no duplicates on the waitlist"
    appts = [{"id": "A1", "pid": 1}, {"id": "A2", "pid": 2}]
    assert q.cancel(appts, "A1", w) == 7 and [a["id"] for a in appts] == ["A2"], "cancel removes A1 and offers it to patient 7"
    assert q.cancel(appts, "A2", w) == 8 and appts == [] and q.cancel([{"id": "A3", "pid": 3}], "A3", w) is None, "empty waitlist -> None"
    try: q.cancel([], "A9", w); raise AssertionError("cancelling a missing id should raise KeyError")
    except KeyError: pass
