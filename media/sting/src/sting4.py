"""MOTION sting v4: the dimensional mark, animated fluidly (3.0 s, 30 fps).

  0.00-0.27  light gathers where the mark will be (anticipation)
  0.20-0.73  the white M flies in out of the dark: scale 2.6 -> 1 on an expo curve with a small spring settle,
             real motion blur (sub-frame), astigmatism streaks + glow flare as it lands
  0.53-1.20  the three red M's peel out of it to the left, one after another (overlapping action),
             each passing behind the one in front, leaving an afterimage, casting live shadows
  1.00-1.70  MOTION tracks in (letters close up from wide spacing) and resolves from soft to sharp
  1.33-1.93  a specular light sweep crosses the mark
  2.47-2.93  exit: the trail collapses back into the white M, which flies through camera with zoom blur
Black background, so it lays over footage with Screen. Red only in the three trailing M's.

usage: python3 sting4.py W H out_dir
"""
import sys, os, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fx"))
import mfx

W, H, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
D = os.path.dirname(os.path.abspath(__file__))
N, FPS = 90, 30
u = min(W, H) / 1080
rng = np.random.default_rng(1030)

def load(name):
    a = np.asarray(Image.open(f"{D}/L3_{W}x{H}_{name}.png").convert("RGBA")).astype(np.float32) / 255
    a[..., :3] *= a[..., 3:4]                      # premultiply
    return a

M = [load(f"m{i}") for i in range(4)]
WORD, SUB = load("word"), load("sub")

