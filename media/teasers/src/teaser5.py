"""MOTION teaser v5: the pop-culture cut (Lucki / Carti / Yeat / Kettama / Boiler Room / Kanye references).

Same track and beat grid as v4 (127.1 bpm, drop on beat 19). What changed, by reference:
  Lucki / Carti   fisheye punch-in on every cut, bulge pulse on every kick, stabilized handheld
  Yeat            repeated type stacks that scroll (outlined copies, one solid), glitch blocks, pixel sort
  Kettama / BR    camcorder HUD: corner brackets, REC dot on the beat, running timecode, raw energy
  Raw Cuts        the logo opens and closes, flashes in before the drop
  Kanye sets      the ending: black, one line of type, monumental negative space, slow push
Warps are now on brand (Jovanni's call). Red stays an accent (MMMM, B2B, REC dot); footage is never tinted.

usage: python3 teaser5.py <video_dir> <sting_frames_dir> <eyes.png> <out.mp4>
"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fx"))
import mfx
from mfx import W, H, FPS

VID, STING, EYES, OUT = sys.argv[1:5]
D = os.path.dirname(os.path.abspath(__file__))
SPB = 60 / 127.1 * FPS
kf = lambda b: 3.6 + SPB * b
rng = np.random.default_rng(31)

A = mfx.plate(mfx.stabilize(f"{VID}/a.mov"), deflicker=True)
B = mfx.plate(f"{VID}/b.mov")
SLOW = mfx.plate(mfx.stabilize(f"{VID}/a.mov"), 2.55, 3.45, fps=90, interp=True, deflicker=True)
PL = {"a": A, "b": B}

def mask(p): return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)[..., 3] / 255
def rgba(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255; return a[..., :3], a[..., 3]
IAM, RAY = mask(f"{D}/P_iam.png"), mask(f"{D}/P_ray.png")
B2B = rgba(f"{D}/P_b2b.png"); SLAM = rgba(f"{D}/P_slam.png"); DEVIL = rgba(f"{D}/P_devil.png"); HUD = rgba(f"{D}/P_hud.png")
STK_IAM, STK_RAY = mfx.stack(IAM, 9, .55), mfx.stack(RAY, 7, .45)
DG = np.asarray(Image.open(f"{D}/P_digits.png").convert("RGBA")).astype(np.float32)[..., 3] / 255
ADV = 15.6
def timecode(f):
    """Running camcorder timecode, bottom right, from digit sprites."""
    s = int(f // FPS); fr = int(f % FPS)
    txt = f"00:00:{s:02d}:{fr:02d}"
    out = np.zeros((H, W), np.float32); x0 = W - 78 - int(len(txt) * ADV); y0 = H - 150 - 30
    for i, ch in enumerate(txt):
        j = "0123456789:".index(ch); sx = int(round(j * ADV))
        out[y0:y0 + 40, x0 + int(i * ADV):x0 + int(i * ADV) + int(ADV) + 1] = DG[0:40, sx:sx + int(ADV) + 1]
    return out
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
_e = Image.open(EYES).convert("L"); _e = _e.resize((840, int(840 * _e.height / _e.width)), Image.LANCZOS)
EY = np.zeros((H, W), np.float32); EY[240:240 + _e.height, 120:960] = np.asarray(_e).astype(np.float32) / 255
sc = 840 / 1080
EYE_BANDS = [(240, 240 + int(437 * sc)), (240 + int(444 * sc), 240 + int(913 * sc)), (240 + int(922 * sc), 240 + _e.height)]

# (beat, source, seconds or None = in sync with track, zoom start->end, extra fx)
CUTS = [(6, "b", None, (1.10, 1.02), ""), (8, "a", 0.95, (1.08, 1.0), ""), (10, "b", None, (1.0, 1.08), ""),
        (12, "a", 2.05, (1.06, 1.0), ""), (13, "b", None, (1.08, 1.0), ""),
        (14, "word:iam", None, None, ""), (15, "word:b2b", None, None, ""), (16, "word:ray", None, None, ""),
        (17, "stutter", None, None, ""), (18, "glitchout", None, None, ""),
        (19, "b", None, (1.12, 1.0), "drop"), (20, "a", 1.55, (1.06, 1.0), ""), (21, "b", None, (1.0, 1.06), "sort"),
        (22, "a", 0.6, (1.06, 1.0), "twitch"), (23, "b", None, (1.0, 1.06), "melt"), (24, "b", None, (1.06, 1.0), "blocks"),
        (25, "slow", None, (1.04, 1.1), ""), (27, "end", None, None, "")]
KICKS = [kf(b) for b in range(6, 27)]
N = int(16.70 * FPS)
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)

EXPO = {}
def raw(c, f, ti):
    b0, src, ss, cam, fx = c
    if src == "slow":
        sp = [3.0 if i < 4 else 3 - 2 * mfx.ease_io((i - 4) / 6) for i in range(int(ti) + 2)]
        return mfx.cover(SLOW[int(min(len(SLOW) - 1, sum(sp[:int(ti)])))], cam[0] + (cam[1] - cam[0]) * ti / (2 * SPB))
    arr = PL[src]; sec = f / FPS if ss is None else ss + ti / FPS
    nb = next((x[0] for x in CUTS if x[0] > b0), 35); L = kf(nb) - kf(b0)
    z = cam[0] + (cam[1] - cam[0]) * mfx.ease_out(ti / max(L, 1), 2)
    sx = sy = rot = 0.0
    for h in KICKS:
        if h <= f < h + 10 and b0 >= 19:
            dx, dy, r = mfx.shake(f, h, amp=22 if b0 == 19 and abs(h - kf(19)) < 1 else 8, seed=int(h)); sx += dx; sy += dy; rot += r
    return mfx.cover(arr[int(min(len(arr) - 1, sec * FPS))], z, sx, sy, rot)

def expo(c, f):
    if c[0] not in EXPO:
        nb = next((x[0] for x in CUTS if x[0] > c[0]), 35); L = kf(nb) - kf(c[0])
        ms = [float(np.percentile(raw(c, f + j, j), 60)) for j in np.linspace(0, max(L - 1, 0), 5)]
        EXPO[c[0]] = float(np.clip(0.33 / max(np.median(ms), .02), .6, 2.0))
    return EXPO[c[0]]

def kick_env(f, decay=4.0):
    """0..1 envelope that hits on every kick and decays."""
    last = max([h for h in KICKS if h <= f], default=None)
    return 0.0 if last is None else math.exp(-(f - last) / decay)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{VID}/b.mov", "-map", "0:v", "-map", "1:a", "-t", f"{N / FPS:.3f}",
                        "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.05,afade=t=out:st={N / FPS - 0.6:.2f}:d=0.6",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", "14M", "-bufsize", "28M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
echo = mfx.Echo((H, W)); prev = np.zeros((H, W), np.float32)
g3 = lambda g: np.repeat(g[..., None], 3, 2)
END_TYPE, END_MARK, END_EXIT = kf(29), kf(31), kf(33.4)

for f in range(N):
    grain_amt = 0.05
    if f < kf(6) - .01:
        rgb = STF(min(87, f)); grain_amt = 0
        if f >= kf(6) - 3: rgb = mfx.zoom_blur(rgb, .3)
    else:
        ci = max(i for i, c in enumerate(CUTS) if kf(c[0]) <= f + .01); c = CUTS[ci]; b0, src = c[0], c[1]; ti = f - kf(b0)
        nxt = CUTS[ci + 1][0] if ci + 1 < len(CUTS) else 35
        if src in ("a", "b", "slow"):
            g = look(mfx.mblur(lambda tt: raw(c, tt, ti - (f - tt)), f, .5, 3) if ti < 5 or b0 >= 19 else raw(c, f, ti), expo(c, f))
            # Lucki/Carti lens: fisheye punch on the cut, bulge on every kick
            k = (0.85 if b0 == 19 else 0.55) * math.exp(-ti / 4) + 0.18
            g = mfx.fisheye(g, k)
            g = mfx.bulge(g, (0.32 if b0 >= 19 else 0.2) * kick_env(f), .55)
            if b0 >= 19 and src != "slow": g = mfx.astig(g, .25 * kick_env(f, 6))
            if ci == 0 and ti < 6: g = mfx.zoom_blur(g, .3 * (1 - mfx.ease_out(ti / 6)))
            if c[4] == "sort" and ti < 5: g = mfx.pixel_sort(g, .5) * (1 - ti / 8) + g * (ti / 8)
            if c[4] == "twitch": g = mfx.twitch(g, f, amount=1.3)
            if c[4] == "blocks" and ti < 4: g = mfx.block_glitch(g, prev, .3, seed=int(f))
            if nxt == 23 and kf(23) - f < 5:                                  # melt across the bar line
                g = mfx.liquid(g, 130 * (1 - (kf(23) - f) / 5), f)
            if c[4] == "melt" and ti < 6: g = mfx.liquid(g, 130 * (1 - ti / 6), f)
            if src == "slow": g = mfx.liquid(g, 18, f * .3)
            if b0 == 25 and kf(27) - f < 6:                                   # twirl out into the ending
                q = 1 - (kf(27) - f) / 6; g = mfx.twirl(g, 2.6 * q ** 2, .7) * (1 - q ** 2)
            g = echo(g, .85 if src == "slow" else .55, .5 if src == "slow" else (.32 if ti < 7 else .18))
            prev = g
            g = mfx.vignette(mfx.promist(g, .28), .3)
            rgb = g3(g)
            if b0 >= 23 and src != "slow" or src == "slow":                    # the name slams in on the bar line, blinks on the beat
                if f >= kf(23):
                    on = (int((f - kf(23)) / (SPB / 2)) % 2 == 0) if f < kf(25) else True
                    cc, aa = SLAM; aa = (aa * (1 if on else .0))[..., None]
                    band = np.clip(1 - np.abs(np.arange(H) - 960) / 520, 0, 1)[:, None, None] * .55
                    if on: rgb = rgb * (1 - band)
                    rgb = rgb * (1 - aa) + cc * aa
            # camcorder HUD (Kettama / Boiler Room raw)
            hc, ha = HUD; tc = timecode(f)
            blink = 1.0 if (f - kf(6)) % SPB < SPB / 2 else 0.0
            ha2 = ha.copy()
            ha2[140:190, 70:110] *= blink                                      # REC dot blinks on the beat
            rgb = rgb * (1 - ha2[..., None] * .9) + hc * ha2[..., None] * .9
            rgb = rgb * (1 - tc[..., None] * .9) + .92 * tc[..., None]
        elif src.startswith("word:"):
            name = src[5:]; m = ti
            bg = look(raw(CUTS[4] if name != "iam" else CUTS[2], f, m), 1.0) * .28
            if name == "b2b":
                cc, aa = B2B; s = 1 + .25 * (1 - mfx.expo_out(m / 6))
                aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / s, 0, W / 2 * (1 - 1 / s), 0, 1 / s, H / 2 * (1 - 1 / s)), resample=Image.BILINEAR))
                g = mfx.invert_hit(bg, m / 5) if m < 5 else bg
                rgb = g3(g) * (1 - aa[..., None]) + cc * aa[..., None]
            else:
                stk = STK_IAM if name == "iam" else STK_RAY
                scroll = (-1 if name == "iam" else 1) * (m * 9)                # stack scrolls through the frame
                st = mfx.shift(stk, 0, scroll)
                st = mfx.liquid(st, 50 * (1 - mfx.ease_out(m / 6)), f) if m < 6 else st
                g = np.maximum(bg, st)
                g = mfx.bulge(g, .25 * kick_env(f), .6)
                rgb = g3(g)
            echo.buf *= .5
        elif src == "stutter":
            half = int(ti // (SPB / 2)); q = ti - half * SPB / 2
            cc = CUTS[1] if half % 2 == 0 else CUTS[4]
            g = look(raw(cc, f, 3 + q), expo(cc, f))
            g = mfx.fisheye(g, .6 * math.exp(-q / 3) + .2)
            if q < 3: g = mfx.invert_hit(g, q / 3)
            g = mfx.twitch(g, f, amount=1.0); prev = g
            rgb = g3(mfx.vignette(g, .3))
        elif src == "glitchout":                                               # the black beat: last image datamoshes away
            p = ti / SPB
            g = mfx.block_glitch(prev * (1 - p) ** 1.5, np.zeros_like(prev), .25 + .6 * p, seed=int(f))
            if kf(19) - f < 4 and int(f) % 2:
                g = np.maximum(g, np.clip((STF(66).mean(axis=2) - .05) / .95, 0, 1) * .2)
                rgb = np.maximum(g3(g), np.clip((STF(66) - .05) / .95, 0, 1) * .25)
            else: rgb = g3(g)
            prev = g
        else:                                                                  # ending: eyes -> Kanye-style type -> the mark
            if f < END_TYPE:
                canvas = np.zeros((H, W), np.float32)
                for i, (a0, a1) in enumerate(EYE_BANDS):
                    fb = kf(27.25) + i * SPB / 2
                    if f < fb: continue
                    mm = f - fb; off = 34 * (1 - mfx.ease_out(mm / 6))
                    band = np.zeros_like(canvas); band[a0:a1] = EY[a0:a1]
                    if off > .5: band = np.maximum(mfx.shift(band, -off), mfx.shift(band, off)) * .8
                    canvas = np.maximum(canvas, band * min(1, .35 + mm / 4))
                canvas = mfx.bulge(canvas, .18 * kick_env(f, 5), .5)
                rgb = g3(mfx.promist(canvas, .3)); grain_amt = .04
            elif f < END_MARK:                                                 # monumental: black, one line, slow push
                z = 1 + .04 * (f - END_TYPE) / (END_MARK - END_TYPE)
                cc, aa = DEVIL
                aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR))
                aa = aa * min(1, (f - END_TYPE) / 4)
                rgb = cc * aa[..., None]; grain_amt = .03
            elif f < END_EXIT:
                rgb = STF(int(min(70, 40 + (f - END_MARK)))); grain_amt = .02
            else:
                rgb = STF(int(min(89, 74 + (f - END_EXIT)))); grain_amt = .02
    if grain_amt: rgb = mfx.grain(rgb, grain_amt, rng=rng)
    enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes())
    if f % 60 == 0: print("frame", f, "/", N, flush=True)
enc.stdin.close(); enc.wait()
print("done", N)
