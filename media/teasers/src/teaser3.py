"""MOTION teaser v3: directed cut of the iamariology b2b raymixes clips, scored to the b.mov track.

Track: 127.1 bpm, first beat 0.12 s, dip at 8.0-9.1 s, drop on beat 19 (9.09 s).
  ACT I    0.0-3.0   the MOTION sting (signature open)
  ACT II   3.0-8.0   build, letterboxed like a film: a cut every 2 beats, each shot pushes in slowly,
                     the frame opens a little wider on every cut; then one word per beat
                     (IAMARIOLOGY cut out of the footage / B2B / RAYMIXES cut out)
  DIP      8.0-9.1   RAYMIXES breaks up into slices, blackout, only the afterimage left
  ACT III  9.1-12.9  drop: the bars snap open to full frame, a punch-in on every beat, afterimage across cuts,
                     one logo stamp; a slow-motion hold for the last bar; name lower third
  ACT IV  12.9-16.7  the frame breaks up into black; the eyes open one band per half-beat; name; date;
                     the MMMM lockup; cut to black and let its afterimage fade
Black and white throughout. Red only in the MMMM letters and the B2B label.

usage: python3 teaser3.py <video_dir> <sting_frames_dir> <eyes.png> <out.mp4>
"""
import sys, os, subprocess, math
import numpy as np
from PIL import Image

VID, STING, EYES, OUT = sys.argv[1:5]
D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
BPM, PH = 127.1, 0.12
SPB = 60 / BPM * FPS                                       # frames per beat (14.16)
k = lambda b: int(round((PH * FPS) + b * SPB))            # beat -> frame
rng = np.random.default_rng(30)
ease = lambda t: 1 - (1 - min(max(t, 0), 1)) ** 3

def decode(name):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", f"{VID}/{name}"], capture_output=True, text=True).stdout.split(",")
    w, h = int(p[0]), int(p[1])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{VID}/{name}", "-r", "30", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)

SRC = {"a": decode("a.mov"), "b": decode("b.mov")}

def fit(g, z=1.0):
    """Cover-crop a grey frame to 1080x1920 with camera zoom z about the centre."""
    h, w = g.shape; s = max(W / w, H / h) * 1.04 * z
    cw, ch = W / s, H / s; x, y = (w - cw) / 2, (h - ch) / 2
    im = Image.fromarray(g).resize((W, H), Image.BICUBIC, box=(x, y, x + cw, y + ch))
    return np.asarray(im).astype(np.float32) / 255

def grade(x, hard):
    x = np.clip((x - (0.12 if hard else 0.06)) * (1.4 if hard else 1.3), 0, None) ** (1.3 if hard else 1.05)
    return (1 - np.exp(-2.4 * x)) / (1 - math.exp(-2.4 * 1.3))   # film shoulder: highlights roll off instead of clipping

def rgba(path):
    a = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255
    return a[..., :3], a[..., 3:4]

def box1d(a, r, axis):
    if r < 1: return a
    pad = [(0, 0)] * a.ndim; pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad), axis=axis)
    return (np.take(c, range(2 * r + 1, c.shape[axis]), axis=axis) - np.take(c, range(0, c.shape[axis] - 2 * r - 1), axis=axis)) / (2 * r + 1)

