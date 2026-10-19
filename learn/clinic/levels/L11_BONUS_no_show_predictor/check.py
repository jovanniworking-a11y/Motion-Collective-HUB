import numpy as np
def data(n, seed):
    r = np.random.default_rng(seed); lead = r.integers(0, 60, n); past = r.poisson(0.6, n)
    p = 1 / (1 + np.exp(-(-4.5 + 0.11 * lead + 2.0 * past))); y = (r.random(n) < p).astype(float)
    return np.column_stack([lead, past]).astype(float), y
def run(q):
    assert abs(q.sigmoid(0) - .5) < 1e-9, "sigmoid(0) should be 0.5"
    X, y = data(1500, 3); Xt, yt = data(600, 4)
    m = q.train(X, y); acc = (q.predict(m, Xt) == yt).mean(); base = max(yt.mean(), 1 - yt.mean())
    assert acc >= .75 and acc > base, f"accuracy {acc:.0%} (always guessing gets {base:.0%}); needs 75% and to beat that"
    w = np.asarray(m["w"]).ravel(); assert w[0] > 0 and w[1] > 0, "both facts should push the risk up (positive weights)"
    print(f"   accuracy {acc:.0%} vs {base:.0%} for always guessing")
