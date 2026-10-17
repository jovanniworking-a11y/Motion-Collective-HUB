"""MOTION teaser v4: hype cut with a reason for every edit (see CUTS: each shot carries its 'why').

Grid: 127.1 bpm, beat b at frame 3.6 + 14.165*b. Bars start on beats 3, 7, 11, 15, 19 (drop), 23, 27, 31.
Structure (tension -> release):
  b0-6    the sting: the mark flies in; its fly-through exit becomes the zoom transition into the footage
  b6-14   build: 2-beat then 1-beat cuts, letterbox opening wider on each, cut on action / graphic match
  b14-17  the name, one word per beat, footage moving inside the letters
  b17-18  stutter: half-beat alternations, the cut density peaks
  b18-19  one beat of black (the dip in the track), two logo ghost ticks
  b19-27  drop: hero image on the drop frame with impact shake + flash, cuts every beat with shakes on the kicks,
          one zoom-through on the bar line (b23), one speed-ramped hero shot (b25-27, optical-flow slow motion)
  b27-35  whip into black, the eyes open on half-beats, name, date, the mark (light sweep), fly-through to black
Look: denoised plates, film curve with highlight roll-off, Black Pro-Mist diffusion, fine film grain over everything,
real sub-frame motion blur on every camera move. Monochrome; red only in MMMM and B2B.

usage: python3 teaser4.py <video_dir> <sting_frames_dir> <eyes.png> <out.mp4>
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
kf = lambda b: 3.6 + SPB * b                      # beat -> exact frame (no per-beat rounding drift)
k = lambda b: int(round(kf(b)))
rng = np.random.default_rng(30)

A = mfx.plate(f"{VID}/a.mov", deflicker=True); B = mfx.plate(f"{VID}/b.mov")
SLOW = mfx.plate(f"{VID}/a.mov", 2.55, 3.45, fps=90, interp=True, deflicker=True)   # 3x optical-flow frames for the hero ramp
PL = {"a": A, "b": B}

def rgba(path):
    a = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32) / 255
    return a[..., :3], a[..., 3]
WD = {n: rgba(f"{D}/W_{n}.png") for n in ("iamH", "rayH", "b2b", "endname", "enddate")}
NAME = rgba(f"{VID}/card_name.png")
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
_e = Image.open(EYES).convert("L"); _e = _e.resize((840, int(840 * _e.height / _e.width)), Image.LANCZOS)
EY = np.zeros((H, W), np.float32); EY[240:240 + _e.height, 120:960] = np.asarray(_e).astype(np.float32) / 255
sc = 840 / 1080
EYE_BANDS = [(240, 240 + int(437 * sc)), (240 + int(444 * sc), 240 + int(913 * sc)), (240 + int(922 * sc), 240 + _e.height)]

# ---- the cut list: (start beat, source, source seconds or None = in sync with the track, camera, why)
# camera: (zoom start, zoom end, pan x px start, pan x end); letterbox height for the build
CUTS = [
    (6,    "b", None, (1.16, 1.04, 0, 0),   620,  "Out of the logo's fly-through: zoom-through lands on the widest, calmest shot (establish the room)."),
    (8,    "a", 0.95, (1.10, 1.02, -30, 30), 760, "Cut on action: the arm starts rising on the cut, motion hides the edit; frame opens wider."),
    (10,   "b", None, (1.05, 1.12, 0, 0),   900,  "Phrase line (bar 3): back to the booth, push in. Eye-trace stays centre."),
    (12,   "a", 2.05, (1.04, 1.10, 20, -20), 1080, "1-beat cuts start: density up. Hands up again = motion match with b8."),
    (13,   "b", None, (1.12, 1.04, 0, 0),   1080, "Kick on the 1: light flash in the source lands on the cut."),
    (14,   "word:iamH", None, None, None,   "Name, word 1 on the beat. Footage keeps moving inside the letters, so the energy carries."),
    (15,   "word:b2b", None, None, None,    "Word 2: the red accent alone on black, the only colour in the build."),
    (16,   "word:rayH", None, None, None,   "Word 3, then the cut density peaks."),
    (17,   "stutter", None, None, None,     "Half-beat alternations a/b: maximum tension in the last bar of the build."),
    (18,   "black", None, None, None,       "One beat of black in the track's dip: the silence makes the drop hit."),
    (19,   "b", None, (1.22, 1.0, 0, 0),    None, "DROP: best image on the drop frame (the room's own light hit), flash + impact shake, zoom settles."),
    (20,   "a", 1.55, (1.08, 1.0, 0, 0),    None, "Graphic match: the diagonal arm rhymes with the diagonal beams."),
    (21,   "b", None, (1.0, 1.08, 0, 0),    None, "Cut on the kick, beams on the beat (in-sync source)."),
    (22,   "a", 0.6, (1.06, 1.0, 0, 0),     None, "Short close shot between two wides: rhythm of scale."),
    (23,   "b", None, (1.0, 1.06, 0, 0),    None, "Bar line: the one designed transition in the drop, a zoom-through. Name lower third arrives."),
    (24,   "b", None, (1.06, 1.0, 0, 0),    None, "Hands in the air, keep the crowd energy."),
    (25,   "slow", None, (1.04, 1.12, 0, 0), None, "The hero moment: one speed ramp only (fast -> 1/3 speed), heavy afterimage. Luxury holds once."),
    (27,   "eyes", None, None, None,        "Whip into black, then the eyes open band by band on half-beats: the series signature."),
]
# speed ramp (Twixtor-style): real time for 4 frames, ease down to 1/3 speed over 6, hold (index into the 90 fps plate)
_sp = [3.0 if i < 4 else 3 - 2 * mfx.ease_io((i - 4) / 6) for i in range(40)]
RAMP = np.concatenate([[0], np.cumsum(_sp)])
HITS = [kf(b) for b in range(19, 27)]             # kicks in the drop get an impact shake
SH_AMP = {k(19): 26}
END_MARK = kf(31)                                  # the mark (sting hold with light sweep)
END_EXIT = kf(33.4)                                # the fly-through exit
N = int(16.70 * FPS)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{VID}/b.mov", "-map", "0:v", "-map", "1:a", "-t", f"{N / FPS:.3f}",
                        "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.05,afade=t=out:st={N / FPS - 0.6:.2f}:d=0.6",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", "14M", "-bufsize", "28M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

def look(g, gain=1.0): return mfx.film_curve(g * gain, black=0.13, gain=1.6, gamma=1.3)

EXPO = {}
def expo(c, f):
    """Per-shot exposure match: measure the shot once at its first frame, lift dark shots toward a common key.
    Constant within the shot, so the room's own light flashes still read."""
    key = c[0]
    if key not in EXPO:
        nb = next((x[0] for x in CUTS if x[0] > key), 35); L = kf(nb) - kf(key)
        ms = [float(np.percentile(shot_frame(c, f + j, j), 60)) for j in np.linspace(0, max(L - 1, 0), 6)]
        EXPO[key] = float(np.clip(0.33 / max(np.median(ms), 0.02), 0.6, 2.0))
    return EXPO[key]

