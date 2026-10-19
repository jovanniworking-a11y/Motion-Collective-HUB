import numpy as np
def run(m):
    rng = np.random.default_rng(0); x = rng.uniform(10, 80, 40); y = 1.4 * x + 5 + rng.normal(0, 3, 40)
    a, b = m.fit(x, y)
    assert abs(a - 1.4) < .1 and abs(b - 5) < 3, f"fit: expected about a=1.4, b=5, got a={a:.2f}, b={b:.2f}"
    yp = m.predict(a, b, x); s = m.r2(y, yp)
    assert s > .95, f"r2 should be > 0.95 for this data, got {s:.3f}"
    print(f"   39 RSVP heads -> about {m.predict(a, b, 39):.0f} people")
