def run(m):
    assert abs(m.beat_length(120) - .5) < 1e-9, "beat_length(120) should be 0.5"
    assert abs(m.beat_time(82.204, 142, 4) - (82.204 + 4 * 60 / 142)) < 1e-9, "beat_time"
    assert abs(m.beat_time(82.204, 142, -3) - (82.204 - 3 * 60 / 142)) < 1e-9, "beat_time with negative k"
    assert m.nearest_beat(82.204, 142, 112.55) == 72, f"nearest_beat: the hit at 112.55 s is beat 72, got {m.nearest_beat(82.204, 142, 112.55)}"
    assert isinstance(m.nearest_beat(82.204, 142, 90.0), int), "nearest_beat should return an int"
    assert abs(m.snap(82.204, 142, 112.55) - (82.204 + 72 * 60 / 142)) < 1e-9, "snap"