def shot_frame(c, t, ti):
    """Footage frame for cut c at absolute frame t (float); ti = frames since the cut."""
    b0, src, ss, cam, box, _ = c
    nb = next((x[0] for x in CUTS if x[0] > b0), 35); L = kf(nb) - kf(b0)
    z0, z1, p0, p1 = cam
    q = mfx.ease_out(ti / max(L, 1), 2) if z0 > z1 else mfx.ease_io(ti / max(L, 1))
    if b0 == 19: q = mfx.expo_out(ti / 9)                                   # drop: the zoom settles fast
    z = z0 + (z1 - z0) * q; px = p0 + (p1 - p0) * q
    sx = sy = rot = 0.0
    for h in HITS:
        if h <= t < h + 12:
            dx, dy, r = mfx.shake(t, h, amp=SH_AMP.get(int(round(h)), 9), seed=int(h)); sx += dx; sy += dy; rot += r
    if src == "slow":                                                        # speed ramp: 1x for 4 frames, ease to 1/3x
        arr = SLOW; i = int(min(len(arr) - 1, RAMP[min(len(RAMP) - 1, int(ti))]))
    else:
        arr = PL[src]
        sec = (t / FPS) if ss is None else ss + ti / FPS
        i = int(min(len(arr) - 1, sec * FPS))
    return mfx.cover(arr[i], z, px + sx, sy, rot)

def footage(c, f, ti, moving):
    if moving:
        return mfx.mblur(lambda tt: shot_frame(c, tt, ti - (f - tt)), f, shutter=0.5, n=4)
    return shot_frame(c, f, ti)

def word_layer(name, m, lit):
    c, a = WD[name]
    s = 1 + 0.14 * (1 - mfx.expo_out(m / 7))                                 # word lands with a scale settle
    if s > 1.002:
        im = Image.fromarray(a); a = np.asarray(im.transform((W, H), Image.AFFINE, (1 / s, 0, W / 2 * (1 - 1 / s), 0, 1 / s, H / 2 * (1 - 1 / s)), resample=Image.BILINEAR))
    if name == "b2b": return np.repeat(a[..., None], 3, 2) * c                # solid red label
    return (np.clip(lit * 1.3 + 0.2, 0, 1) * a)[..., None] * np.ones(3)

