"""MOTION montage v11 (19 Oct): the v10 final re-cut to "Believe" (142 bpm, measured). Open on the breakdown,
AFTERIMAGE on the real silence (80.9-81.25 s), cuts start on the drop (82.20 s), a bar-line music edit (beat 40 -> 68)
into the pre-chorus for the eyes, the eyes matte opens on the hit (112.63 s). Every cut sits on a song beat.
MOTION montage v10 FINAL (19 Oct): finishing pass. Steadied phone exposure flicker, tamed blown sparklers,
real step-printed slow motion instead of optical-flow interpolation, real phone grain instead of waxy denoise,
less ghosting and lens warp, steadier type, higher-quality export.
MOTION montage v9 engine (19 Oct): same edit as the v8 final, rendered fast.
  - every shot is rendered to its own cached piece; a re-run only re-draws shots whose line in the edit list changed
  - shots render in parallel on all cores (--jobs), each warmed up on the end of the shot before it so afterimage trails carry over
  - --draft: every other frame, half-size encode, for checking cuts; the final run uses full quality
  - plates are cached on disk by mfx.plate
usage: python3 montage9_engine.py <video_dir> <sting_dir> <song.mp3> <out.mp4> [--draft] [--jobs N]
MOTION montage v8 (19 Oct): two equal stars. Same type size and treatment for both names (intro, stack, end card),
each DJ gets one featured moment (iamariology the point-to-camera freeze, raymixes a tight punch-in), and the small type
is set larger with one tracking so it reads on a phone.
MOTION montage v7 (18 Oct): v6 re-cut to Silva Bumpa "On 2nite" (90.6 bpm, measured: drops back in at 25.75 s,
again 64 beats later at 68.15 s; dip before the chorus hit at 43.3 s). The breakdown (16.5-25.7 s) carries the open,
the 25.75 s drop starts the cuts, the 43 s dip is silence 2, the chorus hit is the finale. One segment, no music edit.
usage: python3 montage7_on2nite.py <video_dir> <sting_dir> <song.mp3> <out.mp4>
MOTION montage v6 (18 Oct, Charvel + Abraham): every cut is a NEW shot. No cutting back to the same angle 2-3 times;
an angle returns only once, inside the triptych. Faster: half-beat burst after the drop. Zooms and effects are back on.
MOTION montage v5 (18 Oct, raymixes notes): the camera never pushes, pans or punches into an artist. Artist shots are
locked-off frames that change only on the cut. More AFTERIMAGE: the 3x eyes open the edit band by band, the first silence
is the AFTERIMAGE card, the second silence is the eyes' negative afterimage, and the end card carries AFTERIMAGE 001.
MOTION montage v4: iamariology b2b raymixes + Austin. The drop trades the two DJs on the beat (a visual back-to-back).
MOTION montage v3: more of the masked set (Jovanni: he is the most lively, jumping, camera to the crowd and back).
MOTION montage v2: A NIGHT WITH IAMARIOLOGY (~29 s). Rule: no moment of footage is used twice.
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
ARGS = sys.argv[1:]; DRAFT = "--draft" in ARGS
JOBS = int(ARGS[ARGS.index("--jobs") + 1]) if "--jobs" in ARGS else (os.cpu_count() or 2)
VID, STING, SONG, OUT = [a for a in ARGS if not a.startswith("--") and not a.isdigit()][:4]
import hashlib, multiprocessing as mp, shutil, time; D = os.path.dirname(os.path.abspath(__file__))
SB, DROP = 60 / 141.99, 82.204                                 # measured song beat and the drop downbeat
BEAT = SB
def G(k): return DROP + k * SB                                 # song beat k, 0 = the drop
SEG1, SEG2 = (G(-22), G(40)), (G(68), G(82.5))                 # bar-line music edit: beat 40 -> beat 68 (pre-chorus)
L1 = SEG1[1] - SEG1[0]
def bed(out_t): return SEG1[0] + out_t if out_t < L1 else SEG2[0] + (out_t - L1)
def out_of(b): return (b - SEG1[0]) if b <= SEG1[1] + 1e-6 else L1 + (b - SEG2[0])
N = int((L1 + SEG2[1] - SEG2[0]) * FPS)
A, B = [G(k) for k in range(-22, 0)], [G(k) for k in range(0, 40)] + [G(k) for k in range(68, 83)]
CHORUS = G(72)                                                 # the hit after the pre-chorus (112.6 s)
KICKS = [out_of(t) * FPS for t in B]
rng = np.random.default_rng(10)

Cp = mfx.plate(f"{VID}/c.mov", 7.5, 52.4, bw="blue")              # index = (source time - 7.5) * FPS
PL = {"a": mfx.plate(mfx.stabilize(f"{VID}/a.mov"), deflicker=True, denoise=False, deblock=True, bw="blue"), "b": mfx.plate(f"{VID}/b.mov"),
      "d": mfx.plate(f"{VID}/d.mov", bw="blue"), "e": mfx.plate(f"{VID}/e.mov", bw="blue")}
def steady_gain(arr, k=9, amount=1.0):
    m = np.array([float(np.percentile(fr_[::4, ::4], 60)) for fr_ in arr]) + 1.0
    med = np.array([np.median(m[max(0, i - k):i + k + 1]) for i in range(len(m))])
    return np.clip(1 + amount * (med / m - 1), .7, 1.45)
GAIN = {"a": steady_gain(PL["a"]), "b": steady_gain(PL["b"], amount=.6), "c": steady_gain(Cp, amount=.6)}   # club strobes keep a little life
RW = {}                                                        # raymixes windows: (clip, start) -> plate from that start
def rwin(src, st, dur=2.5):
    key = (src, st)
    if key not in RW: RW[key] = mfx.plate(f"{VID}/{src}.mov", st, st + dur, bw="red")   # daylight stage: red filter darkens the sky, holds skin
    return RW[key]
SKY_V = mfx.plate(f"{VID}/r4.mov", 2.0, 4.0, max_h=1440, bw="red")
_ph = np.asarray(Image.open(f"{VID}/skyline.jpg").convert("RGB")).astype(np.float32) / 255
SKY_P = np.clip(_ph @ np.array([.70, .22, .08], np.float32), 0, 1)                         # red-filter B&W of the night photo
SKY_P8 = (SKY_P * 255).astype(np.uint8)
HERO = mfx.plate(f"{VID}/e.mov", 1.9, 2.9, fps=90, bw="blue")          # step-printed: real frames held 3x, no invented frames
EYE_END = mfx.plate(f"{VID}/d.mov", 9.0, 9.85, fps=75, interp=True, bw="blue")    # 2.5x frames: fills the 2 s silence
def rgba(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255; return a[..., :3], a[..., 3]
IAM = rgba(f"{D}/P8_iam.png")[1]; STK = mfx.stack(IAM, 9, .55)
ANN, DEVIL, HUD, KICK = (rgba(f"{D}/P{n}.png") for n in ("8_ann2", "_devil", "_hud142b", "_kick3"))
_ey = np.asarray(Image.open(f"{VID}/../flyer/eyes_hc.png").convert("L")).astype(np.float32) / 255
EYES = np.zeros((H, W), np.float32); EYES[285:285 + 1350] = _ey; BANDS = [(285, 285 + 437), (285 + 444, 285 + 915), (285 + 922, 285 + 1350)]
AFT, AFTW, AFTK, DEVIL2 = (rgba(f"{D}/P{n}.png") for n in ("_aft", "_aftw", "8_aftk", "_devil2"))
TAG = {"iam": rgba(f"{D}/P_tag_iam.png"), "ray": rgba(f"{D}/P_tag_ray.png")}
INTRO = {"in_iam": rgba(f"{D}/P8_in_iam.png"), "in_ray": rgba(f"{D}/P8_in_ray.png")}; FOMO = rgba(f"{D}/P_fomo.png")
WHO = {"b": "iam", "a": "iam", "d": "iam", "e": "iam", "hero": "iam", "r1": "ray", "r2": "ray"}
def tag(rgb, src):                                              # camcorder name tag: who is on screen, every shot
    if src not in WHO: return rgb
    cc, aa = TAG[WHO[src]]; return rgb * (1 - aa[..., None] * .9) + cc * aa[..., None] * .9
RAY = rgba(f"{D}/P8_ray.png")[1]; STK_RAY = mfx.stack(RAY, 9, .55)          # same stack as his partner
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
LOGO = np.clip((STF(66) - .05) / .95, 0, 1)
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
g3 = lambda g: np.repeat(g[..., None], 3, 2)

FULL, D_EYE = (1.0, .5, .5), (2.2, .5, .23)
D_MID, D_HANDS, D_FACE = (1.15, .5, .45), (1.7, .5, .78), (1.6, .5, .33)
E_FR = (1.12, .47, .42); B_FR = (1.05, .5, .5)
# (bed time, kind, source, source start s, framing, fx, why)
R1_WIDE, R1_FAN, R1_DJ, R1_DJ2 = (1.0, .5, .5), (1.0, .5, .55), (1.25, .35, .52), (1.25, .35, .4)
R2_DJ, R2_WIDE = (1.3, .55, .6), (1.05, .5, .55)
H_ = SB
RA_SIDE, RA_FRONT, RA_TIGHT, RA_LOW, RA_TWO = (1.0, .3, .5), (1.0, .47, .5), (1.45, .45, .5), (1.1, .3, .42), (1.0, .45, .5)
RB_SIDE, RB_TIGHT = (1.0, .4, .55), (1.6, .4, .55)
B_BACK, B_BEAMS, B_HANDS = (1.0, .5, .5), (1.0, .5, .4), (1.1, .5, .6)
TRIP3 = [("r1", 40.0, RA_FRONT), ("d", 8.0, D_MID), ("r2", 36.0, RB_SIDE)]          # b2b in one frame: ray / iam / ray
E = [(G(-19), "sky_p", None, 0, None, "", "AUSTIN: the city at night, in the breakdown (3 beats)"),
     (G(-16), "eyes", None, 0, None, "", "THE 3x EYES, one band every 1.5 beats, AFTERIMAGE 001 under them"),
     (G(-11), "shot", "a", 0.5, FULL, "in_iam", "INTRODUCING IAMARIOLOGY (3 beats)"),
     (G(-8), "shot", "r1", 6.0, RA_FRONT, "in_ray", "B2B RAYMIXES (3 beats)"),
     (G(-5), "eye", "d", 0.0, D_EYE, "", "the neon eye sign tilts down to him (2 beats)"),
     (G(-3), "silence", None, 0, None, "", "the real silence before the drop: AFTERIMAGE burns in"),
     (G(0), "shot", "c", 19.2, FULL, "drop", "DROP 82.2 s: the room, sparklers up (3 beats)"),
     (G(3), "shot", "r2", 15.0, RB_SIDE, "", "burst: raymixes from the side"),
     (G(4), "shot", "a", 1.85, FULL, "", "burst: iamariology jumps"),
     (G(5), "shot", "r1", 12.0, RA_TIGHT, "zin", "burst: raymixes, tight"),
     (G(6), "shot", "b", 10.0, B_BEAMS, "", "burst: the beams open over the crowd"),
     (G(7), "shot", "e", 0.0, E_FR, "", "iamariology at the decks, front (2 beats)"),
     (G(9), "shot", "r1", 0.0, RA_SIDE, "", "raymixes past the speaker stack (2 beats)"),
     (G(11), "shot", "a", 4.6, FULL, "", "the camera turns to the crowd (3 beats)"),
     (G(14), "shot", "r1", 24.0, RA_LOW, "xerox", "raymixes from below, 1-bit flash (2 beats)"),
     (G(16), "trip3", None, 0, None, "", "the eye triptych: raymixes / iamariology / raymixes (4 beats, one bar)"),
     (G(20), "stack", "d", 5.05, D_MID, "", "IAMARIOLOGY on the bar line (2 beats)"),
     (G(22), "stack_ray", "r1", 36.0, RA_TWO, "", "RAYMIXES, the other half (2 beats)"),
     (G(24), "shot", "r2", 30.0, RB_TIGHT, "zin", "raymixes, hands tight (2 beats)"),
     (G(26), "shot", "a", 7.5, FULL, "", "iamariology, masked, fist up (2 beats)"),
     (G(28), "shot", "c", 39.5, FULL, "", "sparklers up close (2 beats)"),
     (G(30), "point", "hero", 0, E_FR, "", "iamariology's moment: the point to camera, step-printed, freeze (3 beats)"),
     (G(33), "shot", "r1", 44.0, RA_TIGHT, "zin", "raymixes' moment: tight punch-in (3 beats)"),
     (G(36), "shot", "c", 45.85, FULL, "", "the room and the screen (4 beats, into the music edit)"),
     (G(68), "silence_eye", None, 0, None, "", "pre-chorus: the 3x eyes, then their afterimage (4 beats)"),
     (CHORUS, "finale", "c", 48.95, FULL, "", "THE HIT 112.6 s: the room pours in through the eyes, both names"),
     (G(76), "devil", None, 0, None, "", "Devil's Night with AFTERIMAGE 001"), (G(78), "fomo", None, 0, None, "", "FOMO: invite only, numbered passes, RSVP"), (G(80), "mark", None, 0, None, "", "")]
E.sort(key=lambda e: out_of(e[0]))
used = {}
for t0, kind, src, st, fr, fx, why in E:                                  # guard: no source moment twice
    if (src in PL or src in ("r1", "r2", "c")) and st is not None:
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
    if shake: z = max(z, 1.07)                                    # safety zoom: the shake never shows the plate edge
    if shake:
        for h in KICKS:
            if h <= out_f < h + 10:
                dx, dy, r = mfx.shake(out_f, h, amp=8, seed=int(h)); sx += dx; sy += dy; rot += r
    if src == "c": arr, i = Cp, int((st - 7.5) * FPS + ti)
    elif src in ("r1", "r2"): arr, i = rwin(src, st), int(ti)
    else: arr, i = PL[src], int(st * FPS + ti)
    i = int(min(len(arr) - 1, max(0, i))); fr_ = arr[i]
    if src in GAIN: fr_ = np.clip(fr_.astype(np.float32) * GAIN[src][i], 0, 255).astype(np.uint8)
    return mfx.cover(fr_, z, sx, sy, rot, cx=cx, cy=cy)
EXPO = {}
def expo(key, fn):
    if key not in EXPO:
        EXPO[key] = float(np.clip(0.33 / max(np.median([float(np.percentile(fn(j), 60)) for j in (0, 4, 8)]), .02), .6, 2.0))
    return EXPO[key]

def fresh_state():
    global echo, nerv, thr, LG, prev
    echo = mfx.Echo((H, W)); nerv = mfx.Nervous(16, seed=6); thr = mfx.Threshold(); LG = {}; prev = np.zeros((H, W), np.float32)
fresh_state()

def render_frame(f):
    global prev
    rng = np.random.default_rng(f)
    ot = f / FPS; ga = .05
    first = out_of(E[0][0])
    if ot < first:
        rgb = STF(min(87, f + 46)); ga = 0
        if first - ot < .1: rgb = mfx.zoom_blur(rgb, .3)
        return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    ei = max(i for i, e in enumerate(E) if out_of(e[0]) <= ot + 1e-6); t0, kind, src, st, fr, fx, _ = E[ei]
    t1 = out_of(E[ei + 1][0]) if ei + 1 < len(E) else N / FPS; ti = f - out_of(t0) * FPS; L = (t1 - out_of(t0)) * FPS; q = min(1, ti / max(L, 1))
    if kind == "drake":
        g = look(mfx.cover(SLOW_IN[int(min(len(SLOW_IN) - 1, ti * 1.25))], 1.6 * (1 + .1 * q), cx=.5, cy=.43), 1.2)
        g = LG.setdefault("in", mfx.LightGraffiti())(g, thr=.82, diff=.16, decay=.9, gain=.4)
        g = mfx.fog_glow(mfx.streaks(g * .85, 2, 0, thr=.72, k=.8), .5, .35); g = echo(g, .8, .45)
        rgb = g3(mfx.letterbox(mfx.vignette(mfx.promist(g, .4), .35), 560 + 200 * mfx.ease_io(q)))
        if ti > 8: cc, aa = KICK; aa = (aa * min(1, (ti - 8) / 10))[..., None]; rgb = rgb * (1 - aa) + cc * aa
    elif kind == "sky_v":                                       # Drake/OVO: the city, letterboxed, lights glinting
        g = look(mfx.cover(SKY_V[int(min(len(SKY_V) - 1, ti))], 1.05 * (1 + .04 * q), cx=.5, cy=.5), .62)
        g = mfx.fog_glow(mfx.streaks(g, 2, 0, thr=.85, k=.4), .5, .2); g = echo(g, .7, .3)
        rgb = g3(mfx.letterbox(mfx.vignette(mfx.promist(g, .25), .35), 700))
        cc, aa = KICK; aa = (aa * min(1, ti / 8))[..., None]; rgb = rgb * (1 - aa) + cc * aa
    elif kind == "sky_p":                                       # the night photo: slow push and drift across the lights
        g = mfx.cover(SKY_P8, 1.35 + .1 * q, -60 + 120 * mfx.ease_io(q), 0, cx=.5, cy=.5)
        g = look(g, .8); g = mfx.fog_glow(mfx.streaks(g, 4, 45, thr=.85, k=.35), .5, .2); g = echo(g, .7, .3)
        rgb = g3(mfx.letterbox(mfx.vignette(mfx.promist(g, .25), .35), 700))
        cc, aa = KICK; rgb = rgb * (1 - aa[..., None]) + cc * aa[..., None]
        if L - ti < 4: rgb = mfx.zoom_blur(rgb, .3 * (1 - (L - ti) / 4))
    elif kind == "stack_ray":                                   # RAYMIXES stack over his own stage, scrolling the other way
        bg = look(mfx.cover(rwin(src, st)[int(min(len(rwin(src, st)) - 1, ti))], fr[0], cx=fr[1], cy=fr[2])) * .25
        s_ = mfx.shift(STK_RAY, 0, ti * 12); s_ = mfx.liquid(s_, 14 * (1 - mfx.ease_out(ti / 4)), f) if ti < 6 else s_
        g = mfx.bulge(np.maximum(bg, s_), .25 * env(f), .6); prev = g
        rgb = hud(g3(g), f)
    elif kind == "eyes":                                        # the 3x eyes: one band per beat, each lands with a ghost
        beat = 1.5 * SB * FPS; g = np.zeros((H, W), np.float32)
        if ti < 1: echo.reset()                                 # clean black: no city ghost under the eyes
        for b, (y0, y1) in enumerate(BANDS):
            if ti >= b * beat:
                k = min(1, (ti - b * beat) / 3); g[y0:y1] = EYES[y0:y1] * k
        g = look(g, 1.0) * (EYES > 0); g = mfx.fog_glow(g, .5, .35); g = echo(g, .8, .45); prev = g
        rgb = g3(mfx.vignette(mfx.promist(g, .3), .3))
        if ti >= 2.3 * beat: cc, aa = AFTK; aa = (aa * min(1, (ti - 2.3 * beat) / 4))[..., None]; rgb = rgb * (1 - aa) + cc * aa
        rgb = hud(rgb, f)
    elif kind == "trip":                                        # footage in the eye-triptych bands, locked frame
        arr = rwin(src, st)
        fr3 = [look(mfx.cover(arr[int(min(len(arr) - 1, ti + j * 14))], fr[0], cx=fr[1], cy=fr[2])) for j in range(3)]
        g = mfx.triptych(fr3, gap=8); g = echo(g, .7, .35); prev = g
        rgb = tag(hud(g3(mfx.vignette(mfx.promist(g, .28), .3)), f), src)
    elif kind == "trip3":                                       # three different angles in the eye bands
        fr3 = []
        for s3, st3, fr_ in TRIP3:
            arr = rwin(s3, st3) if s3 in ("r1", "r2") else PL[s3]; j = int(ti) if s3 in ("r1", "r2") else int(st3 * FPS + ti)
            fr3.append(look(mfx.cover(arr[int(min(len(arr) - 1, j))], fr_[0], cx=fr_[1], cy=fr_[2])))
        g = mfx.triptych(fr3, gap=8); g = echo(g, .7, .35); prev = g
        rgb = hud(g3(mfx.vignette(mfx.promist(g, .28), .3)), f)
    elif kind == "fomo":
        cc, aa = FOMO; rgb = cc * (aa * min(1, ti / 3))[..., None]; ga = .03
    elif kind == "eye":
        qq = mfx.ease_io(q); g = look(mfx.cover(PL["d"][int(min(len(PL["d"]) - 1, st * FPS + ti))], 2.2 - 1.1 * qq, cx=.5, cy=.23 + .22 * qq))
        g = mfx.fog_glow(mfx.streaks(g, 2, 0, thr=.8, k=.7), .5, .45)
        if ti < 5: g = mfx.zoom_blur(g, .3 * (1 - ti / 5))
        g = echo(g, .6, .3); rgb = hud(g3(mfx.vignette(mfx.promist(g, .3), .3)), f)
    elif kind in ("shot", "finale", "stack"):
        drift = (-.05 if fr[0] > 1.2 else .05)
        fn = lambda tt: frame_of(src, st, tt, ti - (f - tt), fr, drift * min(1, (ti - (f - tt)) / max(L, 1)), shake=out_of(t0) >= out_of(B[0]))
        k_ = expo((t0, src), lambda j, f0=f - ti: frame_of(src, st, f0 + j, j, fr))   # always metered on the shot's first frames
        g_raw = fn(f) if src == "a" else (mfx.mblur(fn, f, .5, 3) if ti < 5 or out_of(t0) >= out_of(B[0]) else fn(f))   # 320 px clip: blending smears it
        if src in ("a", "c"):                                  # exposure limiter: phone flash frames and sparklers blow out
            m_ = float(np.percentile(g_raw, 60)) * k_
            cap = .42 if src == "a" else .36
            if m_ > cap: g_raw = g_raw * (cap / m_)
        g = look(g_raw, k_)
        if src == "c": g = np.where(g > .72, .72 + (g - .72) * .42, g)       # film-style highlight roll-off on sparklers
        if src == "a": ga = .09                                    # real grain over the phone clip, not a smooth upscale
        if src == "c": g = LG.setdefault(t0, mfx.LightGraffiti())(g, thr=.8, diff=.16, decay=.8, gain=.2)
        kk = (.6 if fx == "drop" or kind == "finale" else .32) * math.exp(-ti / 4) + .1     # lens punch only on the hit
        g = mfx.fisheye(g, kk); g = mfx.bulge(g, (.32 if out_of(t0) >= out_of(B[0]) else .2) * env(f), .55)
        if src == "c": g = mfx.streaks(g, 4, 45, thr=.86, k=.4)
        if src == "b": g = mfx.astig(g, .3 * env(f, 6), thr=.72)
        if fx == "zin" and ti < 4: g = mfx.zoom_blur(g, .15 * (1 - ti / 4))
        if fx == "xerox" and ti < 2: g = thr(g)
        if fx == "melt" and ti < 6: g = mfx.liquid(g, 130 * (1 - ti / 6), f)
        if ei + 1 < len(E) and E[ei + 1][5] == "melt" and (t1 - ot) * FPS < 5: g = mfx.liquid(g, 130 * (1 - (t1 - ot) * FPS / 5), f)
        if fx == "stutter" and L - ti < BEAT * FPS: g = nerv(g, hit=int(ti) % 9 == 0)   # stutter in the last beat
        em = .18 if src in ("a", "c") else .3
        g = echo(g, .62, em if ti < 7 else em * .55); prev = g          # the afterimage trail, stronger
        if kind == "stack":
            s_ = mfx.shift(STK, 0, -ti * 12); s_ = mfx.liquid(s_, 14 * (1 - mfx.ease_out(ti / 4)), f) if ti < 6 else s_
            g = np.maximum(g * .25, s_)
        rgb = g3(mfx.vignette(mfx.promist(g, .28), .3)) if kind != "stack" else g3(g)
        if kind == "finale" and ti < 18:                           # eyes matte: the room flows in through the 3x eyes, brightest first
            p_ = mfx.ease_io(ti / 18); m = np.clip((EYES - (1 - 1.1 * p_)) / .14, 0, 1)
            m = np.maximum(m, p_ ** 3)[..., None]; eyes_ = g3(look(EYES, 1.0) * (EYES > 0) * (.55 - .35 * p_))
            rgb = rgb * m + eyes_ * (1 - m)                            # the eyes hold, the room pours in through them
        if kind == "finale":
            cc, aa = ANN; k2 = float(np.clip((ti - 12) / 5, 0, 1)); band = np.clip(1 - np.abs(np.arange(H) - 960) / 420, 0, 1)[:, None, None] * .6 * k2
            rgb = rgb * (1 - band); rgb = rgb * (1 - aa[..., None] * k2) + cc * aa[..., None] * k2
        if fx in INTRO:
            cc, aa = INTRO[fx]; k2 = min(1, ti / 3); band = np.clip(1 - np.abs(np.arange(H) - 1390) / 260, 0, 1)[:, None, None] * .55 * k2
            rgb = rgb * (1 - band); rgb = rgb * (1 - aa[..., None] * k2) + cc * aa[..., None] * k2
        rgb = hud(rgb, f)
        if fx not in INTRO and kind != "stack": rgb = tag(rgb, src)
    elif kind == "silence":
        g = prev * max(0, 1 - q * 4) ** 1.5                       # the last frame dies, then AFTERIMAGE burns in
        w_ = AFTW[1] * (min(1, q / .25) if q < .55 else max(0, 1 - (q - .55) / .15))
        g = echo(np.maximum(g, w_), .8, .5); prev = g; rgb = g3(g)
        if 0 <= L - ti < 5: rgb = mfx.screen(rgb, LOGO * (.35 if int(f) % 2 else .12))
        rgb = hud(rgb, f)
    elif kind == "silence_eye":
        if ti < 6: g = look(EYES, 1.0) * (EYES > 0)                # the eyes, 6 frames
        else: g = (1 - EYES) * (EYES > 0) * .55 * math.exp(-(ti - 6) / 40)   # their negative afterimage, fading
        g = mfx.fog_glow(g, .5, .35); prev = g; rgb = g3(mfx.vignette(g, .4))
        if ti >= 6: cc, aa = AFTK; aa = (aa * min(1, (ti - 6) / 4))[..., None]; rgb = rgb * (1 - aa) + cc * aa
        if 0 <= L - ti < 5: rgb = mfx.screen(rgb, LOGO * (.35 if int(f) % 2 else .12))
        rgb = hud(rgb, f, .6)
    elif kind == "point":
        p = min(1, q / .5); idx = int(21 * (1 - (1 - p) ** 2.2)) if p < 1 else 21
        g = look(mfx.cover(HERO[idx], 1.12, cx=.47, cy=.42)); g = mfx.fisheye(g, .3 + .4 * math.exp(-ti / 5))
        if p >= 1:
            m = ti - .5 * L; g = np.clip((g - .5) * (1 + .25 * min(1, m / 3)) + .5, 0, 1)
            if m < 4: g = mfx.flash(g, m / 4, .4)
        g = echo(g, .82, .4); prev = g; rgb = g3(mfx.vignette(mfx.promist(g, .3), .3))
        rgb = tag(hud(rgb, f), "hero")
    elif kind == "devil":
        z = 1.0; cc, aa = DEVIL2
        aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR))
        rgb = cc * (aa * min(1, ti / 4))[..., None]; ga = .03
    else:
        rgb = STF(int(min(70, 50 + ti))); ga = .02                      # end on the full lockup, held
    if ga: rgb = mfx.grain(rgb, ga, rng=rng)
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)

# ---------------------------------------------------------------- engine: per-shot pieces, cache, parallel
SRC = open(os.path.abspath(__file__)).read()
CODE = hashlib.md5((SRC[:SRC.index("E = [")] + SRC[SRC.index("E.sort("):] + open(mfx.__file__).read()).encode()).hexdigest()[:10]
STARTS = [0] + [int(math.ceil(out_of(e[0]) * FPS - 1e-6)) for e in E]
SEGS = [(STARTS[k], STARTS[k + 1] if k + 1 < len(STARTS) else N) for k in range(len(STARTS))]
SEGS = [(a, b) for a, b in SEGS if b > a]
MODE = "draft" if DRAFT else "final"
CACHE = os.path.join(os.path.dirname(os.path.abspath(OUT)), ".shots_" + os.path.splitext(os.path.basename(OUT))[0].replace("_DRAFT", ""), MODE)
os.makedirs(CACHE, exist_ok=True)
def seg_key(k):
    a, b = SEGS[k]; ei = next((i for i, e in enumerate(E) if STARTS[i + 1] == a), -1); pe = E[ei - 1] if ei > 0 else None
    return hashlib.md5(repr((CODE, MODE, a, b, E[ei] if ei >= 0 else "sting", pe)).encode()).hexdigest()[:12]
def seg_path(k): return os.path.join(CACHE, f"{k:03d}_{seg_key(k)}.mp4")
def render_seg(k):
    a, b = SEGS[k]; fresh_state()
    for f in range(max(0, a - 8), a): render_frame(f)              # warm-up: trails and the silence pick up the shot before
    step = 2 if DRAFT else 1
    vf = ["-vf", "scale=540:960:flags=area"] if DRAFT else []
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", *vf,
                            "-c:v", "libx264", "-preset", "ultrafast" if DRAFT else "veryfast", "-crf", "20" if DRAFT else "10",
                            "-pix_fmt", "yuv420p", seg_path(k) + ".tmp.mp4"], stdin=subprocess.PIPE)
    last = None
    for f in range(a, b):
        if (f - a) % step == 0: last = render_frame(f).tobytes()
        enc.stdin.write(last)
    enc.stdin.close(); enc.wait(); os.replace(seg_path(k) + ".tmp.mp4", seg_path(k)); return k

if __name__ == "__main__":
    t_start = time.time()
    for e in E:                                                      # load every raymixes window before forking
        if e[2] in ("r1", "r2"): rwin(e[2], e[3])
    for s3, st3, _ in TRIP3:
        if s3 in ("r1", "r2"): rwin(s3, st3)
    keep = {os.path.basename(seg_path(k)) for k in range(len(SEGS))}
    for fn in os.listdir(CACHE):
        if fn not in keep: os.remove(os.path.join(CACHE, fn))       # drop pieces from old versions of the edit
    todo = [k for k in range(len(SEGS)) if not os.path.exists(seg_path(k))]
    todo.sort(key=lambda k: SEGS[k][0] - SEGS[k][1])                # longest first
    print(f"{MODE}: {len(SEGS) - len(todo)} shots cached, {len(todo)} to render on {JOBS} cores", flush=True)
    if todo:
        with mp.get_context("fork").Pool(min(JOBS, len(todo))) as pool:
            for k in pool.imap_unordered(render_seg, todo): print("  shot", k, "done", flush=True)
    lst = os.path.join(CACHE, "list.txt")
    with open(lst, "w") as fh: fh.writelines(f"file '{seg_path(k)}'\n" for k in range(len(SEGS)))
    af = (f"[1:a]atrim={SEG1[0]:.3f}:{SEG1[1]:.3f},asetpts=PTS-STARTPTS[s1];[1:a]atrim={SEG2[0]:.3f}:{SEG2[1]:.3f},asetpts=PTS-STARTPTS[s2];"
          f"[s1][s2]acrossfade=d=0.008:c1=tri:c2=tri,highpass=f=30,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.3,afade=t=out:st={N / FPS - 0.6:.2f}:d=0.6[a]")
    venc = ["-c:v", "copy"] if DRAFT else ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-maxrate", "20M", "-bufsize", "40M", "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-g", "30"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", SONG, "-filter_complex", af,
                    "-map", "0:v", "-map", "[a]", "-t", f"{N / FPS:.3f}", *venc, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
    with open(os.path.splitext(OUT)[0] + "_cutlist.md", "w") as fh:
        fh.write("| Time | Shot | Source moment | Why |\n|---|---|---|---|\n")
        for t0, kind, src, st, fr, fx, why in E:
            fh.write(f"| {out_of(t0):.2f} s | {kind} | {src or '-'} {'' if st is None else f'@ {st:.2f} s'} | {why} |\n")
    print("done", N, round(N / FPS, 1), "s", f"in {time.time() - t_start:.0f} s")
