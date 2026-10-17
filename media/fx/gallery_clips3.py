"""Gallery clips, batch 3: the pop-culture effects (fisheye, bulge, twirl, liquid warp, type stack, HUD, stabilize).
usage: python3 gallery_clips3.py <video_dir> <t5_dir> <out_dir>"""
import sys, os, subprocess, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfx
from mfx import W, H

VID, T5, OUT = sys.argv[1:4]
A = mfx.plate(mfx.stabilize(f"{VID}/a.mov"), deflicker=True); AR = mfx.plate(f"{VID}/a.mov", deflicker=True); B = mfx.plate(f"{VID}/b.mov")
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
fin = lambda g, r: np.clip(mfx.grain(mfx.vignette(mfx.promist(g, .28), .3), .045, rng=r), 0, 1)
fa = lambda t: look(mfx.cover(A[int(min(len(A) - 1, 30 + t))], 1.04))
fb = lambda t: look(mfx.cover(B[int(min(len(B) - 1, 280 + t))], 1.04), 1.4)
IAM = np.asarray(Image.open(f"{T5}/P_iam.png").convert("RGBA")).astype(np.float32)[..., 3] / 255
STK = mfx.stack(IAM, 9, .55)
hud = np.asarray(Image.open(f"{T5}/P_hud.png").convert("RGBA")).astype(np.float32) / 255
g3 = lambda g: np.repeat(g[..., None], 3, 2)
kick = lambda f: math.exp(-(f % 14) / 4)

def e_fisheye(f, r): return g3(fin(mfx.fisheye(fa(f), .85 * math.exp(-(f % 30) / 5) + .15), r))
def e_bulge(f, r): return g3(fin(mfx.bulge(fb(f), .4 * kick(f), .55), r))
def e_twirl(f, r): q = mfx.clamp01((f - 15) / 30); return g3(fin(mfx.twirl(fa(f), 3 * math.sin(math.pi * q) ** 2, .7), r))
def e_liquid(f, r):
    p = mfx.clamp01((f - 15) / 30); return g3(fin(mfx.warp_transition(fa(f), fb(f), p, 140), r))
def e_stack(f, r): return g3(np.maximum(fb(f) * .28, mfx.shift(STK, 0, -f * 9)))
def e_hud(f, r):
    g = g3(fin(fa(f), r)); c, a = hud[..., :3], hud[..., 3:4]; return g * (1 - a * .9) + c * a * .9
def e_stab(f, r):
    raw = look(mfx.cover(AR[int(30 + f)], 1.0)); st = look(mfx.cover(A[int(30 + f)], 1.0))
    out = st.copy(); out[:, :W // 2] = raw[:, :W // 2]; out[:, W // 2 - 2:W // 2 + 2] = 1; return g3(fin(out, r))

EFFECTS = [
    ("fisheye", "Fisheye punch", "Optics Compensation / fisheye lens", "The Lucki and Carti lens: punches in wide on the cut, eases back.", "on", e_fisheye),
    ("bulge", "Bulge on the kick", "CC Bend It / Bulge", "The frame swells toward you on every kick.", "on", e_bulge),
    ("twirl", "Twirl", "CC Twister / Twirl", "A spin-warp at a transition peak. Our exit into the ending.", "careful", e_twirl),
    ("liquid", "Liquid warp transition", "Turbulent Displace transition", "A melts, B melts back in. On the bar line into the name.", "on", e_liquid),
    ("type_stack", "Type stack", "Text animators / repeater (Yeat, Carti)", "The word repeated through the frame, one solid, the rest outlined, scrolling.", "on", e_stack),
    ("hud", "Camcorder HUD", "Overlay packs / Boiler Room raw", "Corner brackets, REC on the beat, running timecode.", "on", e_hud),
    ("stabilize", "Stabilize", "Warp Stabilizer (vid.stab)", "Left: raw handheld. Right: stabilized, then warped on purpose.", "on", e_stab),
]
meta = []
for key, name, plugin, note, tag, fn in EFFECTS:
    rng = np.random.default_rng(7)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-vf", "scale=360:640:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", "-an", f"{OUT}/{key}.mp4"], stdin=subprocess.PIPE)
    for f in range(60): enc.stdin.write((np.clip(fn(f, rng), 0, 1) * 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.3", "-i", f"{OUT}/{key}.mp4", "-frames:v", "1", "-q:v", "6", f"{OUT}/{key}.jpg"])
    meta.append({"key": key, "name": name, "plugin": plugin, "note": note, "tag": tag}); print("done", key, flush=True)
json.dump(meta, open(f"{OUT}/effects3.json", "w"), indent=1)
