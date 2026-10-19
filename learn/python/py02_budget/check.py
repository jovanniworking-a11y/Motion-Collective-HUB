def run(m):
    assert abs(m.total(m.ITEMS) - 347.42) < 1e-6, f"total: expected 347.42, got {m.total(m.ITEMS)}"
    assert m.buffer(450, m.ITEMS) == 102.58, f"buffer: expected 102.58, got {m.buffer(450, m.ITEMS)}"
    assert m.label_report(m.ITEMS) == {"confirmed": 241.42, "estimate": 106.0}, f"label_report: got {m.label_report(m.ITEMS)}"