def soft(a, r, axis):
    for _ in range(3): a = box1d(a, max(1, r // 3), axis)
    return a

def astig(lum, kk):
    """Astigmatism streaks from the hottest points (1/4 size for speed), neutral white, capped."""
    if kk <= 0: return 0
    q = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)).astype(np.float32) / 255
    hot = np.clip((q - 0.72) / 0.28, 0, 1) ** 2
    st = soft(soft(hot, 60, 1), 1, 0) * 1.5 + soft(soft(hot, 26, 0), 1, 1) * 0.6 + soft(soft(hot, 5, 0), 5, 1) * 0.4
    st = np.asarray(Image.fromarray(np.clip(st * kk * 255, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    return np.minimum(st, 0.3)

def shift(img, dx, dy=0):
    dx, dy = int(round(dx)), int(round(dy)); out = np.zeros_like(img)
    if abs(dx) >= W or abs(dy) >= H: return out
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    out[yd, xd] = img[ys, xs]; return out

def zoom(img, z):
    if abs(z - 1) < 1e-3: return img
    w, h = W / z, H / z; x, y = (W - w) / 2, (H - h) / 2
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.resize((W, H), Image.BICUBIC, box=(x, y, x + w, y + h))).astype(np.float32) / 255

def breakup(img, amt, n=7, seed=0):
    """Cut the frame into horizontal slices that slide apart in alternating directions."""
    if amt <= 0.5: return img
    r = np.random.default_rng(seed)
    edges = np.sort(np.r_[0, r.choice(np.arange(80, H - 80), n - 1, replace=False), H])
    out = np.zeros_like(img)
    for i in range(n):
        a, b = edges[i], edges[i + 1]
        out[a:b] = shift(img, (1 if i % 2 else -1) * r.uniform(.5, 1) * amt)[a:b]
    return out

def letterbox(img, h):
    """Black bars top and bottom leaving a centred picture band h px tall (film frame)."""
    if h >= H: return img
    out = img.copy(); t = (H - int(h)) // 2
    out[:t] = 0; out[t + int(h):] = 0; return out

screen = lambda a, b: 1 - (1 - a) * (1 - b)

# ---- layers ----
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
LOGO = np.clip((STF(64) - 0.06) / 0.94, 0, 1)             # clean lockup frame from the sting, grain floor removed
WD = {n: rgba(f"{D}/W_{n}.png") for n in ("iamH", "rayH", "b2b", "endname", "enddate")}
NAME = rgba(f"{VID}/card_name.png")
_e = Image.open(EYES).convert("L"); _e = _e.resize((840, int(840 * _e.height / _e.width)), Image.LANCZOS)
EY = np.zeros((H, W), np.float32); EY[240:240 + _e.height, 120:960] = np.asarray(_e).astype(np.float32) / 255
EYE_BANDS = [(240 + 0, 240 + int(437 * 840 / 1080)), (240 + int(444 * 840 / 1080), 240 + int(913 * 840 / 1080)),
             (240 + int(922 * 840 / 1080), 240 + _e.height)]
gray3 = lambda g: np.repeat(g[..., None], 3, axis=2)

# ---- shot list: (start_frame, source, source_s, mode, speed) ----
SHOTS = [(k(6), "b", None, "build", 1), (k(8), "a", 1.0, "build", 1), (k(10), "b", None, "build", 1), (k(12), "a", 2.3, "build", 1),
         (k(14), "b", None, "word", 1), (k(15), "a", 3.4, "word", 1), (k(16), "b", None, "word", 1),
         (k(17), None, 0, "dip", 1),
         (k(19), "b", None, "drop", 1), (k(20), "a", 1.6, "drop", 1), (k(21), "b", None, "drop", 1), (k(22), "b", None, "drop", 1),
         (k(23), "a", 0.6, "drop", 1), (k(24), "b", None, "drop", 1), (k(25), "a", 2.6, "slow", 0.5),
         (k(27), "b", None, "break", 1),
         (k(28), None, 0, "eyes", 1)]
END_LOCK, END_CUT = k(33), k(34) + 6
N = min(END_CUT + 12, int(16.70 * FPS))
BOX = {k(6): 470, k(8): 560, k(10): 650, k(12): 760}        # letterbox height per build shot, opens every cut
WORDS = {k(14): "iamH", k(15): "b2b", k(16): "rayH"}

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{VID}/b.mov", "-map", "0:v", "-map", "1:a", "-t", f"{N / FPS:.3f}",
                        "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.05,afade=t=out:st={N / FPS - 0.9:.2f}:d=0.9",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

trail = np.zeros((H, W, 3), np.float32)
vign = (1 - 0.35 * (((np.arange(W)[None] - W / 2) / (W / 2)) ** 2 + ((np.arange(H)[:, None] - H / 2) / (H / 2)) ** 2) / 2)[..., None].astype(np.float32)
last_foot = np.zeros((H, W, 3), np.float32)

def footage(src, ss, n, speed, z, f0):
    if ss is None: ss = f0 / FPS                      # in sync with the soundtrack
    arr = SRC[src]; return fit(arr[min(len(arr) - 1, int(ss * FPS + n * speed))], z)

for f in range(N):
    grain_amt = 0.035
    if f < k(6):                                                          # ACT I: the sting
        out = STF(min(89, f)); grain_amt = 0
        trail[:] = 0
    else:
        si = max(i for i, s in enumerate(SHOTS) if s[0] <= f)
        f0, src, ss, mode, speed = SHOTS[si]; n = f - f0
        nxt = SHOTS[si + 1][0] if si + 1 < len(SHOTS) else N; L = nxt - f0
        if mode in ("build", "word", "drop", "slow", "break"):
            hard = mode != "build"
            punch = {"build": .05, "word": .03, "drop": .11, "slow": .06, "break": .04}[mode] * math.exp(-n / 3)
            push = (0.08 if mode in ("build", "slow") else 0.04) * n / max(L, 1)
            g = grade(footage(src, ss, n, speed, 1.0 + push + punch, f0), hard)
            fl = {"build": .25, "word": .3, "drop": .5 if n < 5 else .3, "slow": .45, "break": .3}[mode]
            frame = gray3(np.clip(g + astig(g, fl), 0, 1))
            last_foot = frame
            decay = {"build": .6, "word": .6, "drop": .55, "slow": .84, "break": .6}[mode]
            trail = np.maximum(trail * decay, shift(frame, 5) * 0.85)
            tw = {"build": .42, "word": .42, "drop": .3, "slow": .45, "break": .3}[mode] * (1 if n < 8 or mode == "slow" else .65)
            out = np.maximum(frame, trail * tw)
            if mode == "build":
                prev = max([b for b in BOX if b <= f0]); h0 = BOX[prev]
                out = letterbox(out, h0)
            if mode == "word":
                c, a = WD[WORDS[f0]]; m = n
                off = 26 * (1 - ease(m / 5))
                if off > .5: a = np.maximum(shift(a, -off), shift(a, off)) * 0.85
                if WORDS[f0] == "b2b":                                     # red label on black, footage gone
                    out = trail * 0.18 + c * a
                else:                                                      # word cut out of the footage
                    lit = np.clip(frame * 1.25 + 0.22, 0, 1)
                    out = lit * a + trail * 0.12 * (1 - a)
                out = letterbox(out, 760)
            if mode == "drop" and f0 == k(19):                             # release: bars snap open
                out = letterbox(out, 760 + (H - 760) * ease(n / 4))
                if n < 2: out = breakup(out, 120 * (1 - n / 2), seed=19)
                if n < 5:                                                  # the one logo stamp
                    off = 16 * (1 - n / 5)
                    lg = np.maximum(shift(LOGO, -off), shift(LOGO, off)) if n < 2 else LOGO
                    out = screen(out * (0.4 if n < 2 else 0.65), lg * (1 - n * 0.18))
            if mode in ("drop", "slow") and k(23) + 2 <= f < k(27):        # name lower third
                c, a = NAME; m = f - (k(23) + 2)
                band = np.clip((np.arange(H) - 1200) / 220, 0, 1)[:, None, None]
                out = out * (1 - 0.55 * band * min(1, m / 4))
                a = a * min(1, m / 4); out = out * (1 - a) + c * a
            if mode == "break":                                            # last bar: the picture breaks up into black
                p = n / max(L, 1)
                out = breakup(out, 380 * p ** 1.3, seed=27) * (1 - p) ** 0.6
            out = out * vign
        elif mode == "dip":                                                # RAYMIXES breaks up, then blackout
            p = n / SPB
            if p < 1:
                c, a = WD["rayH"]; lit = np.clip(last_foot * 1.25 + 0.22, 0, 1)
                word = letterbox(lit * a, 760)
                out = breakup(np.maximum(word, trail * 0.12), 300 * p ** 1.3, seed=17) * (1 - p) ** 0.8
                trail = np.maximum(trail * 0.7, out * 0.8)
            else:
                trail = trail * 0.72; out = trail * 0.6
                if f >= k(19) - 3: out = screen(out, LOGO * 0.18 * (1 if f % 2 else 0))   # two ghost ticks before the drop
        else:                                                              # ACT IV: eyes, name, date, lockup
            canvas = np.zeros((H, W), np.float32)
            for i, (a0, a1) in enumerate(EYE_BANDS):                       # one eye band per half-beat
                fb = f0 + int(round(i * SPB / 2))
                if f < fb: continue
                m = f - fb; off = 30 * (1 - ease(m / 6))
                band = np.zeros_like(canvas); band[a0:a1] = EY[a0:a1]
                if off > .5: band = np.maximum(shift(band, -off), shift(band, off)) * 0.8
                canvas = np.maximum(canvas, band * min(1, 0.35 + m / 4))
            out = gray3(canvas)
            out = zoom(out, 1.0 + 0.035 * (f - f0) / (END_LOCK - f0))      # slow push on the eyes
            for key, fb in (("endname", f0 + int(round(2 * SPB))), ("enddate", f0 + int(round(3 * SPB)))):
                if f >= fb:
                    c, a = WD[key]; a = a * min(1, (f - fb) / 5); out = out * (1 - a) + c * a
            if f < END_LOCK:
                trail = np.maximum(trail * 0.6, out * 0.7)
                if f < f0 + 8: out = np.maximum(out, trail * 0.3)
            else:                                              # hard cut to the lockup, then its afterimage
                if f < END_CUT:
                    m = f - END_LOCK
                    out = zoom(LOGO, 1.0 + 0.02 * m / (END_CUT - END_LOCK)) * min(1, 0.4 + m / 3)
                    trail = out.copy()
                else:
                    trail = trail * 0.72; out = shift(trail, 4 * (f - END_CUT)) * 0.7
                grain_amt = 0.02
    grain = rng.standard_normal((H, W, 1)).astype(np.float32) * grain_amt
    out = np.clip(out + grain, 0, 1)
    enc.stdin.write((out * 255).astype(np.uint8).tobytes())
    if f % 60 == 0: print("frame", f, "/", N, flush=True)
enc.stdin.close(); enc.wait()
print("done", N, "frames", round(N / FPS, 2), "s; lock", END_LOCK, "cut", END_CUT)
