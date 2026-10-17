"""MOTION montage v2: A NIGHT WITH IAMARIOLOGY (~29 s). Rule: no moment of footage is used twice.
Every shot is a fresh stretch of a clip, playing forward, so there is always real movement. The neon-room and
dancing clips lead; the sparkler booth appears only on the drop and the finale.
Music edit: the bed runs 7.5-30.18 s of the sparkler track, then jumps on a beat to 45.85-52.4 s
(skipping the middle so both silences and both drops stay). 6 ms crossfade at the jump.
usage: python3 montage2_iam.py <video_dir> <sting_dir> <out.mp4>"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fx"))
import mfx
from mfx import W, H, FPS
VID, STING, OUT = sys.argv[1:4]; D = os.path.dirname(os.path.abspath(__file__))
SEG1, SEG2 = (7.5, 30.18), (45.85, 52.4)
L1 = SEG1[1] - SEG1[0]
def bed(out_t): return SEG1[0] + out_t if out_t < L1 else SEG2[0] + (out_t - L1)
def out_of(b): return (b - SEG1[0]) if b <= SEG1[1] + 1e-6 else L1 + (b - SEG2[0])
N = int((L1 + SEG2[1] - SEG2[0]) * FPS)
def beats(t0, bpm, t1): return list(np.arange(t0, t1 - 1e-3, 60 / bpm))
A, B = beats(10.185, 97.82, 17.79), beats(19.19, 93.48, 30.18)
Db = beats(40.165, 94.98, 47.0); DROP2 = 48.95
KICKS = [out_of(t) * FPS for t in A + B + [t for t in Db if t >= SEG2[0]] + [DROP2 + i * 60 / 95 for i in range(6)]]
rng = np.random.default_rng(10)

Cp = mfx.plate(f"{VID}/c.mov", 7.5, 52.4, bw="blue")              # index = (bed - 7.5) * FPS
PL = {"a": mfx.plate(mfx.stabilize(f"{VID}/a.mov"), deflicker=True, bw="blue"), "b": mfx.plate(f"{VID}/b.mov"),
      "d": mfx.plate(f"{VID}/d.mov", bw="blue"), "e": mfx.plate(f"{VID}/e.mov", bw="blue")}
SLOW_IN = mfx.plate(f"{VID}/c.mov", 12.5, 13.9, fps=75, interp=True, bw="blue")
HERO = mfx.plate(f"{VID}/e.mov", 1.9, 2.9, fps=90, interp=True, bw="blue")
EYE_END = mfx.plate(f"{VID}/d.mov", 9.0, 9.85, fps=75, interp=True, bw="blue")    # 2.5x frames: fills the 2 s silence
def rgba(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255; return a[..., :3], a[..., 3]
IAM = rgba(f"{D}/P_iam.png")[1]; STK = mfx.stack(IAM, 9, .55)
ANN, DEVIL, HUD, KICK = (rgba(f"{D}/P_{n}.png") for n in ("announce", "devil", "hud96", "kick2"))
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
LOGO = np.clip((STF(66) - .05) / .95, 0, 1)
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
g3 = lambda g: np.repeat(g[..., None], 3, 2)

FULL, D_EYE = (1.0, .5, .5), (2.2, .5, .23)
D_MID, D_HANDS, D_FACE = (1.15, .5, .45), (1.7, .5, .78), (1.6, .5, .33)
E_FR = (1.12, .47, .42); B_FR = (1.05, .5, .5)
# (bed time, kind, source, source start s, framing, fx, why)
E = [(A[0], "drake", "slow_in", 0, None, "", "moody open on the sparklers"),
     (A[4], "eye", "d", 0.0, D_EYE, "", "the neon eye tilts down to him"),
     (A[8], "shot", "a", 0.5, FULL, "zin", "arms up: motion carries over the cut"),
     (A[9], "shot", "b", 0.5, B_FR, "", "a different room, same energy"),
     (A[10], "shot", "e", 0.0, E_FR, "", "him at the decks, close"),
     (A[11], "shot", "d", 2.6, D_HANDS, "stutter", "hands on the mixer, stutter into the silence"),
     (17.79, "silence", None, 0, None, "", "the track goes quiet"),
     (B[0], "shot", "c", None, FULL, "drop", "DROP: the real room as the beat hits"),
     (B[1], "shot", "d", 3.6, D_FACE, "", "hand to the headphones"),
     (B[2], "shot", "a", 1.6, FULL, "", "masked set, arms"),
     (B[3], "shot", "b", 9.7, B_FR, "", "beams and hands"),
     (B[4], "shot", "e", 0.7, E_FR, "", "smiling, dancing"),
     (B[5], "shot", "d", 4.4, D_MID, "", "the eye behind him again, wider"),
     (B[6], "shot", "a", 2.6, FULL, "xerox", "1-bit flash on the accent"),
     (B[7], "shot", "b", 12.6, B_FR, "", "beams cross on the beat"),
     (B[8], "stack", "d", 5.05, D_MID, "", "the name, on the bar line"),
     (B[9], "shot", "e", 3.0, E_FR, "", "dancing"),
     (B[10], "shot", "d", 5.75, D_FACE, "", "hand to the ear"),
     (B[11], "shot", "b", 15.0, B_FR, "melt", "hands up, melts in"),
     (B[12], "shot", "a", 7.5, FULL, "", "masked, arms high"),
     (B[13], "shot", "d", 6.8, D_HANDS, "", "back to the mixer"),
     (B[14], "point", "hero", 0, E_FR, "", "the point to camera: slow, freeze, his name"),
     (SEG2[0], "shot", "d", 8.2, D_FACE, "", "the music jumps: nodding"),
     (Db[10] if len(Db) > 10 else 46.48, "shot", "b", 4.0, B_FR, "", "the room, last look"),
     (47.0, "silence_eye", None, 0, None, "", "silence 2: the eye glows in the dark, slowed (the last unused second of the neon clip)"),
     (DROP2, "finale", "c", None, FULL, "", "DROP 2: the whole room, the card"),
     (50.35, "devil", None, 0, None, "", ""), (51.15, "mark", None, 0, None, "", "")]
E.sort(key=lambda e: out_of(e[0]))
used = {}
for t0, kind, src, st, fr, fx, why in E:                                  # guard: no source moment twice
    if src in PL and st is not None:
        t1 = next((out_of(x[0]) for x in E if out_of(x[0]) > out_of(t0)), N / FPS); dur = t1 - out_of(t0)
        for (a0, a1) in used.get(src, []):
            assert st >= a1 - .02 or st + dur <= a0 + .02, f"reused {src} {st}"
        used.setdefault(src, []).append((st, st + dur))

def env(f, decay=4):
    last = max([h for h in KICKS if h <= f], default=None); return 0 if last is None else math.exp(-(f - last) / decay)
def hud(rgb, f, s=.9):
    hc, ha = HUD; ha = ha.copy()
    last = max([h for h in KICKS if h <= f], default=None)
    if last is None or f - last > 7: ha[140:190, 70:110] = 0
    return rgb * (1 - ha[..., None] * s) + hc * ha[..., None] * s
def frame_of(src, st, out_f, ti, fr, drift=0.0, shake=False):
    z, cx, cy = fr[0] * (1 + drift), fr[1], fr[2]; sx = sy = rot = 0.0
    if shake:
        for h in KICKS:
            if h <= out_f < h + 10:
                dx, dy, r = mfx.shake(out_f, h, amp=8, seed=int(h)); sx += dx; sy += dy; rot += r
    if src == "c": arr, i = Cp, int((bed(out_f / FPS) - 7.5) * FPS)
    else: arr, i = PL[src], int(st * FPS + ti)
    return mfx.cover(arr[int(min(len(arr) - 1, max(0, i)))], z, sx, sy, rot, cx=cx, cy=cy)
EXPO = {}
def expo(key, fn):
    if key not in EXPO:
        EXPO[key] = float(np.clip(0.33 / max(np.median([float(np.percentile(fn(j), 60)) for j in (0, 4, 8)]), .02), .6, 2.0))
    return EXPO[key]

af = (f"[1:a]atrim={SEG1[0]}:{SEG1[1]},asetpts=PTS-STARTPTS[s1];[1:a]atrim={SEG2[0]}:{SEG2[1]},asetpts=PTS-STARTPTS[s2];"
      f"[s1][s2]acrossfade=d=0.006:c1=tri:c2=tri,highpass=f=30,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.3,afade=t=out:st={N / FPS - 0.5:.2f}:d=0.5[a]")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{VID}/c.mov", "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-t", f"{N / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "slow", "-b:v", "7M", "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
echo = mfx.Echo((H, W)); nerv = mfx.Nervous(16, seed=6); thr = mfx.Threshold(); LG = {}; prev = np.zeros((H, W), np.float32)

for f in range(N):
    ot = f / FPS; ga = .05
    first = out_of(E[0][0])
    if ot < first:
        rgb = STF(min(87, f)); ga = 0
        if first - ot < .1: rgb = mfx.zoom_blur(rgb, .3)
        enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes()); continue
    ei = max(i for i, e in enumerate(E) if out_of(e[0]) <= ot + 1e-6); t0, kind, src, st, fr, fx, _ = E[ei]
    t1 = out_of(E[ei + 1][0]) if ei + 1 < len(E) else N / FPS; ti = f - out_of(t0) * FPS; L = (t1 - out_of(t0)) * FPS; q = min(1, ti / max(L, 1))
    if kind == "drake":
        g = look(mfx.cover(SLOW_IN[int(min(len(SLOW_IN) - 1, ti * 1.25))], 1.6 * (1 + .1 * q), cx=.5, cy=.43), 1.2)
        g = LG.setdefault("in", mfx.LightGraffiti())(g, thr=.82, diff=.16, decay=.9, gain=.4)
        g = mfx.fog_glow(mfx.streaks(g * .85, 2, 0, thr=.72, k=.8), .5, .35); g = echo(g, .8, .45)
        rgb = g3(mfx.letterbox(mfx.vignette(mfx.promist(g, .4), .35), 560 + 200 * mfx.ease_io(q)))
        if ti > 8: cc, aa = KICK; aa = (aa * min(1, (ti - 8) / 10))[..., None]; rgb = rgb * (1 - aa) + cc * aa
    elif kind == "eye":
        qq = mfx.ease_io(q); g = look(mfx.cover(PL["d"][int(min(len(PL["d"]) - 1, st * FPS + ti))], 2.2 - 1.1 * qq, cx=.5, cy=.23 + .22 * qq))
        g = mfx.fog_glow(mfx.streaks(g, 2, 0, thr=.8, k=.7), .5, .45)
        if ti < 5: g = mfx.zoom_blur(g, .3 * (1 - ti / 5))
        g = echo(g, .6, .3); rgb = hud(g3(mfx.vignette(mfx.promist(g, .3), .3)), f)
    elif kind in ("shot", "finale", "stack"):
        drift = (-.05 if fr[0] > 1.2 else .05)
        fn = lambda tt: frame_of(src, st, tt, ti - (f - tt), fr, drift * min(1, (ti - (f - tt)) / max(L, 1)), shake=out_of(t0) >= out_of(B[0]))
        k_ = expo((t0, src), lambda j: frame_of(src, st, f + j, ti + j, fr))
        g = look(mfx.mblur(fn, f, .5, 3) if ti < 5 or out_of(t0) >= out_of(B[0]) else fn(f), k_)
        if src == "c": g = LG.setdefault(t0, mfx.LightGraffiti())(g, thr=.82, diff=.16, decay=.84, gain=.4)
        kk = (.9 if fx == "drop" or kind == "finale" else .5) * math.exp(-ti / 4) + .18
        g = mfx.fisheye(g, kk); g = mfx.bulge(g, (.32 if out_of(t0) >= out_of(B[0]) else .2) * env(f), .55)
        if src == "c": g = mfx.streaks(g, 4, 45, thr=.86, k=.4)
        if src == "b": g = mfx.astig(g, .3 * env(f, 6), thr=.72)
        if fx == "zin" and ti < 5: g = mfx.zoom_blur(g, .3 * (1 - ti / 5))
        if fx == "xerox" and ti < 2: g = thr(g)
        if fx == "melt" and ti < 6: g = mfx.liquid(g, 130 * (1 - ti / 6), f)
        if ei + 1 < len(E) and E[ei + 1][5] == "melt" and (t1 - ot) * FPS < 5: g = mfx.liquid(g, 130 * (1 - (t1 - ot) * FPS / 5), f)
        if fx == "stutter" and L - ti < 0.6134 * FPS: g = nerv(g, hit=int(ti) % 9 == 0)   # stutter in the last beat
        g = echo(g, .55, .3 if ti < 7 else .16); prev = g
        if kind == "stack":
            s_ = mfx.shift(STK, 0, -ti * 12); s_ = mfx.liquid(s_, 45 * (1 - mfx.ease_out(ti / 6)), f) if ti < 6 else s_
            g = np.maximum(g * .25, s_)
        rgb = g3(mfx.vignette(mfx.promist(g, .28), .3)) if kind != "stack" else g3(g)
        if kind == "finale":
            cc, aa = ANN; k2 = min(1, ti / 4); band = np.clip(1 - np.abs(np.arange(H) - 960) / 420, 0, 1)[:, None, None] * .6 * k2
            rgb = rgb * (1 - band); rgb = rgb * (1 - aa[..., None] * k2) + cc * aa[..., None] * k2
        rgb = hud(rgb, f)
    elif kind == "silence":
        g = mfx.block_glitch(prev * max(0, 1 - q * 2.5) ** 1.5, np.zeros_like(prev), .25 + .6 * q, seed=int(f)); prev = g
        rgb = g3(g)
        if 0 <= L - ti < 5: rgb = mfx.screen(rgb, LOGO * (.35 if int(f) % 2 else .12))
        rgb = hud(rgb, f)
    elif kind == "silence_eye":
        g = look(mfx.cover(EYE_END[int(min(len(EYE_END) - 1, ti * 1.05))], 1.9 - .25 * mfx.ease_io(q), cx=.5, cy=.26)) * (.5 + .1 * math.sin(ti / 6))
        g = mfx.fog_glow(mfx.streaks(g, 2, 0, thr=.45, k=.6), .5, .4); g = echo(g, .85, .4); prev = g
        rgb = g3(mfx.letterbox(mfx.vignette(g, .45), 900))
        if 0 <= L - ti < 5: rgb = mfx.screen(rgb, LOGO * (.35 if int(f) % 2 else .12))
        rgb = hud(rgb, f, .6)
    elif kind == "point":
        p = min(1, q / .5); idx = int(21 * (1 - (1 - p) ** 2.2)) if p < 1 else 21
        g = look(mfx.cover(HERO[idx], 1.12, cx=.47, cy=.42)); g = mfx.fisheye(g, .3 + .4 * math.exp(-ti / 5))
        if p >= 1:
            m = ti - .5 * L; g = np.clip((g - .5) * (1 + .25 * min(1, m / 3)) + .5, 0, 1)
            if m < 4: g = mfx.flash(g, m / 4, .7)
        g = echo(g, .82, .4); prev = g; rgb = g3(mfx.vignette(mfx.promist(g, .3), .3))
        if p >= 1:
            k2 = min(1, (ti - .5 * L) / 2); band = np.clip(1 - np.abs(np.arange(H) - 960) / 300, 0, 1)[:, None, None] * .6 * k2
            rgb = rgb * (1 - band); aa = IAM * k2; rgb = rgb * (1 - aa[..., None]) + np.array([.95, .93, .9]) * aa[..., None]
        rgb = hud(rgb, f)
    elif kind == "devil":
        z = 1 + .04 * q; cc, aa = DEVIL
        aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR))
        rgb = cc * (aa * min(1, ti / 4))[..., None]; ga = .03
    else:
        rgb = STF(int(min(70, 50 + ti))) if ti < 20 else STF(int(min(89, 74 + ti - 20))); ga = .02
    if ga: rgb = mfx.grain(rgb, ga, rng=rng)
    enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes())
    if f % 150 == 0: print("frame", f, "/", N, flush=True)
enc.stdin.close(); enc.wait()
with open(os.path.splitext(OUT)[0] + "_cutlist.md", "w") as fh:
    fh.write("| Time | Shot | Source moment | Why |\n|---|---|---|---|\n")
    for t0, kind, src, st, fr, fx, why in E:
        fh.write(f"| {out_of(t0):.2f} s | {kind} | {src or '-'} {'' if st is None else f'@ {st:.2f} s'} | {why} |\n")
print("done", N, round(N / FPS, 1), "s")
