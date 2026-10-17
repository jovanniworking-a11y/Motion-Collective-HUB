"""MOTION montage: A NIGHT WITH IAMARIOLOGY (~45 s, 9:16). All five of his clips, cut to the sparkler clip's own track.
The bed's tempo drifts (phone recording), so the beat grid is fitted per section and every cut indexes into it.

  bed 7.5-10.2   I    the mark
  10.2-17.8      II   Drake open (letterboxed slow-motion sparklers, title) -> the neon eye reveal -> first cuts, stutter
  17.8-19.2           silence 1: black, logo flash
  19.2-30.2      III  drop 1: every beat across sparklers / neon room / masked set, name stack, melt, stutter
  30.2-40.2      IV   chapter 2, the big rooms: beams and the masked set, 2-beat cuts, rays, vertigo, xerox, kaleidoscope
  40.2-47.0      V    the breath: slow-motion sparkler with light graffiti, then the point to camera freezes with his name
  47.0-48.95          silence 2: black, logo flash
  48.95-52.4     VI   drop 2: the whole room, the card, Devil's Night, the mark
usage: python3 montage_iam.py <video_dir> <sting_dir> <out.mp4>"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fx"))
import mfx
from mfx import W, H, FPS
VID, STING, OUT = sys.argv[1:4]; D = os.path.dirname(os.path.abspath(__file__))
C0, CEND = 7.5, 52.4
N = int((CEND - C0) * FPS)
fr_of = lambda t: (t - C0) * FPS                                  # bed time -> output frame
def beats(t0, bpm, t1): return list(np.arange(t0, t1 - 1e-3, 60 / bpm))
A, B, Cb, Db = beats(10.185, 97.82, 17.79), beats(19.19, 93.48, 30.18), beats(30.18, 98.68, 40.165), beats(40.165, 94.98, 47.0)
DROP2 = 48.95
KICKS = [fr_of(t) for t in A + B + Cb + Db] + [fr_of(DROP2 + i * 60 / 95) for i in range(6)]
rng = np.random.default_rng(9)

# plates (B&W filter chosen per light: blue under yellow/amber light)
Cp = mfx.plate(f"{VID}/c.mov", C0, CEND, bw="blue")                # bed clip, in sync: index = output frame
Ap = mfx.plate(mfx.stabilize(f"{VID}/a.mov"), deflicker=True, bw="blue")
Bp = mfx.plate(f"{VID}/b.mov")
Dp = mfx.plate(f"{VID}/d.mov", bw="blue")
SLOW_IN = mfx.plate(f"{VID}/c.mov", 12.5, 13.9, fps=75, interp=True, bw="blue")
SLOW_SP = mfx.plate(f"{VID}/c.mov", 28.4, 29.6, fps=90, interp=True, bw="blue")
HERO = mfx.plate(f"{VID}/e.mov", 1.9, 2.9, fps=90, interp=True, bw="blue")
PL = {"c": Cp, "a": Ap, "b": Bp, "d": Dp}

def rgba(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255; return a[..., :3], a[..., 3]
IAM = rgba(f"{D}/P_iam.png")[1]; STK = mfx.stack(IAM, 9, .55)
ANN, DEVIL, HUD, KICK = (rgba(f"{D}/P_{n}.png") for n in ("announce", "devil", "hud96", "kick2"))
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
LOGO = np.clip((STF(66) - .05) / .95, 0, 1)
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
g3 = lambda g: np.repeat(g[..., None], 3, 2)

# framings: zoom, cx, cy
WIDE, SPARK, HANDS, CROWD = (1.04, .5, .5), (1.6, .5, .43), (1.9, .52, .56), (1.35, .5, .45)
D_EYE, D_HANDS, D_FACE, D_WIDE = (2.0, .5, .25), (1.9, .5, .82), (1.7, .5, .32), (1.1, .5, .45)
FULL = (1.0, .5, .5)
# EDL: (bed start time, kind, source, source time (None = sync for c), framing, fx)
E = []
add = lambda t, *r: E.append((t,) + r)
add(10.185 - 0.0, "drake", "slow_in", 0, SPARK, "")
add(A[4], "eye", "d", 3.0, D_EYE, "")
add(A[8], "shot", "a", 0.95, FULL, "zin"); add(A[9], "shot", "b", 9.3, FULL, ""); add(A[10], "shot", "d", 6.0, D_FACE, ""); add(A[11], "shot", "c", None, HANDS, "")
add(A[12], "stutter", None, 0, None, "")
add(17.79, "silence", None, 0, None, "")
seq = [("c", None, WIDE, "drop"), ("d", 1.5, D_HANDS, ""), ("c", None, SPARK, ""), ("e", 0, (1.12, .47, .42), ""), ("c", None, HANDS, ""),
       ("d", 2.4, D_WIDE, ""), ("c", None, CROWD, "xerox"), ("a", 1.0, FULL, "")]
for i, (s, st, fr, fx) in enumerate(seq): add(B[i], "shot", s, st, fr, fx)
add(B[8], "stack", None, 0, None, "")
for i, (s, st, fr, fx) in zip(range(9, 14), [("c", None, SPARK, "xerox"), ("d", 7.0, D_FACE, ""), ("b", 10.6, FULL, "melt"), ("c", None, WIDE, ""), ("d", 4.2, D_EYE, "")]):
    add(B[i], "shot", s, st, fr, fx)
add(B[14], "stutter", None, 0, None, "")
for i, (s, st, fr, fx) in zip(range(0, 16, 2), [("b", 10.6, FULL, "rays"), ("a", 2.05, FULL, "vertigo"), ("c", None, SPARK, ""), ("b", 12.0, FULL, "xerox"),
                                              ("a", 0.6, FULL, ""), ("c", None, HANDS, ""), ("b", 14.6, FULL, "kaleido"), ("c", None, WIDE, "")]):
    add(Cb[i], "shot", s, st, fr, fx)
add(Db[0], "breath", "slow_sp", 0, (1.15, .5, .5), "")
add(Db[4], "point", "hero", 0, (1.12, .47, .42), "")
for i, (s, st, fr, fx) in zip(range(8, 11), [("d", 1.0, D_HANDS, ""), ("a", 1.4, FULL, ""), ("c", None, SPARK, "")]):
    if i < len(Db): add(Db[i], "shot", s, st, fr, fx)
add(47.0, "silence", None, 0, None, "")
add(DROP2, "finale", "c", None, (1.0, .5, .5), "")
add(50.35, "devil", None, 0, None, ""); add(51.15, "mark", None, 0, None, "")
E.sort(key=lambda e: e[0])

def env(f, decay=4):
    last = max([h for h in KICKS if h <= f], default=None); return 0 if last is None else math.exp(-(f - last) / decay)
def hud(rgb, f, ha_scale=.9):
    hc, ha = HUD; ha = ha.copy()
    if env(f, 1e9) and (f - max(h for h in KICKS if h <= f)) > 7: ha[140:190, 70:110] = 0
    return rgb * (1 - ha[..., None] * ha_scale) + hc * ha[..., None] * ha_scale
EXPO = {}
def src_frame(src, st, f, ti, fr, z_drift=0.0, shake=False):
    z, cx, cy = fr[0] * (1 + z_drift), fr[1], fr[2]
    sx = sy = rot = 0.0
    if shake:
        for h in KICKS:
            if h <= f < h + 10:
                dx, dy, r = mfx.shake(f, h, amp=8, seed=int(h)); sx += dx; sy += dy; rot += r
    if src == "c": arr, i = Cp, int(f)
    elif src == "e": arr, i = mfx.plate(f"{VID}/e.mov", bw="blue") if "e" not in PL else PL["e"], int((st + 1.0) * FPS + ti)
    else: arr, i = PL[src], int((st + ti / FPS) * FPS)
    return mfx.cover(arr[int(min(len(arr) - 1, max(0, i)))], z, sx, sy, rot, cx=cx, cy=cy)
PL["e"] = mfx.plate(f"{VID}/e.mov", bw="blue")

def expo(key, fn):
    if key not in EXPO:
        ms = [float(np.percentile(fn(j), 60)) for j in (0, 4, 8)]
        EXPO[key] = float(np.clip(0.33 / max(np.median(ms), .02), .6, 2.0))
    return EXPO[key]

af = f"atrim={C0}:{CEND},asetpts=PTS-STARTPTS,highpass=f=30,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.3,afade=t=out:st={CEND - C0 - 0.5:.2f}:d=0.5"
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{VID}/c.mov", "-map", "0:v", "-map", "1:a", "-af", af, "-t", f"{N / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", "14M", "-bufsize", "28M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
echo = mfx.Echo((H, W)); nerv = mfx.Nervous(20, seed=5); thr = mfx.Threshold(); vert = mfx.Vertigo()
LG = {}; prev = np.zeros((H, W), np.float32); freeze = None
STUT = [("c", None, SPARK), ("d", 2.0, D_HANDS), ("a", 1.0, FULL), ("c", None, HANDS)]

for f in range(N):
    t = C0 + f / FPS; ga = .05
    if t < E[0][0]:
        rgb = STF(min(87, f)); ga = 0
        if E[0][0] - t < 0.1: rgb = mfx.zoom_blur(rgb, .3)
        enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes()); continue
    ei = max(i for i, e in enumerate(E) if e[0] <= t + 1e-6); t0, kind, src, st, fr, fx = E[ei]
    t1 = E[ei + 1][0] if ei + 1 < len(E) else CEND; ti = f - fr_of(t0); L = (t1 - t0) * FPS; q = min(1, ti / max(L, 1))
    if kind == "drake":
        g = look(mfx.cover(SLOW_IN[int(min(len(SLOW_IN) - 1, ti * 1.25))], SPARK[0] * (1 + .1 * q), cx=.5, cy=.43), 1.2)
        g = LG.setdefault("in", mfx.LightGraffiti())(g, thr=.82, diff=.16, decay=.9, gain=.4)
        g = mfx.fog_glow(mfx.streaks(g * .85, 2, 0, thr=.72, k=.8), .5, .35); g = echo(g, .8, .45)
        g = mfx.letterbox(mfx.vignette(mfx.promist(g, .4), .35), 560 + 200 * mfx.ease_io(q))
        rgb = g3(g)
        if ti > 8: cc, aa = KICK; aa = (aa * min(1, (ti - 8) / 10))[..., None]; rgb = rgb * (1 - aa) + cc * aa
    elif kind == "eye":
        qq = mfx.ease_io(q); g = look(mfx.cover(Dp[int(min(len(Dp) - 1, (st + ti / FPS) * FPS))], 2.2 - 1.1 * qq, cx=.5, cy=.23 + .22 * qq))
        g = mfx.fog_glow(mfx.streaks(g, 2, 0, thr=.8, k=.7), .5, .45)
        if ti < 5: g = mfx.zoom_blur(g, .3 * (1 - ti / 5))
        g = echo(g, .6, .3); rgb = hud(g3(mfx.vignette(mfx.promist(g, .3), .3)), f)
    elif kind in ("shot", "finale"):
        fn = lambda tt, jj=None: src_frame(src, st, tt, ti - (f - tt), fr, (-.05 if fr[0] > 1.2 else .05) * min(1, (ti - (f - tt)) / max(L, 1)), shake=t0 >= 19)
        k_ = expo((t0, src), lambda j: src_frame(src, st, f + j, ti + j, fr))
        g = look(mfx.mblur(fn, f, .5, 3) if ti < 5 or t0 >= 19 else fn(f), k_)
        if src == "c": g = LG.setdefault(t0, mfx.LightGraffiti())(g, thr=.82, diff=.16, decay=.84, gain=.4)
        kk = (.9 if fx == "drop" or kind == "finale" else .5) * math.exp(-ti / 4) + .18
        g = mfx.fisheye(g, kk); g = mfx.bulge(g, (.32 if t0 >= 19 else .2) * env(f), .55)
        if src == "c" and t0 >= 19: g = mfx.streaks(g, 4, 45, thr=.86, k=.4)
        if src == "b": g = mfx.astig(g, .3 * env(f, 6), thr=.72)
        if fx == "zin" and ti < 5: g = mfx.zoom_blur(g, .3 * (1 - ti / 5))
        if fx == "xerox" and ti < 2: g = thr(g)
        if fx == "rays": g = mfx.rays(g, .5, .3, .6 * (1 - q))
        if fx == "vertigo": g = vert(g, 1.03, .7)
        if fx == "kaleido" and ti < 5: g = mfx.kaleidoscope(g, 6, rot=ti * 8)
        if fx == "melt" and ti < 6: g = mfx.liquid(g, 130 * (1 - ti / 6), f)
        if ei + 1 < len(E) and E[ei + 1][5] == "melt" and (E[ei + 1][0] - t) * FPS < 5: g = mfx.liquid(g, 130 * (1 - (E[ei + 1][0] - t) * FPS / 5), f)
        g = echo(g, .55, .3 if ti < 7 else .16); prev = g
        rgb = g3(mfx.vignette(mfx.promist(g, .28), .3))
        if kind == "finale":
            cc, aa = ANN; k2 = min(1, ti / 4); band = np.clip(1 - np.abs(np.arange(H) - 960) / 420, 0, 1)[:, None, None] * .6 * k2
            rgb = rgb * (1 - band); rgb = rgb * (1 - aa[..., None] * k2) + cc * aa[..., None] * k2
        rgb = hud(rgb, f)
    elif kind == "stack":
        bg = look(src_frame("c", None, f, ti, WIDE)) * .25
        s_ = mfx.shift(STK, 0, -ti * 12); s_ = mfx.liquid(s_, 45 * (1 - mfx.ease_out(ti / 6)), f) if ti < 6 else s_
        rgb = hud(g3(mfx.bulge(np.maximum(bg, s_), .25 * env(f), .6)), f)
    elif kind == "stutter":
        half = int(ti // 9); s_, st_, fr_ = STUT[half % 4]
        g = look(src_frame(s_, st_, f, 3 + ti % 9, fr_), 1.1); g = nerv(g, hit=ti % 9 < 1)
        g = mfx.fisheye(g, .6 * math.exp(-(ti % 9) / 3) + .2)
        if ti % 9 < 2: g = mfx.invert_hit(g, (ti % 9) / 2)
        prev = g; rgb = hud(g3(mfx.vignette(g, .3)), f)
    elif kind == "silence":
        g = mfx.block_glitch(prev * max(0, 1 - q * 2.5) ** 1.5, np.zeros_like(prev), .25 + .6 * q, seed=int(f)); prev = g
        rgb = g3(g)
        if 0 <= (t1 - t) * FPS < 5: rgb = mfx.screen(rgb, LOGO * (.35 if int(f) % 2 else .12))
        rgb = hud(rgb, f)
    elif kind == "breath":                                          # the music thins out: so does the edit
        g = look(mfx.cover(SLOW_SP[int(min(len(SLOW_SP) - 1, ti * 1.2))], 1.15 * (1 + .06 * q)), 1.2)
        g = LG.setdefault("sp", mfx.LightGraffiti())(g, thr=.8, diff=.14, decay=.93, gain=.5)
        g = mfx.fog_glow(mfx.streaks(g, 2, 0, thr=.74, k=.7), .5, .4); g = echo(g, .85, .45)
        rgb = hud(g3(mfx.letterbox(mfx.vignette(mfx.promist(g, .35), .32), 1100 + 820 * mfx.ease_io(q))), f, .6)
    elif kind == "point":
        p = min(1, q / .55); idx = int(21 * (1 - (1 - p) ** 2.2))
        if p >= 1: freeze = 21; idx = 21
        g = look(mfx.cover(HERO[idx], 1.12, cx=.47, cy=.42))
        g = mfx.fisheye(g, .3 + .4 * math.exp(-ti / 5))
        if p >= 1:
            m = ti - .55 * L; g = np.clip((g - .5) * (1 + .25 * min(1, m / 3)) + .5, 0, 1)
            if m < 4: g = mfx.flash(g, m / 4, .7)
        g = echo(g, .82, .4); rgb = g3(mfx.vignette(mfx.promist(g, .3), .3))
        if p >= 1:
            k2 = min(1, (ti - .55 * L) / 2); band = np.clip(1 - np.abs(np.arange(H) - 960) / 300, 0, 1)[:, None, None] * .6 * k2
            rgb = rgb * (1 - band); aa = IAM * k2; rgb = rgb * (1 - aa[..., None]) + np.array([.95, .93, .9]) * aa[..., None]
        rgb = hud(rgb, f)
    elif kind == "devil":
        z = 1 + .04 * q; cc, aa = DEVIL
        aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR))
        rgb = cc * (aa * min(1, ti / 4))[..., None]; ga = .03
    else:                                                           # the mark: hold, then the fly-through
        rgb = STF(int(min(70, 50 + ti))) if ti < 20 else STF(int(min(89, 74 + ti - 20))); ga = .02
    if ga: rgb = mfx.grain(rgb, ga, rng=rng)
    enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes())
    if f % 150 == 0: print("frame", f, "/", N, flush=True)
enc.stdin.close(); enc.wait(); print("done", N, round(N / FPS, 1), "s")
