def run(q):
    ok = {"name": "Patient 01 · lumbar ESI", "minutes": 30, "consent_signed": True, "prior_auth": "approved", "sedation": False, "blood_thinner": False}
    assert q.missing(ok) == [], f"a complete case should be ready, got {q.missing(ok)}"
    sed = dict(ok, name="Patient 02 · RFA", minutes=60, sedation=True, driver_confirmed=False, npo_confirmed=True)
    assert q.missing(sed) == ["driver"], f"sedation without a driver: got {q.missing(sed)}"
    bad = {"name": "Patient 03", "minutes": 45, "consent_signed": False, "prior_auth": "pending", "sedation": True, "blood_thinner": True}
    assert q.missing(bad) == ["consent", "prior auth", "driver", "fasting", "blood thinner plan"], f"order and items: got {q.missing(bad)}"
    sed_ok = dict(sed, driver_confirmed=True)
    sched = q.room_schedule([ok, bad, sed_ok, dict(ok, name="Patient 04 · nerve block", minutes=45)])
    want = [("07:30", "08:00", "Patient 01 · lumbar ESI"), ("08:15", "09:15", "Patient 02 · RFA"), ("09:30", "10:15", "Patient 04 · nerve block")]
    assert sched == want, f"room_schedule: expected {want}, got {sched}"
