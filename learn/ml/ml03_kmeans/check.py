import numpy as np
def run(m):
    rng = np.random.default_rng(2)
    true = np.array([[20, 5], [200, 60], [90, 120]], float)
    pts = np.concatenate([c + rng.normal(0, 6, (30, 2)) for c in true])
    best = None
    for seed in range(10):                                         # k-means can get stuck: restart and keep the best
        c, l = m.kmeans(pts, 3, seed=seed); c = np.asarray(c, float)
        cost = ((pts - c[np.asarray(l)]) ** 2).sum()
        if best is None or cost < best[0]: best = (cost, c, l)
    _, centers, labels = best
    for c in true:
        assert np.min(np.linalg.norm(np.asarray(centers) - c, axis=1)) < 10, f"no center found near {c.tolist()}; got {np.round(centers, 1).tolist()}"
    assert len(set(np.asarray(labels).tolist())) == 3, "labels should use 3 groups"
