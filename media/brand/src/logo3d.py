"""MOTION mark, dimensional version.

Each M is lit like a physical object instead of flat type:
  - bevelled relief (height from a blurred glyph mask) lit by a soft key light from top-left
  - lacquer gloss on the red trail, satin pearl with a fine brushed grain on the front M
  - the trail recedes in depth (each M behind is a little smaller and darker)
  - each M casts a soft shadow onto the one behind it, and sits *over* it (no additive merging)
Glyphs are shaded at 3x and downsampled, so edges stay crisp.

usage:
  python3 logo3d.py layers W H out_dir     -> RGBA layers L3_{W}x{H}_{m0..m3,word,sub}.png for the sting
  python3 logo3d.py lockup out.png [scale] -> transparent lockup (MMMM + MOTION + COLLECTIVE · AUSTIN)
  python3 logo3d.py mark out.png [scale]   -> transparent MMMM only
"""
import sys, os, math
import numpy as np
from PIL import Image

D = os.path.dirname(os.path.abspath(__file__))
SS = 3                                                   # glyph masks are rendered at 3x the 1080-base size

def load(name):
    return np.asarray(Image.open(f"{D}/A_{name}.png")).astype(np.float32) / 255

def box1d(a, r, axis):
    if r < 1: return a
    pad = [(0, 0)] * a.ndim; pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad), axis=axis)
    return (np.take(c, range(2 * r + 1, c.shape[axis]), axis=axis) - np.take(c, range(0, c.shape[axis] - 2 * r - 1), axis=axis)) / (2 * r + 1)

