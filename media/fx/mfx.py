"""MOTION FX: the house effects library (numpy + PIL + ffmpeg, no After Effects needed).

Each effect is named after the plugin look it stands in for, so the team can talk in pro terms:
  RENDER / FINISH   promist (Tiffen Black Pro-Mist), deep_glow (Deep Glow / S_Glow), grain (FilmConvert/Dehancer),
                    film_curve (film shoulder), vignette
  MOTION            xform (camera: zoom/pan/rotate), mblur (ReelSmart Motion Blur: real sub-frame motion blur),
                    shake (S_Shake impact), ease / spring (Animation Composer-style curves)
  TIME              plate(...) decodes denoised plates, with optional optical-flow frames (Twixtor-style ramps)
  TRANSITIONS       whip (whip pan), zoom_blur (CC Radial Fast Blur zoom transition), luma_fade (luma key reveal),
                    defocus (rack-focus dissolve), flash (S_Flicker exposure flash), slices (S_Zap-ish break-up)
  STYLE             echo (Echo / Time Displacement afterimage), triptych (three-band split, our eyes motif),
                    letterbox (film bars), astig (light streaks), tracking_in (luxury type tracking)
Everything is monochrome on purpose. Red stays an accent added by the caller (MMMM, b2b), never a tint.
Deliberately left out: chromatic aberration / RGB split (adds coloured fringes = a tint), acid colour washes,
heavy wave warps (reads cheap, "trippy").
"""
import math, subprocess
import numpy as np
from PIL import Image

W, H, FPS = 1080, 1920, 30

# ---------------------------------------------------------------- curves
def clamp01(t): return min(max(t, 0.0), 1.0)
def ease_out(t, p=3): t = clamp01(t); return 1 - (1 - t) ** p
def ease_in(t, p=3): t = clamp01(t); return t ** p
def ease_io(t): t = clamp01(t); return t * t * (3 - 2 * t) if t < 1 else 1.0
def expo_out(t): t = clamp01(t); return 1 - 2 ** (-10 * t) if t < 1 else 1.0
def expo_io(t):
    t = clamp01(t)
    if t in (0, 1): return t
    return 2 ** (20 * t - 10) / 2 if t < .5 else (2 - 2 ** (-20 * t + 10)) / 2
def spring(t, damp=6.0, freq=2.2):
    """Overshoot-and-settle (Animation Composer 'elastic'/Flow spring). 0 -> 1."""
    if t <= 0: return 0.0
    return 1 - math.exp(-damp * t) * math.cos(2 * math.pi * freq * t)

# ---------------------------------------------------------------- blur helpers
def box1d(a, r, axis):
    r = int(r)
    if r < 1: return a
    pad = [(0, 0)] * a.ndim; pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad), axis=axis, dtype=np.float32)
    n = c.shape[axis]
    return (np.take(c, range(2 * r + 1, n), axis=axis) - np.take(c, range(0, n - 2 * r - 1), axis=axis)) / (2 * r + 1)

def blur(a, r, passes=3):
    r = max(1, int(r / math.sqrt(passes)))
    for _ in range(passes): a = box1d(box1d(a, r, 0), r, 1)
    return a

