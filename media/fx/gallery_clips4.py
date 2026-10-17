"""Gallery clips, batch 4: effects written from studying open-source tools (frei0r, Blender, FFmpeg, G'MIC, openfx-misc).
usage: python3 gallery_clips4.py <video_dir> <t5_dir> <out_dir>"""
import sys, os, subprocess, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfx
from mfx import W, H

VID, T5, OUT = sys.argv[1:4]
C = mfx.plate(f"{VID}/c.mov", 26.5, 30.0); A = mfx.plate(mfx.stabilize(f"{VID}/a.mov"), deflicker=True); B = mfx.plate(f"{VID}/b.mov")
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
fin = lambda g, r: np.clip(mfx.grain(mfx.vignette(g, .3), .04, rng=r), 0, 1)
fc = lambda t, z=1.3: look(mfx.cover(C[int(min(len(C) - 1, t))], z, cy=.45), 1.3)
fa = lambda t: look(mfx.cover(A[int(min(len(A) - 1, 30 + t))], 1.04))
fb = lambda t: look(mfx.cover(B[int(min(len(B) - 1, 280 + t))], 1.04), 1.4)
IAM = np.asarray(Image.open(f"{T5}/P_iam.png").convert("RGBA")).astype(np.float32)[..., 3] / 255
g3 = lambda g: np.repeat(g[..., None], 3, 2)
ST = {}
def st(k, cls): return ST.setdefault(k, cls())

