import numpy as np
def blur(a, k=5):
    out = a.copy()
    for _ in range(k): out = (out + np.roll(out, 1, 0) + np.roll(out, -1, 0) + np.roll(out, 1, 1) + np.roll(out, -1, 1)) / 5
    return out
def run(m):
    rng = np.random.default_rng(1)
    sharp = [rng.uniform(0, 255, (64, 64)) for _ in range(20)]; blurry = [blur(rng.uniform(0, 255, (64, 64))) for _ in range(20)]
    t = m.learn_threshold([m.sharpness(a) for a in sharp[:10]], [m.sharpness(a) for a in blurry[:10]])
    test = [(a, "sharp") for a in sharp[10:]] + [(a, "blurry") for a in blurry[10:]]
    acc = sum(m.classify(a, t) == lab for a, lab in test) / len(test)
    assert acc >= .9, f"accuracy {acc:.0%}, needs 90%"
    print(f"   accuracy on unseen frames: {acc:.0%}")
