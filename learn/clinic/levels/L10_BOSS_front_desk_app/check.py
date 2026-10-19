def run(q):
    out = q.run(["book 1 2026-10-21 10:00 30", "book 2 2026-10-21 10:15 30", "book 2 2026-10-21 14:00 45",
                 "schedule 2026-10-21", "wait 7", "cancel A1", "cancel A9", "schedule 2026-10-22", "dance"])
    assert out[0] == "booked A1 2026-10-21 10:00 (30 min) for patient 1", f"book line: {out[0]!r}"
    assert out[1].startswith("error: "), f"overlapping booking should print an error, got {out[1]!r}"
    assert out[2] == "booked A2 2026-10-21 14:00 (45 min) for patient 2", f"second booking: {out[2]!r}"
    assert out[3:5] == ["10:00 A1 patient 1 (30 min)", "14:00 A2 patient 2 (45 min)"], f"schedule: {out[3:5]}"
    assert out[5] == "patient 7 is on the waitlist (1 waiting)", f"wait: {out[5]!r}"
    assert out[6:8] == ["cancelled A1", "offer the slot to patient 7"], f"cancel: {out[6:8]}"
    assert out[8] == "error: no appointment A9", f"cancel unknown: {out[8]!r}"
    assert out[9] == "no appointments" and out[10] == "error: unknown command", f"end: {out[9:]}"
    free = q.run(["book 1 2026-10-21 09:00 60", "free 2026-10-21"])[-1]
    assert free.startswith("free: 10:00 10:15") and free.endswith("16:30"), f"free: {free!r}"
