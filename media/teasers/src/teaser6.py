"""MOTION teaser v6: "the combo" (Drake + Carti + Bad Bunny/reggaeton + Yeat + Boiler Room + Kanye), cut to the
sparkler clip's own track (96.5 bpm reggaeton; 2 beats of silence before the drop at 19.22 s in the clip).

Teaser t = clip t - 7.5 s.  Beat n at clip 10.52 + 0.6218 n  ->  teaser frame 90.6 + 18.65 n.  Drop = beat 14.
Dembow accents (the "chick" of boom-ch-boom-chick) at n+0.75 and n+1.5 of each beat pair drive the small pops.
  0-3.0 s   the MOTION sting
  b0-4      DRAKE: letterboxed, moody, slow-motion sparklers, one small line of type, slow push. No HUD yet.
  b4-8      CARTI / BAD BUNNY: the frame opens, fisheye punch-ins on each beat, camcorder HUD switches on
  b8-10     YEAT: IAMARIOLOGY stack / B2B / RAYMIXES stack, on the beat and the half
  b10-11.7  stutter on half-beats with invert hits on the dembow accents
  b11.7-14  the track's own silence: black, the HUD alone, a datamosh decay, one logo flash before the drop
  b14-20    drop: fisheye + shake, bulge on every kick, small pops on the dembow accents, melt into the name
  b20-22    hero: the closest sparkler in optical-flow slow motion, heavy afterimage, liquid shimmer
  b22-28    KANYE ending: eyes, then black with one line, then the mark
Monochrome; red only in MMMM, B2B and the REC dot.

usage: python3 teaser6.py <video_dir> <sting_frames_dir> <eyes.png> <out.mp4>
"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fx"))
import mfx
from mfx import W, H, FPS

VID, STING, EYES, OUT = sys.argv[1:5]
D = os.path.dirname(os.path.abspath(__file__))
C0 = 7.5                                        # clip time at teaser t = 0
SPB = 0.62176 * FPS
kf = lambda n: (10.52 - C0) * FPS + SPB * n
rng = np.random.default_rng(32)

C = mfx.plate(f"{VID}/c.mov", C0, C0 + 22)        # in-sync plate: index = teaser frame
A = mfx.plate(mfx.stabilize(f"{VID}/a.mov"), deflicker=True)
B = mfx.plate(f"{VID}/b.mov")
SLOW_IN = mfx.plate(f"{VID}/c.mov", 12.5, 13.9, fps=75, interp=True)     # 2.5x frames for the Drake open
SLOW_HERO = mfx.plate(f"{VID}/c.mov", 28.4, 29.6, fps=90, interp=True)  # 3x frames for the hero

def mask(p): return np.asarray(Image.open(p).convert("RGBA")).astype(np.float32)[..., 3] / 255
def rgba(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255; return a[..., :3], a[..., 3]
IAM, RAY = mask(f"{D}/P_iam.png"), mask(f"{D}/P_ray.png")
B2B, SLAM, DEVIL, HUD, KICK = (rgba(f"{D}/P_{n}.png") for n in ("b2b", "slam", "devil", "hud96", "kicker"))
STK_IAM, STK_RAY = mfx.stack(IAM, 9, .55), mfx.stack(RAY, 7, .45)
DG = mask(f"{D}/P_digits.png"); ADV = 15.6
def timecode(f):
    s = int(f // FPS); fr = int(f % FPS); txt = f"00:00:{s:02d}:{fr:02d}"
    out = np.zeros((H, W), np.float32); x0 = W - 78 - int(len(txt) * ADV); y0 = H - 180
    for i, ch in enumerate(txt):
        sx = int(round("0123456789:".index(ch) * ADV)); xx = x0 + int(i * ADV)
        out[y0:y0 + 40, xx:xx + int(ADV) + 1] = DG[0:40, sx:sx + int(ADV) + 1]
    return out
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
LOGO = np.clip((STF(66) - .05) / .95, 0, 1)
_e = Image.open(EYES).convert("L"); _e = _e.resize((840, int(840 * _e.height / _e.width)), Image.LANCZOS)
EY = np.zeros((H, W), np.float32); EY[240:240 + _e.height, 120:960] = np.asarray(_e).astype(np.float32) / 255
sc = 840 / 1080
EYE_BANDS = [(240, 240 + int(437 * sc)), (240 + int(444 * sc), 240 + int(913 * sc)), (240 + int(922 * sc), 240 + _e.height)]

# framings of the one-camera clip (a director's punch-ins): zoom, centre x, centre y (fractions of the plate)
WIDE, SPARK, HANDS, CROWD = (1.04, .5, .5), (1.6, .5, .43), (1.9, .52, .56), (1.35, .5, .45)
# (beat, source, seconds (None = in sync with the track), framing, zoom drift, fx)
CUTS = [(0, "slow_in", None, SPARK, .10, "drake"),
        (4, "a", 0.95, (1.0, .5, .5), -.06, ""), (5, "c", None, HANDS, -.05, ""), (6, "b", 9.3, (1.0, .5, .5), .06, ""),
        (7, "c", None, WIDE, .05, ""),
        (8, "word:iam", None, None, 0, ""), (9, "word:b2b", None, None, 0, ""), (9.5, "word:ray", None, None, 0, ""),
        (10, "stutter", None, None, 0, ""), (11.7, "silence", None, None, 0, ""),
        (14, "c", None, WIDE, -.04, "drop"), (15, "c", None, SPARK, -.06, ""), (16, "a", 1.0, (1.0, .5, .5), -.05, ""),
        (17, "c", None, HANDS, -.06, "sort"), (18, "b", 10.6, (1.0, .5, .5), .05, "melt"), (19, "c", None, CROWD, .05, "blocks"),
        (20, "slow_hero", None, (1.15, .5, .5), .08, "hero"), (22, "end", None, None, 0, "")]
KICKS = [kf(n) for n in range(4, 22) if not (11.7 <= n < 14)]
SNARES = [kf(n + o) for n in range(4, 22, 2) for o in (.75, 1.5) if not (11.7 <= n + o < 14)]
N = int(round(kf(28.6)))
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
nxt_of = lambda b0: next((x[0] for x in CUTS if x[0] > b0), 30)

def env(f, hits, decay):
    last = max([h for h in hits if h <= f], default=None)
    return 0.0 if last is None else math.exp(-(f - last) / decay)

def raw(c, f, ti):
    b0, src, ss, fr, drift, fx = c
    L = kf(nxt_of(b0)) - kf(b0); q = mfx.ease_out(ti / max(L, 1), 2)
    z, cx, cy = fr[0] * (1 + drift * q), fr[1], fr[2]
    sx = sy = rot = 0.0
    if b0 >= 14:
        for h in KICKS:
            if h <= f < h + 10:
                dx, dy, r = mfx.shake(f, h, amp=24 if abs(h - kf(14)) < 1 else 8, seed=int(h)); sx += dx; sy += dy; rot += r
    if src == "slow_in": arr, i = SLOW_IN, int(ti * 2.5 * 0.5)            # 0.5x speed from 2.5x frames... held moody
    elif src == "slow_hero":
        sp = [3.0 if k < 4 else 3 - 2.2 * mfx.ease_io((k - 4) / 8) for k in range(int(ti) + 2)]
        arr, i = SLOW_HERO, int(sum(sp[:int(ti)]))
    elif src == "c": arr, i = C, int(f)
    else: arr, i = (A if src == "a" else B), int((ss + ti / FPS) * FPS)
    return mfx.cover(arr[int(min(len(arr) - 1, max(0, i)))], z, sx, sy, rot, cx=cx, cy=cy)

EXPO = {}
def expo(c, f):
    if c[0] not in EXPO:
        L = kf(nxt_of(c[0])) - kf(c[0])
        ms = [float(np.percentile(raw(c, f + j, j), 60)) for j in np.linspace(0, max(L - 1, 0), 5)]
        EXPO[c[0]] = float(np.clip(0.33 / max(np.median(ms), .02), .6, 2.0))
    return EXPO[c[0]]

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-ss", f"{C0}", "-i", f"{VID}/c.mov", "-map", "0:v", "-map", "1:a", "-t", f"{N / FPS:.3f}",
                        "-af", f"highpass=f=30,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.4,afade=t=out:st={N / FPS - 0.8:.2f}:d=0.8",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", "14M", "-bufsize", "28M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
echo = mfx.Echo((H, W)); prev = np.zeros((H, W), np.float32)
LG = {}                                            # light graffiti per shot (fresh background at each cut)
NERV = mfx.Nervous(depth=20, seed=4); THR = mfx.Threshold()
XEROX = [kf(14.75), kf(16.75)]                     # two 1-bit flash frames on dembow accents
g3 = lambda g: np.repeat(g[..., None], 3, 2)
def hud_on(rgb, f):
    hc, ha = HUD; ha = ha.copy()
    if (f - kf(4)) % SPB >= SPB / 2: ha[140:190, 70:110] = 0          # REC dot blinks on the beat
    rgb = rgb * (1 - ha[..., None] * .9) + hc * ha[..., None] * .9
    tc = timecode(f); return rgb * (1 - tc[..., None] * .9) + .92 * tc[..., None]
E_TYPE, E_MARK, E_EXIT = kf(24), kf(26), kf(27.6)

for f in range(N):
    grain_amt = .05
    if f < kf(0) - .01:
        rgb = STF(min(87, f)); grain_amt = 0
        if f >= kf(0) - 3: rgb = mfx.zoom_blur(rgb, .3)
    else:
        ci = max(i for i, c in enumerate(CUTS) if kf(c[0]) <= f + .01); c = CUTS[ci]; b0, src = c[0], c[1]; ti = f - kf(b0)
        nb = nxt_of(b0)
        if src in ("a", "b", "c", "slow_in", "slow_hero"):
            moving = ti < 5 or b0 >= 14
            g = look(mfx.mblur(lambda tt: raw(c, tt, ti - (f - tt)), f, .5, 3) if moving and src != "slow_in" else raw(c, f, ti), expo(c, f))
            if src in ("c", "slow_hero", "slow_in"):                       # sparklers paint their own trails
                g = LG.setdefault(b0, mfx.LightGraffiti())(g, thr=.82, diff=.16, decay=.84 if src == "c" else .9, gain=.4)
            if c[5] == "drake":                                                 # moody: lower key, anamorphic streaks, fog glow
                g = mfx.fog_glow(mfx.streaks(g * .85, 2, 0, thr=.72, k=.8), .5, .35)
                g = echo(g, .8, .45)
                h = 560 + 200 * mfx.ease_io(ti / (kf(4) - kf(0)))
                g = mfx.letterbox(mfx.vignette(mfx.promist(g, .4), .35), h)
                rgb = g3(g)
                if ti > 8:
                    cc, aa = KICK; aa = (aa * min(1, (ti - 8) / 10))[..., None]; rgb = rgb * (1 - aa) + cc * aa
                if kf(4) - f < 4: rgb = mfx.zoom_blur(rgb, .3 * (1 - (kf(4) - f) / 4))
            else:
                k = (.9 if c[5] == "drop" else .55) * math.exp(-ti / 4) + .18
                if src == "slow_hero": k = .3
                g = mfx.fisheye(g, k)
                g = mfx.bulge(g, (.32 if b0 >= 14 else .2) * env(f, KICKS, 4) + .12 * env(f, SNARES, 3), .55)
                g = mfx.astig(g, (.35 if b0 >= 14 else .2) * env(f, KICKS + SNARES, 5) + (.25 if src.startswith("slow") else 0), thr=.72)
                if b0 == 4 and ti < 5: g = mfx.zoom_blur(g, .3 * (1 - ti / 5))
                if b0 >= 14 and src == "c": g = mfx.streaks(g, 4, 45, thr=.86, k=.4)
                if any(0 <= f - x < 2 for x in XEROX): g = THR(g)
                if b0 == 19 and ti < 6: g = mfx.kaleidoscope(g, 6, rot=ti * 8) if ti < 4 else mfx.zoom_blur(g, .25 * (1 - (ti - 4) / 2))
                if c[5] == "sort" and ti < 6: g = mfx.pixel_sort(g, .5) * (1 - ti / 8) + g * (ti / 8)
                if c[5] == "blocks" and ti < 4: g = mfx.block_glitch(g, prev, .3, seed=int(f))
                if nb == 18 and kf(18) - f < 5: g = mfx.liquid(g, 130 * (1 - (kf(18) - f) / 5), f)
                if c[5] == "melt" and ti < 6: g = mfx.liquid(g, 130 * (1 - ti / 6), f)
                if src == "slow_hero": g = mfx.liquid(g, 16, f * .3)
                if b0 == 20 and kf(22) - f < 7:
                    q = 1 - (kf(22) - f) / 7; g = mfx.twirl(g, 2.6 * q ** 2, .7) * (1 - q ** 2)
                g = echo(g, .86 if src == "slow_hero" else .55, .5 if src == "slow_hero" else (.32 if ti < 7 else .18))
                prev = g
                rgb = g3(mfx.vignette(mfx.promist(g, .28), .3))
                if b0 >= 18 and f >= kf(18):                                    # the name slams on the bar line, blinks on the beat
                    on = (int((f - kf(18)) / (SPB / 2)) % 2 == 0) if f < kf(20) else True
                    if on:
                        cc, aa = SLAM; band = np.clip(1 - np.abs(np.arange(H) - 960) / 520, 0, 1)[:, None, None] * .55
                        rgb = rgb * (1 - band); rgb = rgb * (1 - aa[..., None]) + cc * aa[..., None]
                rgb = hud_on(rgb, f)
        elif src.startswith("word:"):
            name = src[5:]; m = ti
            bg = look(raw((7, "c", None, WIDE, 0, ""), f, m)) * .26
            if name == "b2b":
                cc, aa = B2B; s = 1 + .25 * (1 - mfx.expo_out(m / 5))
                aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / s, 0, W / 2 * (1 - 1 / s), 0, 1 / s, H / 2 * (1 - 1 / s)), resample=Image.BILINEAR))
                g = mfx.invert_hit(bg, m / 5) if m < 5 else bg
                rgb = g3(g) * (1 - aa[..., None]) + cc * aa[..., None]
            else:
                stk = STK_IAM if name == "iam" else STK_RAY
                st = mfx.shift(stk, 0, (-1 if name == "iam" else 1) * m * 11)
                if m < 6: st = mfx.liquid(st, 50 * (1 - mfx.ease_out(m / 6)), f)
                g = mfx.bulge(np.maximum(bg, st), .25 * env(f, KICKS, 4) + .12 * env(f, SNARES, 3), .6)
                rgb = g3(g)
            rgb = hud_on(rgb, f); echo.buf *= .5
        elif src == "stutter":
            half = int(ti // (SPB / 2)); q = ti - half * SPB / 2
            cc = [CUTS[2], (5, "c", None, SPARK, 0, ""), CUTS[1], (5, "c", None, HANDS, 0, "")][half % 4]
            g = look(raw(cc, f, 3 + q), expo(cc, f))
            g = NERV(g, hit=q < 1)                                             # Carti stutter: short runs back and forth in time
            g = mfx.fisheye(g, .6 * math.exp(-q / 3) + .2)
            if env(f, SNARES, 3) > .6: g = mfx.invert_hit(g, 1 - env(f, SNARES, 3))
            g = mfx.twitch(g, f, amount=.9); prev = g
            rgb = hud_on(g3(mfx.vignette(g, .3)), f)
        elif src == "silence":                                                 # the track goes quiet: so does the picture
            p = (f - kf(11.7)) / (kf(14) - kf(11.7))
            g = mfx.block_glitch(prev * max(0, 1 - p * 2.5) ** 1.5, np.zeros_like(prev), .25 + .6 * p, seed=int(f))
            prev = g; rgb = g3(g)
            if 0 <= kf(14) - f < 5: rgb = mfx.screen(rgb, LOGO * (.35 if int(f) % 2 else .12))
            rgb = hud_on(rgb, f)
        else:                                                                  # ending
            if f < E_TYPE:
                canvas = np.zeros((H, W), np.float32)
                for i, (a0, a1) in enumerate(EYE_BANDS):
                    fb = kf(22.25) + i * SPB / 2
                    if f < fb: continue
                    mm = f - fb; off = 34 * (1 - mfx.ease_out(mm / 6))
                    band = np.zeros_like(canvas); band[a0:a1] = EY[a0:a1]
                    if off > .5: band = np.maximum(mfx.shift(band, -off), mfx.shift(band, off)) * .8
                    canvas = np.maximum(canvas, band * min(1, .35 + mm / 4))
                canvas = mfx.bulge(canvas, .16 * env(f, [kf(n) for n in range(22, 24)], 5), .5)
                rgb = g3(mfx.promist(canvas, .3)); grain_amt = .04
            elif f < E_MARK:
                z = 1 + .04 * (f - E_TYPE) / (E_MARK - E_TYPE); cc, aa = DEVIL
                aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR))
                rgb = cc * (aa * min(1, (f - E_TYPE) / 4))[..., None]; grain_amt = .03
            elif f < E_EXIT: rgb = STF(int(min(70, 40 + (f - E_MARK)))); grain_amt = .02
            else: rgb = STF(int(min(89, 74 + (f - E_EXIT)))); grain_amt = .02
    if grain_amt: rgb = mfx.grain(rgb, grain_amt, rng=rng)
    enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes())
    if f % 90 == 0: print("frame", f, "/", N, flush=True)
enc.stdin.close(); enc.wait()
print("done", N, round(N / FPS, 2), "s")
