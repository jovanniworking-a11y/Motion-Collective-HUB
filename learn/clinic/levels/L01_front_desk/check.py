def run(q):
    assert q.greeting("Jane") == "Welcome to Dr. Kim's Clinic, Jane!", f"greeting: got {q.greeting('Jane')!r}"
    for day, hour, want in [("Mon", 9, True), ("Mon", 8, False), ("Fri", 16, True), ("Fri", 17, False), ("Wed", 12, False), ("Wed", 13, True), ("Sat", 10, False), ("Sun", 10, False)]:
        assert q.is_open(day, hour) == want, f"is_open({day!r}, {hour}) should be {want}"
    assert q.sign("Tue", 10) == "OPEN" and q.sign("Sun", 10) == "CLOSED", "sign"
