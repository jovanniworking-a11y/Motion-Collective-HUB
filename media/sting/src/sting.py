"""MOTION sting: the logo 'touchdown' animation used at the start/end of every video.

Beats (30 fps, 3.0 s):
  0.00  black, two strobe ticks
  0.27  the four M's land left to right; each one leaves an AFTERIMAGE trail and
        fires an ASTIGMATISM flare (the starburst streaks you see from lights when drunk)
  1.00  MOTION fades in seeing double, then snaps into focus
  1.50  hold: flicker, grain, a slow flare sweep
  2.40  exit: everything smears right into its afterimage, one white strobe, black

Rendered on black so it can be laid over footage with a SCREEN blend (black disappears).
Red appears only in the MMMM trail itself, never as a tint.

usage: python3 sting.py W H out_dir
"""
import sys, os, math
import numpy as np
from PIL import Image

W, H, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
FPS, N = 30, 90
D = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(1030)

def layer(name):
    a = np.asarray(Image.open(f"{D}/L_{W}x{H}_{name}.png").convert("RGBA")).astype(np.float32) / 255
    return a[..., :3] * a[..., 3:4]                      # premultiplied RGB on black

M = [layer(f"m{i}") for i in range(4)]
WORD, SUB = layer("word"), layer("sub")
u = min(W, H) / 1080

def shift(img, dx, dy=0):
    dx, dy = int(round(dx)), int(round(dy))
    out = np.zeros_like(img)
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    out[yd, xd] = img[ys, xs]
    return out

def box1d(a, r, axis):
    """Fast box blur along one axis (cumulative sum)."""
    if r < 1: return a
    pad = [(0, 0)] * a.ndim; pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="constant"), axis=axis)
    hi = np.take(c, range(2 * r + 1, c.shape[axis]), axis=axis)
    lo = np.take(c, range(0, c.shape[axis] - 2 * r - 1), axis=axis)
    return (hi - lo) / (2 * r + 1)

def soft1d(a, r, axis):
    """Tapered blur along one axis (three box passes approximate a gaussian, so streaks fade out)."""
    for _ in range(3): a = box1d(a, max(1, r // 3), axis)
    return a

def astig(img, k):
    """Astigmatism flare: thin NEUTRAL light streaks out of the brightest points only.
    Uses luminance, so the red of the M's never bleeds into a pink glow (red stays an accent)."""
    if k <= 0: return 0
    lum = img.mean(axis=2, keepdims=True)
    hot = np.clip((lum - 0.72) / 0.28, 0, 1) ** 2
    h = soft1d(soft1d(hot, int(260 * u), 1), int(3 * u), 0) * 1.3
    v = soft1d(soft1d(hot, int(110 * u), 0), int(3 * u), 1) * 0.7
    glow = soft1d(soft1d(hot, int(18 * u), 0), int(18 * u), 1) * 0.55
    return np.repeat(np.minimum(k * (h + v + glow), 0.45), 3, axis=2)

# strobe light lives only around the mark: a faint ghost of the full logo plus a soft halo, never a grey full frame
LOGO = sum(M) + WORD
_l = LOGO.mean(axis=2, keepdims=True)
HALO = np.repeat(np.clip(_l * 0.5 + box1d(box1d(box1d(box1d(_l, int(90 * u), 1), int(90 * u), 0), int(90 * u), 1), int(90 * u), 0) * 2.2, 0, 1), 3, axis=2)

def ease_out(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3

trail = np.zeros((H, W, 3), np.float32)
os.makedirs(OUT, exist_ok=True)
for f in range(N):
    t = f / FPS
    frame = np.zeros((H, W, 3), np.float32)
    flash = 0.0
    # strobe ticks
    if f in (3, 6): flash = 0.35 if f == 3 else 0.6
    # four M's land, 5 frames apart, sliding in from the left
    flare = 0.0
    for i in range(4):
        f0 = 8 + 5 * i
        if f < f0: continue
        p = ease_out((f - f0) / 6)
        frame += shift(M[i], -140 * u * (1 - p)) * min(1, (f - f0 + 1) / 2)
        if f0 <= f < f0 + 2: flash = max(flash, 0.12 if i < 3 else 0.25)
        if f0 <= f < f0 + 7: flare = max(flare, (1 - (f - f0) / 7) * (0.4 if i < 3 else 0.6))
    # MOTION: double vision converging, then sharp
    if f >= 30:
        p = ease_out((f - 30) / 14)
        off = 26 * u * (1 - p)
        a = min(1, (f - 30) / 8)
        if off > 0.5:
            frame += (shift(WORD, -off, -off * .25) + shift(WORD, off, off * .25)) * 0.55 * a
        else:
            frame += WORD
    if f >= 44: frame += SUB * min(1, (f - 44) / 8)
    # hold: slow flare sweep across the mark
    if 48 <= f < 72: flare = max(flare, 0.08 + 0.12 * math.sin((f - 48) / 24 * math.pi))
    # exit: smear right into the afterimage
    if f >= 72:
        p = (f - 72) / 10
        frame = shift(frame, 260 * u * p ** 2) * max(0, 1 - p * 1.1)
        flare = max(flare, 0.3 * (1 - p))
    # afterimage: the trail keeps a decaying, slightly drifting copy of everything bright
    trail = np.maximum(trail * 0.80, shift(frame, 6 * u) * 0.9)
    trail = box1d(trail, int(3 * u), 1)
    out = np.maximum(frame, trail * 0.75) + astig(frame + trail * 0.3, flare)
    if f == 82: out = np.ones_like(out) * 0.85          # single white strobe on the exit
    if f > 82: out = out * 0
    # flicker + film grain (monochrome)
    flick = 1.0 - (0.08 * rng.random() if 30 <= f < 82 else 0)
    out = out * flick + flash * HALO
    grain = (rng.standard_normal((H, W, 1)).astype(np.float32)) * 0.045
    out = np.clip(out + grain * (0.6 + 0.4 * (out.mean(axis=2, keepdims=True) < 0.05)), 0, 1)
    Image.fromarray((out * 255).astype(np.uint8)).save(f"{OUT}/f{f:03d}.png")
print("frames", N, W, H)