def small(a, f=4):
    h, w = a.shape[:2]
    return np.asarray(Image.fromarray(a.astype(np.float32)).resize((w // f, h // f), Image.BILINEAR))

def big(a, shape):
    return np.asarray(Image.fromarray(a.astype(np.float32)).resize((shape[1], shape[0]), Image.BILINEAR))

def qblur(a, r):
    """Large-radius blur done at quarter size (for glows), returned full size."""
    return big(blur(small(a), max(1, r / 4)), a.shape)

# ---------------------------------------------------------------- plates (footage)
def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(",")
    return int(out[0]), int(out[1])

def plate(path, t0=None, t1=None, fps=30, interp=False, denoise=True, deflicker=False):
    """Decode a clip to grey uint8 frames at native size.
    denoise: hqdn3d before any scaling, so blocky phone compression doesn't get magnified.
    deflicker: even out frame-to-frame exposure jumps from strobes.
    interp: optical-flow motion-compensated frames (ffmpeg minterpolate), like Twixtor, for smooth slow motion."""
    w, h = probe(path)
    vf = []
    if denoise: vf.append("hqdn3d=3:2:5:4")
    if deflicker: vf.append("deflicker=size=9:mode=median")   # tame phone-camera strobe washouts (keeps the shot, drops the white frames)
    vf.append(f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" if interp else f"fps={fps}")
    cmd = ["ffmpeg", "-v", "error"]
    if t0 is not None: cmd += ["-ss", f"{t0:.3f}"]
    cmd += ["-i", path]
    if t1 is not None: cmd += ["-t", f"{t1 - (t0 or 0):.3f}"]
    cmd += ["-vf", ",".join(vf), "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)

def cover(g, z=1.0, dx=0.0, dy=0.0, rot=0.0, cx=0.5, cy=0.5, out=(W, H)):
    """Place a native plate frame into the output with a virtual camera.
    z zoom, dx/dy pan in output px, rot degrees, (cx, cy) zoom centre as a fraction of the plate.
    One resampling step from the native plate (Lanczos-quality bicubic), never resample twice."""
    h, w = g.shape; OW, OH = out
    s = max(OW / w, OH / h) * z
    a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
    # output pixel (x, y) -> plate pixel
    px, py = cx * w, cy * h
    ox, oy = OW / 2 + dx, OH / 2 + dy
    A = ca / s; B = sa / s; D = -sa / s; E = ca / s
    C = px - A * ox - B * oy; F = py - D * ox - E * oy
    im = Image.fromarray(g).transform((OW, OH), Image.AFFINE, (A, B, C, D, E, F), resample=Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255

def mblur(render, t, shutter=0.5, n=7):
    """ReelSmart-style motion blur for anything we animate ourselves: average sub-frame renders across the shutter.
    render(t) -> frame; t in frames. shutter 0.5 = 180-degree shutter (film standard)."""
    if n <= 1 or shutter <= 0: return render(t)
    acc = None
    for i in range(n):
        f = render(t - shutter * (1 - i / (n - 1)))
        acc = f if acc is None else acc + f
    return acc / n

def shake(t, t_hit, amp=18.0, decay=7.0, freq=11.0, seed=0):
    """Impact shake after a hit (S_Shake / Universe Shake): returns (dx, dy, rot) in px/deg. t, t_hit in frames."""
    dt = (t - t_hit) / FPS
    if dt < 0: return 0.0, 0.0, 0.0
    e = amp * math.exp(-decay * dt)
    r = np.random.default_rng(seed)
    p1, p2, p3 = r.uniform(0, 6.28, 3)
    return (e * math.sin(2 * math.pi * freq * dt + p1), e * 0.7 * math.sin(2 * math.pi * freq * 1.3 * dt + p2),
            e * 0.035 * math.sin(2 * math.pi * freq * 0.8 * dt + p3))

# ---------------------------------------------------------------- finish
def film_curve(x, black=0.06, gain=1.35, gamma=1.08, shoulder=2.4):
    """Expose, then roll the highlights off like film instead of clipping (no 'deep fried' whites)."""
    x = np.clip((x - black) * gain, 0, None) ** gamma
    return (1 - np.exp(-shoulder * x)) / (1 - math.exp(-shoulder * 1.25))

def promist(x, strength=0.45, r=48):
    """Black Pro-Mist diffusion: highlights bleed a soft halo, contrast stays.
    Also hides upscaling blocks: fine detail softens, light spreads like a real lens filter."""
    hl = np.clip((x - 0.45) / 0.55, 0, 1) ** 1.6
    halo = qblur(hl, r)
    return x + strength * halo * (1 - x) * 1.25

def deep_glow(x, strength=0.5, thr=0.62, radii=(6, 20, 64, 180), weights=(.35, .3, .22, .13)):
    """Deep Glow: physically-plausible bloom, many radii summed with falloff (used on logos and light sources)."""
    hl = np.clip((x - thr) / (1 - thr), 0, 1)
    acc = 0
    for r, wgt in zip(radii, weights):
        acc = acc + wgt * (blur(hl, r) if r < 12 else qblur(hl, r))
    return x + strength * acc

def grain(x, amt=0.05, size=1.4, rng=None):
    """Film grain: clumped (not per-pixel TV noise), strongest in the midtones, like scanned 35mm."""
    rng = rng or np.random.default_rng()
    h, w = x.shape[:2]
    gh, gw = int(h / size), int(w / size)
    n = rng.standard_normal((gh, gw)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
    lum = x if x.ndim == 2 else x.mean(axis=2)
    m = 0.35 + 2.6 * lum * (1 - lum)
    n = n * m * amt
    return x + (n if x.ndim == 2 else n[..., None])

_VIG = {}
def vignette(x, k=0.32):
    key = x.shape[:2]
    if key not in _VIG:
        h, w = key; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        _VIG[key] = 1 - k * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 2
    v = _VIG[key]
    return x * (v if x.ndim == 2 else v[..., None])

def astig(x, k=0.4, thr=0.74, cap=0.3):
    """Astigmatism streaks (Optical Flares-lite, neutral white): long horizontal + short vertical streaks off hot points."""
    if k <= 0: return x
    q = small(x)
    hot = np.clip((q - thr) / (1 - thr), 0, 1) ** 2
    st = blur(box1d(hot, 60, 1), 1) * 1.5 + blur(box1d(hot, 24, 0), 1) * .6 + blur(hot, 5) * .4
    return x + np.minimum(big(st * k, x.shape), cap)

def finish(x, rng=None, mist=0.45, glow=0.0, grain_amt=0.05, vig=0.3):
    """The house look in one call: film curve already applied by the caller, then mist, glow, vignette, grain."""
    if mist: x = promist(x, mist)
    if glow: x = deep_glow(x, glow)
    if vig: x = vignette(x, vig)
    x = grain(x, grain_amt, rng=rng)
    return np.clip(x, 0, 1)

# ---------------------------------------------------------------- transitions / style
def shift(img, dx, dy=0):
    dx, dy = int(round(dx)), int(round(dy)); h, w = img.shape[:2]
    out = np.zeros_like(img)
    if abs(dx) >= w or abs(dy) >= h: return out
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    out[yd, xd] = img[ys, xs]; return out

def directional_blur(x, px, axis=1):
    """Fast motion smear along one axis (used for whips): px = travel during the shutter."""
    return box1d(x, max(1, int(abs(px) / 2)), axis) if abs(px) > 2 else x

def whip(a, b, p, dist=W * 1.1, direction=1):
    """Whip pan: A flies out, B flies in from the other side, both smeared by their speed. p 0->1."""
    e = expo_io(p); v = abs(dist * (expo_io(min(1, p + .04)) - expo_io(max(0, p - .04)))) / .08 / FPS * 2.2
    if p < .5:
        return directional_blur(shift(a, -direction * dist * e), v)
    return directional_blur(shift(b, direction * dist * (1 - e)), v)

def zoom_blur(x, amt, n=9, cx=0.5, cy=0.5):
    """CC Radial Fast Blur look: average of the frame scaled 1 -> 1+amt about a centre."""
    if amt < 0.004: return x
    if x.ndim == 3: return np.stack([zoom_blur(x[..., c], amt, n, cx, cy) for c in range(x.shape[2])], -1)
    h, w = x.shape[:2]; acc = 0
    for i in range(n):
        z = 1 + amt * i / (n - 1)
        a = 1 / z; c = cx * w * (1 - a); f = cy * h * (1 - a)
        acc = acc + np.asarray(Image.fromarray(x.astype(np.float32)).transform((w, h), Image.AFFINE, (a, 0, c, 0, a, f), resample=Image.BILINEAR))
    return acc / n

def zoom_transition(a, b, p, amt=0.5):
    """Zoom-through: punch into A with radial blur, land on B pulling out of the same blur (hide the cut at the peak)."""
    if p < .5:
        q = ease_in(p * 2, 2); return zoom_blur(a, amt * q)
    q = 1 - ease_out((p - .5) * 2, 2); return zoom_blur(b, amt * q)

def luma_fade(a, b, p, soft=0.12, use='b'):
    """Luma-key reveal: B appears through its brightest areas first (lights, faces of the crowd), then fills in."""
    key = b if use == 'b' else a
    k = qblur(key, 10)
    th = 1 - p * (1 + soft)
    m = np.clip((k - th) / soft, 0, 1)
    return a * (1 - m) + b * m

def defocus(a, b, p, r=40):
    """Rack-focus dissolve: A goes soft, B resolves out of the softness. Elegant, fashion-film transition."""
    if p < .5:
        q = ease_in(p * 2); return qblur(a, 1 + r * q) if q > .02 else a
    q = 1 - ease_out((p - .5) * 2); return qblur(b, 1 + r * q) if q > .02 else b

def flash(x, p, peak=0.85):
    """Exposure flash (S_Flicker style): push exposure then fall back, never a flat grey card."""
    k = peak * max(0.0, 1 - p) ** 2
    return x + (1 - x) * k

def slices(x, amt, n=7, seed=0):
    """Break-up: horizontal slices slide apart in alternating directions (S_Zap / glitch, kept clean)."""
    if amt <= .5: return x
    r = np.random.default_rng(seed); h = x.shape[0]
    edges = np.sort(np.r_[0, r.choice(np.arange(60, h - 60), n - 1, replace=False), h])
    out = np.zeros_like(x)
    for i in range(n):
        y0, y1 = edges[i], edges[i + 1]
        out[y0:y1] = shift(x, (1 if i % 2 else -1) * r.uniform(.5, 1) * amt)[y0:y1]
    return out

class Echo:
    """Echo / Time Displacement afterimage: a decaying copy that trails behind motion."""
    def __init__(self, shape): self.buf = np.zeros(shape, np.float32)
    def __call__(self, x, decay=0.62, mix=0.4, drift=0):
        self.buf = np.maximum(self.buf * decay, shift(x, drift) if drift else x)
        return np.maximum(x, self.buf * mix)
    def reset(self): self.buf[:] = 0

def letterbox(x, h):
    if h >= x.shape[0]: return x
    out = x.copy(); t = (x.shape[0] - int(h)) // 2
    out[:t] = 0; out[t + int(h):] = 0; return out

def triptych(frames, gap=8):
    """Three horizontal bands, three moments: the eye-triptych motif applied to footage."""
    h = frames[0].shape[0]; bh = (h - 2 * gap) // 3; out = np.zeros_like(frames[0])
    for i, f in enumerate(frames[:3]):
        y = i * (bh + gap); c = (h - bh) // 2
        out[y:y + bh] = f[c:c + bh]
    return out

def over(base, rgb, a):
    """Straight alpha over. base/rgb (H,W,3), a (H,W,1)."""
    return base * (1 - a) + rgb * a

def screen(a, b): return 1 - (1 - a) * (1 - b)

# ================================================================ v2: the rest of the popular plugin looks
# Tagged ON/OFF brand in the gallery. OFF-brand effects are here so the team knows them by name, not to use on MOTION.

def _edge(a, r=2):
    """Outline of a mask/alpha (a - eroded a), soft."""
    return np.clip(a - np.clip((blur(a, r) - 0.5) * 2.2 + 0.5, 0, 1) * a + np.clip(blur(a, r) - a, 0, 1), 0, 1)

def saber(alpha, t=0, core=1.0, glow=0.9, flicker=0.15, seed=0):
    """Video Copilot Saber: an energy glow running along a shape's outline (type, logo). Returns a 2-D light layer."""
    e = _edge(alpha, 3)
    r = np.random.default_rng(int(t) + seed)
    k = 1 - flicker * r.random()
    return np.clip(e * core * k + glow * k * (blur(e, 6) * 1.6 + qblur(e, 30) * 1.2), 0, 1.5)

def lens_flare(x, cx, cy, k=0.6):
    """Optical Flares-style flare, neutral: anamorphic streak + soft core + ghosts mirrored through the frame centre."""
    h, w = x.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
    core = np.exp(-d2 / (2 * (0.03 * w) ** 2))
    streak = np.exp(-((yy - cy) / (0.006 * h)) ** 2) * np.exp(-np.abs(xx - cx) / (0.45 * w))
    out = core * 0.9 + streak * 0.8
    for f, rad, a in ((-0.4, .05, .18), (-0.8, .09, .12), (0.35, .03, .22), (-1.25, .14, .08)):
        gx = w / 2 + (cx - w / 2) * f; gy = h / 2 + (cy - h / 2) * f
        dd = np.sqrt((xx - gx) ** 2 + (yy - gy) ** 2) / (rad * w)
        out += a * np.clip(1 - dd, 0, 1) ** 0.6 * (0.6 + 0.4 * (dd > 0.8))
    return x + k * out if x.ndim == 2 else x + k * out[..., None]

def rays(x, cx=0.5, cy=0.35, k=0.7, thr=0.6, length=0.6):
    """Sapphire S_Rays / CC Light Rays: god rays streaming out of the bright areas from a light centre."""
    hl = np.clip((x - thr) / (1 - thr), 0, 1)
    q = small(hl, 4)
    r = zoom_blur(q, length, n=14, cx=cx, cy=cy)
    return x + k * big(r, x.shape)

def twitch(x, t, seed=0, amount=1.0):
    """Video Copilot Twitch: random frames jump (scale/offset/exposure/blur) for a nervous, live energy."""
    r = np.random.default_rng(int(t) * 7 + seed)
    if r.random() > 0.35 * amount: return x
    z = 1 + r.uniform(0, .06) * amount; dx, dy = r.uniform(-30, 30, 2) * amount
    h, w = x.shape[:2]; a = 1 / z
    y = np.asarray(Image.fromarray(x.astype(np.float32)).transform((w, h), Image.AFFINE, (a, 0, w / 2 * (1 - a) - dx * a, 0, a, h / 2 * (1 - a) - dy * a), resample=Image.BILINEAR))
    y = y * r.uniform(0.85, 1.25)
    return blur(y, 2) if r.random() < .3 else y

def block_glitch(x, prev, amt=0.3, block=48, seed=0):
    """Datamosh / Universe Glitch blocks: some macro-blocks keep the previous frame or slide, like a broken codec."""
    r = np.random.default_rng(seed); h, w = x.shape[:2]; out = x.copy()
    for by in range(0, h, block):
        for bx in range(0, w, block):
            if r.random() < amt:
                sx = int(np.clip(bx + r.integers(-2, 3) * block // 2, 0, w - block)); out[by:by + block, bx:bx + block] = prev[by:by + block, sx:sx + block][:out[by:by + block, bx:bx + block].shape[0], :out[by:by + block, bx:bx + block].shape[1]]
    return out

def rgb_split(x, px=8):
    """Shift Channels / chromatic aberration. OFF-BRAND for MOTION (adds red/cyan fringes = a tint)."""
    g = x if x.ndim == 2 else x.mean(axis=2)
    return np.stack([shift(g, px), g, shift(g, -px)], -1)

def reflect(x, floor=0.72, fade=0.35, strength=0.45):
    """VC Reflect: a mirrored copy below a floor line, fading out (glossy floor under a logo or a DJ)."""
    h = x.shape[0]; y0 = int(h * floor); out = x.copy()
    src = x[max(0, 2 * y0 - h):y0][::-1]
    n = min(len(src), h - y0)
    ramp = np.clip(1 - np.arange(n) / (fade * h), 0, 1) * strength
    ramp = ramp[:, None] if x.ndim == 2 else ramp[:, None, None]
    out[y0:y0 + n] = np.maximum(out[y0:y0 + n], src[:n] * ramp)
    return out

_FIELD = {}
def heat_haze(x, t, amt=6.0, scale=90):
    """Heat Distortion: a slow, smooth displacement field (shimmer above a hot surface)."""
    h, w = x.shape[:2]
    key = (h, w, scale)
    if key not in _FIELD:
        r = np.random.default_rng(3); _FIELD[key] = [qblur(r.standard_normal((h, w)).astype(np.float32), scale) for _ in range(2)]
    fx, fy = _FIELD[key]; fx = fx / (np.abs(fx).max() + 1e-6); fy = fy / (np.abs(fy).max() + 1e-6)
    yy, xx = np.mgrid[0:h, 0:w]
    ph = t * 0.15
    dx = (np.roll(fx, int(ph * 20), 0) * amt).astype(int); dy = (np.roll(fy, int(ph * 30), 0) * amt).astype(int)
    return x[np.clip(yy + dy, 0, h - 1), np.clip(xx + dx, 0, w - 1)]

def warp(x, t, amp=24, period=260):
    """Wave Warp / Turbulent Displace. OFF-BRAND for MOTION (reads trippy)."""
    h, w = x.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    dx = (amp * np.sin(2 * np.pi * (yy / period + t / 30))).astype(int)
    return x[yy, np.clip(xx + dx, 0, w - 1)]

def light_leak(x, t, k=0.55, seed=4):
    """BCC Light Leaks, neutral: a soft white leak drifting across the frame (Screen blend). Use as a transition."""
    h, w = x.shape[:2]; r = np.random.default_rng(seed)
    cx = w * (-0.2 + 1.4 * ((t / 45) % 1)); cy = h * r.uniform(.3, .7)
    yy, xx = np.mgrid[0:h:4, 0:w:4].astype(np.float32)
    blob = np.exp(-(((xx - cx) / (0.35 * w)) ** 2 + ((yy - cy) / (0.6 * h)) ** 2))
    blob = big(blob, (h, w)) * k
    return screen(x, blob if x.ndim == 2 else blob[..., None])

def film_burn(x, p, seed=5):
    """Film burn transition, neutral: blown patches bloom from the edges and swallow the frame to white."""
    h, w = x.shape[:2]; r = np.random.default_rng(seed)
    n = qblur(r.standard_normal((h, w)).astype(np.float32), 120); n = (n - n.min()) / (n.max() - n.min() + 1e-6)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); edge = np.maximum(np.abs(xx / w - .5), np.abs(yy / h - .5)) * 2
    m = np.clip((0.55 * n + 0.45 * edge - (1 - p * 1.3)) / 0.15, 0, 1)
    return x * (1 - m) + m if x.ndim == 2 else x * (1 - m[..., None]) + m[..., None]

def vhs(x, t, seed=0):
    """VHS / CRT look (mono): scanlines, a rolling tracking band, line jitter. Retro; use only as a deliberate quote."""
    h, w = x.shape[:2]; r = np.random.default_rng(int(t) + seed); out = x.copy()
    out[::3] *= 0.78
    band = int((t * 23) % h); out[band:band + 18] = np.clip(out[band:band + 18] + r.uniform(.15, .35), 0, 1)
    for y in r.integers(0, h, 6): out[y:y + 4] = shift(out[y:y + 4], int(r.integers(-25, 25)))
    return blur(out, 1)

def halftone(x, cell=14, angle=45):
    """Halftone (Color Halftone / CC Ball Action-lite): dots sized by brightness. Matches the eyes' print texture."""
    h, w = x.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle); u = (xx * math.cos(a) + yy * math.sin(a)) / cell; v = (-xx * math.sin(a) + yy * math.cos(a)) / cell
    d = np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2)
    lum = blur(x if x.ndim == 2 else x.mean(axis=2), cell / 3)
    dot = np.clip((np.sqrt(np.clip(lum, 0, 1)) * 0.62 - d) * 6, 0, 1)
    return dot

def pixel_sort(x, thr=0.55, axis=1):
    """Pixel sorting (the popular GFX glitch): bright runs in each row get sorted into smears. Done at half size."""
    q = small(x, 2) if x.ndim == 2 else small(x.mean(axis=2), 2)
    out = q.copy()
    for i in range(q.shape[0]):
        row = q[i]; m = row > thr
        if not m.any(): continue
        idx = np.flatnonzero(np.diff(np.r_[0, m.astype(np.int8), 0]))
        for s, e in zip(idx[::2], idx[1::2]):
            if e - s > 3: out[i, s:e] = np.sort(row[s:e])
    return big(out, x.shape[:2])

def duotone(x, shadow=(0.02, 0.03, 0.06), high=(0.75, 0.86, 0.94)):
    """Tritone / Colorama-lite: map brightness onto night blue -> steel ice. The only tint MOTION allows (steel blue)."""
    g = x if x.ndim == 2 else x.mean(axis=2)
    s, hgh = np.array(shadow, np.float32), np.array(high, np.float32)
    return s + (hgh - s) * g[..., None]

def freeze_outline(x, k=1.0):
    """Freeze-frame outline pop (popular in edits): the frame darkens and its edges trace in white."""
    gy, gx = np.gradient(blur(x, 2)); e = np.clip(np.sqrt(gx ** 2 + gy ** 2) * 14, 0, 1)
    return np.clip(x * (1 - 0.65 * k) + e * k, 0, 1)

def posterize_time(t, fps_out=12, fps_in=30):
    """Posterize Time: hold frames to a lower frame rate (stop-motion choppiness on purpose). Returns the held time."""
    step = fps_in / fps_out; return math.floor(t / step) * step

def invert_hit(x, p):
    """Invert flash on a hit (hype-edit staple), decays back. Monochrome, so it stays on brand if used once."""
    k = max(0.0, 1 - p) ** 1.5
    return x * (1 - k) + (1 - x) * k

def mirror(x, mode="h"):
    """CC Kaleida / Mirror: symmetric frame. OFF-BRAND for MOTION except as a single deliberate shot."""
    if mode == "h":
        w = x.shape[1]; out = x.copy(); out[:, w // 2:] = x[:, :w - w // 2][:, ::-1]; return out
    h = x.shape[0]; out = x.copy(); out[h // 2:] = x[:h - h // 2][::-1]; return out