def blur(a, r):
    for _ in range(3): a = box1d(box1d(a, max(1, r // 3), 0), max(1, r // 3), 1)
    return a

def hexc(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255

# key light top-left and a little in front; faint cool rim from bottom-right
KEY = np.array([-0.55, -0.62, 0.56]); KEY /= np.linalg.norm(KEY)
RIM = np.array([0.7, 0.55, 0.45]); RIM /= np.linalg.norm(RIM)
HALF = KEY + np.array([0, 0, 1.0]); HALF /= np.linalg.norm(HALF)

MATS = {   # base colour, diffuse floor, gloss sharpness, gloss strength, clearcoat, brushed grain
    "m0": ("#5a171d", .12, 80, .55, .10, 0.0),
    "m1": ("#8e2f37", .12, 80, .60, .11, 0.0),
    "m2": ("#c04e56", .14, 70, .62, .12, 0.0),
    "m3": ("#f1ebe1", .22, 40, .50, .10, 0.0),
    "word": ("#efe9df", .40, 30, .35, .06, .0),
}

EXTRUDE = 26                                              # side-wall depth in hi-res px (~9 px at 1x)
EXTRUDE_DIR = (0.55, 0.85)
CHISEL = 22                                               # bevel width in hi-res px (~7 px at 1x)

def chisel(A, bw):
    B = A > 0.5; d = np.zeros(A.shape, np.float32); E = B.copy()
    for k in range(bw):                                   # octagonal distance via alternating 4/8-neighbour erosion
        n = E.copy()
        n[1:] &= E[:-1]; n[:-1] &= E[1:]; n[:, 1:] &= E[:, :-1]; n[:, :-1] &= E[:, 1:]
        if k % 2:
            n[1:, 1:] &= E[:-1, :-1]; n[:-1, :-1] &= E[1:, 1:]; n[1:, :-1] &= E[:-1, 1:]; n[:-1, 1:] &= E[1:, :-1]
        E = n; d += E
        if not E.any(): break
    d = (d + np.clip(A, 0, 1)) / bw                       # antialiased edge start
    for _ in range(2): d = box1d(box1d(d, 3, 0), 3, 1)    # soften the erosion stair steps, keep the facet edges
    return np.clip(d, 0, 1) ** 0.9

def shade(A, mat, relief=1.0, seed=0):
    """Light a glyph mask A (hi-res). Returns straight-alpha RGBA float."""
    base, floor_, p, ks, kc, brush = MATS[mat]
    base = hexc(base)
    pad = 80
    A = np.pad(A, pad)
    # relief: a chiselled bevel (distance from the edge, clipped), like letters cut in stone or metal.
    # Wide strokes get a flat top with sharp facets; hairlines become a single crisp ridge.
    h = chisel(A, CHISEL) * relief
    gy, gx = np.gradient(h * CHISEL * 1.1)
    n = np.stack([-gx, -gy, np.ones_like(h)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    ndl = np.clip(n @ KEY, 0, 1); ndr = np.clip(n @ RIM, 0, 1); ndh = np.clip(n @ HALF, 0, 1)
    fres = (1 - n[..., 2]) ** 2
    # soft vertical gradient across the letter: a studio light falling off toward the bottom
    yy = np.linspace(0, 1, A.shape[0])[:, None]
    fall = 1.05 - 0.22 * yy
    rng = np.random.default_rng(seed)
    tex = 1.0
    if brush:
        noise = rng.standard_normal(A.shape).astype(np.float32)
        tex = 1 + brush * box1d(noise, 40, 1) * 6                       # horizontal brushed grain
    col = base[None, None] * (floor_ + (1 - floor_) * ndl[..., None]) * (fall * tex)[..., None]
    col += (ks * ndh ** p + kc * ndh ** 6)[..., None] * np.array([1.0, .97, .93])   # warm-white gloss
    col += (0.10 * ndr ** 3)[..., None] * np.array([.75, .85, 1.0])                  # cool rim
    col += (0.18 * fres)[..., None] * base[None, None]
    # sandblasted micro-texture so the surface reads as a material, not flat ink
    micro = box1d(box1d(rng.standard_normal(A.shape).astype(np.float32), 1, 0), 1, 1)
    col *= (1 + 0.05 * micro)[..., None]
    col = np.clip(col, 0, 1)
    face = np.concatenate([col, A[..., None]], -1)
    if EXTRUDE and mat.startswith("m"):                   # real thickness (M's only; the wordmark stays fine): a side wall stepped back down-right
        side = np.zeros_like(face); dx, dy = EXTRUDE_DIR
        for k in range(EXTRUDE, 0, -1):
            sa = np.roll(np.roll(A, int(round(k * dy)), 0), int(round(k * dx)), 1)
            t = k / EXTRUDE                                   # deeper = darker; a little light catches the near edge
            sc = base * (0.42 - 0.30 * t) + 0.05 * (1 - t)
            side[..., :3] = side[..., :3] * (1 - sa[..., None]) + sc * sa[..., None]
            side[..., 3] = np.maximum(side[..., 3], sa)
        a_ = face[..., 3:4]
        face = np.concatenate([face[..., :3] * a_ + side[..., :3] * (1 - a_), np.maximum(a_, side[..., 3:4])], -1)
    return face[pad:-pad, pad:-pad]

def down(rgba, f):
    """Premultiplied downsample (no dark fringes)."""
    pm = np.concatenate([rgba[..., :3] * rgba[..., 3:4], rgba[..., 3:4]], -1)
    h, w = pm.shape[:2]; nw, nh = max(1, round(w * f)), max(1, round(h * f))
    chans = [np.asarray(Image.fromarray(pm[..., c]).resize((nw, nh), Image.LANCZOS)) for c in range(4)]
    pm = np.clip(np.stack(chans, -1), 0, 1)
    a = pm[..., 3:4]
    return np.concatenate([np.where(a > 1e-4, pm[..., :3] / np.maximum(a, 1e-4), 0), a], -1)

# trail geometry at the 1080 base (u = 1): step between M centres, depth scale per M
STEP = 160
DEPTH = [0.90, 0.935, 0.968, 1.0]

def glyph_layers(scale):
    """Shaded pieces at final size (scale = target px per 1080-base px) and their centres relative to the mark centre."""
    M = load("M"); word, sub = load("word"), load("sub")
    pieces = []
    for i in range(4):
        rg = down(shade(M, f"m{i}", seed=i), DEPTH[i] * scale / SS)
        pieces.append((f"m{i}", rg, ((i - 1.5) * STEP * scale, (1 - DEPTH[i]) * 0.5 * rg.shape[0] / DEPTH[i])))
    pieces.append(("word", down(shade(word, "word", relief=0.6, seed=9), scale / SS), (0, 0)))
    s = down(np.concatenate([np.ones(sub.shape + (3,), np.float32) * hexc("#9a968f"), sub[..., None]], -1), scale / SS)
    pieces.append(("sub", s, (0, 0)))
    return pieces

def place(canvas_hw, rgba, cx, cy):
    H, W = canvas_hw; out = np.zeros((H, W, 4), np.float32)
    h, w = rgba.shape[:2]; x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xs, ys = max(0, x0), max(0, y0); xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe > xs and ye > ys: out[ys:ye, xs:xe] = rgba[ys - y0:ye - y0, xs - x0:xe - x0]
    return out

def layers(W, H, out_dir):
    u = min(W, H) / 1080
    mark_cy, word_cy, sub_cy = H / 2 - 112 * u, H / 2 + 131 * u, H / 2 + 204 * u
    os.makedirs(out_dir, exist_ok=True)
    for name, rg, (dx, _dy) in glyph_layers(u):
        cy = {"word": word_cy, "sub": sub_cy}.get(name, mark_cy + _dy)
        L = place((H, W), rg, W / 2 + dx, cy)
        Image.fromarray((np.clip(L, 0, 1) * 255).astype(np.uint8), "RGBA").save(f"{out_dir}/L3_{W}x{H}_{name}.png")
    print("layers", W, H)

def over(dst, src):
    a = src[..., 3:4]
    rgb = src[..., :3] * a + dst[..., :3] * dst[..., 3:4] * (1 - a)
    al = a + dst[..., 3:4] * (1 - a)
    return np.concatenate([np.where(al > 1e-4, rgb / np.maximum(al, 1e-4), 0), al], -1)

def cast_shadow(dst, src_alpha, u, strength=0.62):
    """Darken what's already drawn by the soft shadow of the next (front) M."""
    sh = blur(np.roll(np.roll(src_alpha, int(14 * u), 1), int(10 * u), 0), max(2, int(16 * u)))
    out = dst.copy(); out[..., :3] *= (1 - strength * sh)[..., None]
    return out

def compose(W, H, pieces_xy, u):
    acc = np.zeros((H, W, 4), np.float32)
    for name, L in pieces_xy:
        if name.startswith("m") and name != "m0": acc = cast_shadow(acc, L[..., 3], u)
        acc = over(acc, L)
    return acc

def lockup(path, scale=3.0, with_text=True):
    W, H = int(1200 * scale), int((560 if with_text else 380) * scale)
    pcs = glyph_layers(scale); out = []
    mark_cy = 190 * scale
    for name, rg, (dx, _dy) in pcs:
        if not with_text and name in ("word", "sub"): continue
        cy = {"word": mark_cy + 243 * scale, "sub": mark_cy + 316 * scale}.get(name, mark_cy + _dy)
        out.append((name, place((H, W), rg, W / 2 + dx, cy)))
    img = compose(W, H, out, scale)
    a = img[..., 3]; ys, xs = np.where(a > 0.01); pad = int(30 * scale)
    img = img[max(0, ys.min() - pad):ys.max() + pad, max(0, xs.min() - pad):xs.max() + pad]
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGBA").save(path)
    print("saved", path, img.shape[1], "x", img.shape[0])

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "layers": layers(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    if cmd in ("lockup", "mark"): lockup(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 3.0, cmd == "lockup")