def centre(L):
    ys, xs = np.where(L[..., 3] > .1); return (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2

CM = [centre(L) for L in M]
CX, CY = CM[3]                                     # the white (front) M

def xf(L, z=1.0, dx=0.0, dy=0.0, rot=0.0, about=None):
    """Affine move of a premultiplied RGBA layer: zoom z about a point, then translate."""
    if abs(z - 1) < 1e-4 and abs(dx) < .01 and abs(dy) < .01 and abs(rot) < 1e-3: return L
    px, py = about if about else (W / 2, H / 2)
    a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
    A, B, Dd, E = ca / z, sa / z, -sa / z, ca / z
    ox, oy = px + dx, py + dy
    C = px - A * ox - B * oy; F = py - Dd * ox - E * oy
    return np.stack([np.asarray(Image.fromarray(L[..., c]).transform((W, H), Image.AFFINE, (A, B, C, Dd, E, F), resample=Image.BILINEAR))
                     for c in range(4)], -1)

def over(dst, src): return src + dst * (1 - src[..., 3:4])

# word split into letters so it can track in (luxury type move)
def letters(L):
    col = L[..., 3].max(axis=0) > .02
    segs, x = [], 0
    while x < W:
        if col[x]:
            s = x
            while x < W and col[x]: x += 1
            segs.append((s, x))
        x += 1
    return segs
SEGS = letters(WORD)

def word_at(spread, soft):
    out = np.zeros_like(WORD); cx = W / 2
    for s, e in SEGS:
        piece = np.zeros_like(WORD); piece[:, s:e] = WORD[:, s:e]
        mid = (s + e) / 2
        out += mfx.shift(piece, (mid - cx) * (spread - 1))
    if soft > .3: out = np.stack([mfx.blur(out[..., c], soft) for c in range(4)], -1)
    return out

def mark_state(t):
    """Per-M transform at time t (frames, fractional). Returns list of (alpha_mult, z, dx, dy, rot)."""
    st = []
    # white M flight
    p = (t - 6) / 16
    if t < 6: w = (0, 1, 0, 0, 0)
    elif t < 74:
        e = mfx.expo_out(p); s = mfx.spring(max(0, p) * 1.1, damp=5.5, freq=1.6)
        z = 1 + 1.6 * (1 - e) + 0.03 * (1 - s) * (p > .6)
        w = (min(1, (t - 6) / 4), z, 0, -40 * u * (1 - e), 6 * (1 - e))
    else: w = (1, 1, 0, 0, 0)
    # red M's peel out of the white one (m2 first, then m1, m0)
    for i in range(3):
        t0 = 16 + (2 - i) * 4
        tx = CM[3][0] - CM[i][0]                   # offset that puts M_i on top of the white M
        if t < t0: st.append((0, 1, tx, 0, 0)); continue
        q = mfx.expo_out((t - t0) / 13)
        st.append((min(1, (t - t0) / 3), 1, tx * (1 - q), 0, 0))
    st.append(w)
    # exit: collapse back into the white M, then fly through camera
    if t >= 74:
        c = mfx.ease_in((t - 74) / 6, 3)
        for i in range(3):
            tx = CM[3][0] - CM[i][0]; a, z, dx, dy, r = st[i]
            st[i] = (a * (1 - .6 * c), z, tx * c, dy, r)
        if t >= 79:
            f = mfx.ease_in((t - 79) / 8, 3)
            st = [(a * (1 - f) ** .5, z * (1 + 3.2 * f), dx, dy, r) for a, z, dx, dy, r in st]
    return st

def render_mark(t):
    canvas = np.zeros((H, W, 4), np.float32)
    for i, (a, z, dx, dy, r) in enumerate(mark_state(t)):
        if a <= 0: continue
        L = xf(M[i], z, dx, dy, r, about=(CX, CY)) * a
        if i:                                       # live soft shadow on the M's behind
            sh = mfx.qblur(mfx.shift(L[..., 3], 12 * u, 9 * u), 16 * u)
            canvas[..., :3] *= (1 - 0.55 * sh)[..., None]; canvas[..., 3] = np.maximum(canvas[..., 3], 0)
        canvas = over(canvas, L)
    return canvas

def moving(t): return 4 <= t <= 40 or t >= 73
echo = mfx.Echo((H, W, 3))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
os.makedirs(OUT, exist_ok=True)
for f in range(N):
    mk = mfx.mblur(render_mark, f, shutter=0.5, n=6) if moving(f) else render_mark(f)
    rgb = mk[..., :3]
    # afterimage only while the mark is moving
    rgb = echo(rgb, decay=0.62, mix=0.42) if moving(f) else (echo.reset() or rgb)
    frame = rgb.copy()
    # anticipation: light gathers where the white M will land
    if f < 10:
        gl = mfx.qblur(M[3][..., 3], 120 * u) * 0.5 * mfx.ease_in(f / 10, 2) * (1 - max(0, f - 7) / 3)
        frame = frame + gl[..., None]
    # MOTION tracks in, COLLECTIVE · AUSTIN follows
    if 30 <= f < 80:
        p = mfx.expo_out((f - 30) / 20)
        wd = word_at(1 + 0.5 * (1 - p), 10 * u * (1 - p)) * min(1, (f - 30) / 8)
        if f >= 74: wd = wd * (1 - (f - 74) / 6)
        frame = frame * (1 - wd[..., 3:4]) + wd[..., :3]
    if 44 <= f < 80:
        sa = min(1, (f - 44) / 10) * (1 - max(0, f - 74) / 6)
        frame = frame * (1 - SUB[..., 3:4] * sa) + SUB[..., :3] * sa
    # specular light sweep across the mark
    if 40 <= f < 58:
        pos = -300 * u + (W + 600 * u) * mfx.ease_io((f - 40) / 18)
        band = np.exp(-(((xx + (yy - CY) * 0.45) - pos) / (55 * u)) ** 2)
        frame = frame + (0.55 * band * mk[..., 3])[..., None]
    # glow: always a soft bloom; a flare on the landing
    lum = frame.mean(axis=2)
    land = max(0.0, 1 - abs(f - 21) / 7)
    if f >= 6:
        frame = frame + (mfx.deep_glow(lum, 0.22 + 0.5 * land, thr=0.55) - lum)[..., None] * np.array([1, .98, .96])
        if land > 0: frame = frame + (mfx.astig(lum, 0.35 * land, thr=0.8) - lum)[..., None]
    # camera: slow push on the hold
    if 22 <= f < 74:
        z = 1 + 0.035 * mfx.ease_io((f - 22) / 52)
        frame = np.stack([np.asarray(Image.fromarray(frame[..., c].astype(np.float32)).transform(
            (W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR)) for c in range(3)], -1)
    if f >= 80: frame = mfx.zoom_blur(frame, 0.25 * mfx.ease_in((f - 79) / 8), n=7, cx=CX / W, cy=CY / H)
    if f >= 88: frame = frame * 0
    frame = mfx.grain(frame, 0.028, rng=rng)
    Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8)).save(f"{OUT}/f{f:03d}.png")
    if f % 15 == 0: print("frame", f, flush=True)
print("frames", N, W, H)