def e_lg(f, r): return g3(fin(st("lg", mfx.LightGraffiti)(fc(f)), r))
def e_streaks(f, r): return g3(fin(np.clip(mfx.streaks(fc(f), 4, 45, thr=.78, k=.9 if (f // 30) % 2 else 0), 0, 1), r))
def e_anamorphic(f, r): return g3(fin(np.clip(mfx.streaks(fc(f), 2, 0, thr=.75, k=1.0), 0, 1), r))
def e_fog(f, r): return g3(fin(np.clip(mfx.fog_glow(fc(f), .6, .9 if (f // 30) % 2 else 0), 0, 1), r))
def e_vertigo(f, r): return g3(fin(np.clip(st("v", mfx.Vertigo)(fa(f), 1.035, .8), 0, 1), r))
def e_nervous(f, r): return g3(fin(st("n", mfx.Nervous)(fc(f), hit=f % 7 == 0), r))
def e_slit(f, r): return g3(fin(st("s", mfx.SlitScan)(fa(f), "rings"), r))
def e_thr(f, r): return g3(st("t", mfx.Threshold)(fb(f)) if (f // 15) % 2 else fin(fb(f), r))
def e_thr3(f, r): return g3(mfx.Threshold()(fa(f), 3))
def e_kuwa(f, r): return g3(fin(mfx.kuwahara(fa(f), 6), r))
def e_kal(f, r): return g3(fin(mfx.kaleidoscope(fc(f), 6, rot=f * 2), r))
def e_wires(f, r): return g3(st("w", mfx.Wires)(fa(f)))
def e_dissolve(f, r): return g3(fin(mfx.noise_dissolve(fa(f), fc(f), mfx.clamp01((f - 15) / 30), block=6), r))
def e_wind(f, r): return g3(fin(mfx.wind_wipe(fa(f), fc(f), mfx.ease_io((f - 15) / 30)), r))
def e_hblur(f, r): return g3(fin(mfx.hblur_transition(fa(f), fc(f), mfx.clamp01((f - 18) / 24)), r))
def e_pix(f, r): return g3(fin(mfx.pixelize_transition(fa(f), fc(f), mfx.clamp01((f - 15) / 30)), r))
def e_squig(f, r): return g3(mfx.squiggle(IAM, f, 2.0))
def e_chrome(f, r):
    m = IAM; c = mfx.chrome(m, angle=135 + 40 * math.sin(f / 10))
    return np.clip(mfx.duotone(c) * m[..., None], 0, 1)

EFFECTS = [
    ("light_graffiti", "Light graffiti", "frei0r lightgraffiti (method)", "Only bright moving lights paint into a layer that persists. Sparklers and phones become light trails.", "on", e_lg),
    ("streaks", "Star glare", "Blender Glare: Streaks (method)", "Star-filter lines off the brightest points. Toggles every second.", "on", e_streaks),
    ("anamorphic", "Anamorphic streak", "Blender Glare: Streaks, 2 lines", "Horizontal lens streaks off lights. The Drake / OVO night look.", "on", e_anamorphic),
    ("fog_glow", "Fog glow", "Blender Glare: Fog Glow (Spencer 1995 kernel)", "A physically based halo around lights, like your eye's own glare. Toggles.", "on", e_fog),
    ("vertigo", "Vertigo tunnel", "frei0r vertigo (method)", "Each frame feeds back into itself, zoomed and turned. A dizzy tunnel.", "careful", e_vertigo),
    ("nervous", "Nervous stutter", "frei0r nervous (method)", "Short runs back and forth through the last second. The Carti stutter.", "on", e_nervous),
    ("slit_scan", "Slit-scan rings", "frei0r delaygrab / openfx SlitScan (method)", "The centre is now, the edges are the past, so motion ripples outward.", "careful", e_slit),
    ("threshold", "1-bit xerox", "frei0r twolay0r (method)", "Pure black and white, the cut point adapts every frame. Flash frames.", "on", e_thr),
    ("threshold3", "3-tone poster", "frei0r threelay0r (method)", "Black, grey, white at fixed percentiles. Screen-print look.", "careful", e_thr3),
    ("kuwahara", "Kuwahara paint", "Blender Kuwahara (method)", "Painterly flattening that keeps edges. A still, art-print moment.", "careful", e_kuwa),
    ("kaleidoscope", "Kaleidoscope", "frei0r kaleid0sc0pe (idea)", "Six-fold mirror of the sparklers. One hit on a break.", "careful", e_kal),
    ("wires", "Neon wires", "FFmpeg edgedetect + lagfun (idea)", "Edges draw thin lines that hang behind the motion.", "careful", e_wires),
    ("noise_dissolve", "Digital dissolve", "FFmpeg xfade: dissolve (method)", "Random chunky blocks swap A for B.", "on", e_dissolve),
    ("wind_wipe", "Wind wipe", "FFmpeg xfade: hlwind (method)", "A wipe whose edge tears row by row.", "on", e_wind),
    ("hblur_whip", "Smear-through", "FFmpeg xfade: hblur (method)", "Both shots smear sideways and swap at the peak. A whip without motion.", "on", e_hblur),
    ("pixelize", "Pixelize", "FFmpeg xfade: pixelize (method)", "Blocks grow to a peak, the shots cross underneath.", "careful", e_pix),
    ("squiggle", "Boiling type", "frei0r squigglevision (idea)", "The letters wobble frame to frame like hand-drawn animation.", "on", e_squig),
    ("chrome", "Chrome type", "frei0r emboss + metal ramp (idea)", "Lit relief mapped to a steel ramp, toned steel blue. Y2K chrome, in our palette.", "on", e_chrome),
]
meta = []
for key, name, plugin, note, tag, fn in EFFECTS:
    rng = np.random.default_rng(7); ST.clear()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-vf", "scale=360:640:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", "-an", f"{OUT}/{key}.mp4"], stdin=subprocess.PIPE)
    for f in range(60): enc.stdin.write((np.clip(fn(f, rng), 0, 1) * 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.3", "-i", f"{OUT}/{key}.mp4", "-frames:v", "1", "-q:v", "6", f"{OUT}/{key}.jpg"])
    meta.append({"key": key, "name": name, "plugin": plugin, "note": note, "tag": tag}); print("done", key, flush=True)
json.dump(meta, open(f"{OUT}/effects4.json", "w"), indent=1)
