"""MOTION teaser v2: 'raw cuts visualizer' cut of the iamariology b2b raymixes clips.

Everything is cut to the b.mov track (127.1 bpm, first beat 0.12 s, drop at beat 19 = 9.09 s).
  0.0  MOTION sting (the logo 'touchdown')
  3.0  build: a cut every 2 beats, footage black and white, each shot ghosts into the next (afterimage)
  6.7  one word per beat: IAMARIOLOGY / B2B / RAYMIXES, then the logo strobes on half-beats
  9.1  drop: a cut every beat, light beams flare (astigmatism), logo stamp on every downbeat
 13.3  end card (eyes + name + date), then the sting exit to black
Red only in the MMMM letters and the B2B label. Footage never tinted.

usage: python3 teaser2.py <video_dir> <sting_frames_dir> <out.mp4>
"""
import sys, os, subprocess, math
import numpy as np
from PIL import Image

VID, STING, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
BPM, PH = 127.1, 0.12
beat = lambda k: int(round((PH + k * 60 / BPM) * FPS))   # beat k -> frame index
rng = np.random.default_rng(30)

def decode(name):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", f"{VID}/{name}"], capture_output=True, text=True).stdout.split(",")
    w, h = int(p[0]), int(p[1])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{VID}/{name}", "-r", "30", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w)

SRC = {"a": decode("a.mov"), "b": decode("b.mov")}

def fit(g):
    """Cover-crop a grey frame to 1080x1920, slight push-in so upscales look intentional."""
    h, w = g.shape; s = max(W / w, H / h) * 1.04
    im = Image.fromarray(g).resize((int(w * s + .5), int(h * s + .5)), Image.BICUBIC)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return np.asarray(im.crop((x, y, x + W, y + H))).astype(np.float32) / 255

def grade(x, hard):
    x = np.clip((x - 0.06) * (1.4 if hard else 1.3), 0, 1)
    return x ** (1.15 if hard else 1.05)

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