echo = mfx.Echo((H, W))
for f in range(N):
    beat = (f - 3.6) / SPB
    ci = max(i for i, c in enumerate(CUTS) if kf(c[0]) <= f + 0.01) if f >= kf(6) - .01 else -1
    grain_amt, rgb = 0.05, None
    if ci < 0:                                                               # the sting
        sf = min(87, f)
        rgb = STF(sf); grain_amt = 0.0
        if f >= k(6) - 3:                                                    # the sting's fly-through hands over
            rgb = mfx.zoom_blur(rgb, 0.3)
    else:
        c = CUTS[ci]; b0, src = c[0], c[1]; ti = f - kf(b0)
        if src in ("a", "b", "slow"):
            moving = ti < 6 or b0 >= 19
            g = look(footage(c, f, ti, moving), expo(c, f))
            if b0 >= 19 and src != "slow": g = mfx.astig(g, 0.3 if ti < 5 else 0.15)
            if ci == 0 and ti < 6: g = mfx.zoom_blur(g, 0.3 * (1 - mfx.ease_out(ti / 6)))   # end of the zoom-through
            if b0 == 23 and ti < 4: g = mfx.zoom_blur(g, 0.35 * (1 - ti / 4))
            nxt = CUTS[ci + 1][0] if ci + 1 < len(CUTS) else 35
            if nxt == 23 and kf(23) - f < 4: g = mfx.zoom_blur(g, 0.35 * (1 - (kf(23) - f) / 4))
            mix = {True: .3}.get(b0 >= 19, .35); dec = .55
            if src == "slow": mix, dec = .55, .85
            g = echo(g, decay=dec, mix=mix if ti < 8 or src == "slow" else .2)
            if c[4]: g = mfx.letterbox(g, c[4])
            if b0 in (23, 24, 25) and f >= kf(23) + 2:                        # name lower third (protect legibility)
                m = f - (kf(23) + 2); band = np.clip((np.arange(H) - 1200) / 220, 0, 1)[:, None]
                g = g * (1 - 0.5 * band * min(1, m / 4))
            if b0 == 25 and kf(27) - f < 5:                                   # whip out of the hero shot
                g = mfx.whip(g, np.zeros_like(g), 0.5 * (1 - (kf(27) - f) / 5))
            rgb = np.repeat(mfx.vignette(g, .3)[..., None], 3, 2)
            if b0 in (23, 24, 25) and f >= kf(23) + 2:
                cc, aa = NAME; aa = (aa * min(1, (f - kf(23) - 2) / 4))[..., None]
                rgb = rgb * (1 - aa) + cc * aa
        elif src.startswith("word:"):
            name = src[5:]; m = ti
            lit = look(mfx.cover(B[int(min(len(B) - 1, f))], 1.06), 1.8)
            rgb = word_layer(name, m, lit)
            rgb = np.maximum(rgb, np.repeat(echo.buf[..., None], 3, 2) * 0.12)
            echo.buf *= 0.6
        elif src == "stutter":
            half = int(ti // (SPB / 2)); q = ti - half * SPB / 2
            cc = CUTS[1] if half % 2 == 0 else CUTS[4]
            g = look(shot_frame(cc, f, 3 + q), expo(cc, f))
            if q < 2: g = mfx.flash(g, q / 2, 0.35)
            g = echo(g, .5, .3)
            rgb = np.repeat(mfx.letterbox(mfx.vignette(g, .3), 1080)[..., None], 3, 2)
        elif src == "black":
            echo.buf *= 0.7; g = echo.buf * 0.5
            rgb = np.repeat(g[..., None], 3, 2)
            if kf(19) - f < 4 and int(f) % 2:                                 # two ghost ticks of the mark
                rgb = mfx.screen(rgb, np.clip((STF(66) - .05) / .95, 0, 1) * 0.16)
        elif src == "eyes":
            if f < END_MARK:
                canvas = np.zeros((H, W), np.float32)
                for i, (a0, a1) in enumerate(EYE_BANDS):
                    fb = kf(27.25) + i * SPB / 2
                    if f < fb: continue
                    m = f - fb; off = 34 * (1 - mfx.ease_out(m / 6))
                    band = np.zeros_like(canvas); band[a0:a1] = EY[a0:a1]
                    if off > .5: band = np.maximum(mfx.shift(band, -off), mfx.shift(band, off)) * 0.8
                    canvas = np.maximum(canvas, band * min(1, .35 + m / 4))
                z = 1 + 0.04 * (f - kf(27)) / (END_MARK - kf(27))
                canvas = np.asarray(Image.fromarray(canvas).transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR))
                canvas = mfx.promist(canvas, .3)
                rgb = np.repeat(canvas[..., None], 3, 2)
                for key, fb in (("endname", kf(29)), ("enddate", kf(30))):
                    if f >= fb:
                        cc, aa = WD[key]; aa = (aa * min(1, (f - fb) / 4))[..., None]; rgb = rgb * (1 - aa) + cc * aa
                if f - kf(27) < 3: rgb = rgb * ((f - kf(27)) / 3)
            elif f < END_EXIT:                                                # the mark: sting frames with the light sweep
                rgb = STF(int(min(70, 40 + (f - END_MARK))))
            else:
                rgb = STF(int(min(89, 74 + (f - END_EXIT))))
            grain_amt = 0.03
    rgb = mfx.grain(rgb, grain_amt, rng=rng) if grain_amt else rgb
    enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes())
    if f % 60 == 0: print("frame", f, "/", N, flush=True)
enc.stdin.close(); enc.wait()
with open(os.path.splitext(OUT)[0] + "_cutlist.md", "w") as fh:
    fh.write("| Beat | Time | Shot | Why this cut |\n|---|---|---|---|\n")
    for c in CUTS:
        fh.write(f"| {c[0]} | {kf(c[0]) / FPS:.2f} s | {c[1] if c[1] not in ('a', 'b') else 'clip ' + c[1]} | {c[5]} |\n")
print("done", N)