def astig(lum, k):
    """Astigmatism streaks from the hottest points, computed at 1/4 size for speed, neutral white."""
    if k <= 0: return 0
    q = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)).astype(np.float32) / 255
    hot = np.clip((q - 0.70) / 0.30, 0, 1) ** 2
    st = soft(soft(hot, 60, 1), 1, 0) * 1.6 + soft(soft(hot, 26, 0), 1, 1) * 0.7 + soft(soft(hot, 5, 0), 5, 1) * 0.5
    st = np.asarray(Image.fromarray(np.clip(st * k * 255, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    return np.minimum(st, 0.35)

def shift(img, dx, dy=0):
    dx, dy = int(round(dx)), int(round(dy)); out = np.zeros_like(img)
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    out[yd, xd] = img[ys, xs]; return out

BAND = np.zeros((H, 1, 1), np.float32); BAND[1250:1760] = 1
BAND = box1d(BAND, 80, 0)
screen = lambda a, b: 1 - (1 - a) * (1 - b)

# ---- layers ----
LOGO = np.asarray(Image.open(f"{STING}/f060.png").convert("RGB")).astype(np.float32) / 255
LOGO = np.clip((LOGO - 0.06) / 0.94, 0, 1)                     # lift the sting's grain floor to true black
WORDS = {k: rgba(f"{D}/W_{k}.png") for k in ("iam", "b2b", "ray", "presents", "opening")}
NAME = rgba(f"{VID}/card_name.png")
END = np.asarray(Image.open(f"{VID}/card_end.png").convert("RGB")).astype(np.float32) / 255
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255

# ---- edit decision list: (start_frame, source, source_seconds, mode) ----
k = beat
EDL = [(0, "sting", 0, "sting"),
       (k(6), "b", 0.3, "build"), (k(8), "a", 1.0, "build"), (k(10), "b", 3.4, "build"), (k(12), "a", 2.3, "build"),
       (k(14), "b", 5.0, "word"), (k(15), "a", 3.4, "word"), (k(16), "b", 6.1, "word"),
       (k(17), "a", 7.2, "strobe"),
       (k(19), "b", 9.1, "drop"), (k(20), "a", 1.6, "drop"), (k(21), "b", 10.6, "drop"), (k(22), "b", 12.0, "drop"),
       (k(23), "a", 3.0, "drop"), (k(24), "b", 13.4, "drop"), (k(25), "a", 7.7, "drop"), (k(26), "b", 14.6, "drop"),
       (k(27), "b", 15.6, "drop"),
       (k(28), "end", 0, "end"), (k(28) + 70, "sting", 60, "outro")]
N = EDL[-1][0] + 30
WORD_AT = {k(14): "iam", k(15): "b2b", k(16): "ray"}
DOWNBEATS = {k(19), k(23), k(27)}

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-ss", "0", "-i", f"{VID}/b.mov", "-map", "0:v", "-map", "1:a", "-t", f"{N / FPS:.3f}",
                        "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.05,afade=t=out:st={N / FPS - 0.7:.2f}:d=0.7",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

trail = np.zeros((H, W, 3), np.float32)
vign = (1 - 0.35 * (((np.arange(W)[None] - W / 2) / (W / 2)) ** 2 + ((np.arange(H)[:, None] - H / 2) / (H / 2)) ** 2) / 2)[..., None].astype(np.float32)
for f in range(N):
    seg = max(i for i, e in enumerate(EDL) if e[0] <= f)
    f0, src, ss, mode = EDL[seg]; n = f - f0
    if mode in ("sting", "outro"):
        out = STF(min(89, ss + n)); trail[:] = 0
    elif mode == "end":
        p = min(1, n / 10)                                      # end card arrives seeing double, then focuses
        off = 30 * (1 - p) ** 2
        out = END if off < .5 else np.maximum(shift(END, -off), shift(END, off)) * 0.85
        out = np.maximum(out * min(1, 0.25 + n / 6), trail * 0.6)
        trail = np.maximum(trail * 0.7, out * 0.8)
    else:
        arr = SRC[src]; g = fit(arr[min(len(arr) - 1, int(ss * FPS) + n)])
        hard = mode in ("drop", "strobe")
        g = grade(g, hard)
        if n == 0: g = np.clip(g * (1.25 if hard else 1.15), 0, 1)          # exposure pop on the cut, no grey frames
        flare = {"build": 0.35, "word": 0.4, "strobe": 0.6, "drop": 0.6 if n < 6 else 0.35}[mode]
        lum = np.clip(g + astig(g, flare), 0, 1)
        frame = np.repeat(lum[..., None], 3, axis=2)
        # afterimage: last shot keeps burning through the new one, drifting right
        decay = 0.72 if hard else 0.6
        trail = np.maximum(trail * decay, shift(frame, 5) * 0.85)
        out = np.maximum(frame, trail * (0.45 if n < 8 else 0.3))
        if mode == "build" and seg == 1 and n < 26:                       # MOTION PRESENTS on the first shot
            c, a = WORDS["presents"]; a = a * min(1, n / 4) * (1 if n < 20 else (26 - n) / 6)
            out = out * (1 - a) + c * a
        wk = max((fr for fr in WORD_AT if fr <= f), default=None)
        if mode == "word" and wk is not None and f - wk < k(15) - k(14):
            c, a = WORDS[WORD_AT[wk]]; m = f - wk
            off = 22 * (1 - min(1, m / 4)) ** 2
            if off > .5: c, a = np.maximum(shift(c, -off), shift(c, off)), np.maximum(shift(a, -off), shift(a, off)) * 0.8
            out = out * 0.55                                               # dip the footage under the word
            out = out * (1 - a) + c * a
        if mode == "strobe":                                               # logo on every half-beat, footage blinks
            hb = int((f - f0) / (60 / BPM / 2 * FPS))
            ph = (f - f0) - hb * (60 / BPM / 2 * FPS)
            if ph < 3:
                out = screen(out * 0.25, LOGO * (1 - ph / 3 * 0.5))
            else:
                out = out * (0.5 if hb % 2 else 0.8)
        if mode == "drop":
            fd = max(fr for fr in DOWNBEATS if fr <= f) if any(fr <= f for fr in DOWNBEATS) else None
            if fd is not None and f - fd < 4:                              # logo stamp on each downbeat
                m = f - fd; off = 14 * (1 - m / 4)
                lg = np.maximum(shift(LOGO, -off), shift(LOGO, off)) if m < 2 else LOGO
                out = screen(out * (0.35 if m < 2 else 0.6), lg * (1 - m * 0.2))
            if k(23) + 2 <= f < k(27):                                     # name lower third through the drop
                c, a = NAME; m = f - (k(23) + 2)
                a = a * min(1, m / 3)
                out = out * (1 - 0.45 * min(1, m / 3) * BAND)
                out = out * (1 - a * 0.9) + c * a * 0.9
            if k(27) <= f < k(28):
                c, a = WORDS["opening"]; out = out * (1 - a) + c * a
        out = out * vign
    grain = rng.standard_normal((H, W, 1)).astype(np.float32) * (0.035 if mode not in ("sting", "outro") else 0)
    out = np.clip(out + grain, 0, 1)
    enc.stdin.write((out * 255).astype(np.uint8).tobytes())
    if f % 60 == 0: print("frame", f, "/", N, mode, flush=True)
enc.stdin.close(); enc.wait()
print("done", N, "frames", N / FPS, "s")
