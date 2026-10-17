"""Gallery clips for the second batch of MOTION FX (the rest of the popular plugin looks). RGB output.
usage: python3 gallery_clips2.py <video_dir> <sting_frames_dir> <word_layer.png> <out_dir> [part 0|1]"""
import sys, os, subprocess, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfx
from mfx import W, H

VID, STING, WORD, OUT = sys.argv[1:5]; PART = int(sys.argv[5]) if len(sys.argv) > 5 else -1
os.makedirs(OUT, exist_ok=True)
A = mfx.plate(f"{VID}/a.mov", deflicker=True); B = mfx.plate(f"{VID}/b.mov")
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
fin = lambda g, rng: np.clip(mfx.grain(mfx.vignette(mfx.promist(g, .3), .3), .045, rng=rng), 0, 1)
wa = np.asarray(Image.open(WORD).convert("RGBA")).astype(np.float32)[..., 3] / 255
LOGO = np.asarray(Image.open(f"{STING}/f064.png").convert("RGB")).astype(np.float32) / 255
N = 60
fa = lambda t, z=1.06: look(mfx.cover(A[int(min(len(A) - 1, 30 + t))], z))
fb = lambda t, z=1.06: look(mfx.cover(B[int(min(len(B) - 1, 280 + t))], z), 1.4)
g3 = lambda g: np.repeat(g[..., None], 3, 2)
toggle = lambda f: (f // 30) % 2 == 1
PREV = {}

def e_saber(f, r):
    l = mfx.saber(wa, f)
    return g3(np.clip(wa * 0.15 + l, 0, 1))
def e_flare(f, r): g = fb(f); return g3(fin(np.clip(mfx.lens_flare(g, 300 + 10 * f, 520, .55), 0, 1), r))
def e_rays(f, r): g = fb(f); return g3(fin(np.clip(mfx.rays(g, .45, .25, .8 if toggle(f) else 0), 0, 1), r))
def e_twitch(f, r): return g3(fin(mfx.twitch(fa(f), f, amount=1.2), r))
def e_glitch(f, r):
    g = fb(f); p = PREV.get("g", g); PREV["g"] = g
    return g3(fin(mfx.block_glitch(g, p, .25 if toggle(f) else 0, seed=f), r))
def e_rgb(f, r): g = fa(f); return np.clip(mfx.rgb_split(g, 10 if toggle(f) else 0), 0, 1)
def e_reflect(f, r):
    lg = mfx.shift(LOGO, 0, 260)
    return np.clip(mfx.reflect(lg, .64, .22, .4), 0, 1)
def e_heat(f, r): return g3(fin(mfx.heat_haze(fb(f), f, 7), r))
def e_warp(f, r): return g3(fin(mfx.warp(fa(f), f), r))
def e_leak(f, r): return g3(fin(np.clip(mfx.light_leak(fa(f), f, .6), 0, 1), r))
def e_burn(f, r):
    a, b = fa(f), fb(f); p = mfx.clamp01((f - 10) / 20)
    g = mfx.film_burn(a, p) if f < 30 else mfx.film_burn(b, 1 - mfx.clamp01((f - 30) / 20))
    return g3(fin(g, r))
def e_vhs(f, r): return g3(mfx.vhs(fa(f), f))
def e_halftone(f, r): return g3(mfx.halftone(fa(f), 12))
def e_sort(f, r): g = fb(f); return g3(fin(mfx.pixel_sort(g, .5) if toggle(f) else g, r))
def e_duotone(f, r): return np.clip(mfx.grain(mfx.duotone(fa(f)), .04, rng=r), 0, 1)
def e_outline(f, r):
    t = f if f < 25 else 25
    g = fa(t); return g3(fin(mfx.freeze_outline(g, 1.0) if f >= 25 else g, r))
def e_posterize(f, r): return g3(fin(fa(mfx.posterize_time(f, 8)), r))
def e_invert(f, r):
    g = fb(f); hit = 15 if f < 30 else 45
    return g3(fin(mfx.invert_hit(g, (f - hit) / 6) if f >= hit else g, r))
def e_mirror(f, r): return g3(fin(mfx.mirror(fa(f)), r))

EFFECTS = [
    ("saber", "Saber outline", "Video Copilot Saber", "Energy glow running along a logo or word outline. Neutral white for us, on type only.", "on", e_saber),
    ("lens_flare", "Lens flare", "Video Copilot Optical Flares", "Anamorphic streak plus ghosts. Neutral, sparing: one light source, one moment.", "on", e_flare),
    ("rays", "Light rays", "Sapphire S_Rays / CC Light Rays", "God rays out of the club lights. Toggles every second.", "on", e_rays),
    ("twitch", "Twitch", "Video Copilot Twitch", "Random frames jump in scale, position, exposure and focus. Nervous live energy; use for a beat or two.", "careful", e_twitch),
    ("block_glitch", "Datamosh blocks", "Universe Glitch / datamosh", "Macro-blocks stick to the last frame like a broken codec. Toggles every second.", "careful", e_glitch),
    ("rgb_split", "RGB split", "Shift Channels / chromatic aberration", "Red and cyan fringes. Off-brand: it tints the image.", "off", e_rgb),
    ("reflect", "Floor reflection", "Video Copilot VC Reflect", "A glossy mirrored floor under the mark. Luxury product-shot look.", "on", e_reflect),
    ("heat_haze", "Heat haze", "Video Copilot Heat Distortion", "A slow shimmer over the frame. Subtle on lights; strong reads as trippy.", "careful", e_heat),
    ("warp", "Wave warp", "Wave Warp / Turbulent Displace", "Rippling distortion. Off-brand: the acid look we avoid.", "off", e_warp),
    ("light_leak", "Light leak", "BCC Light Leaks (neutral)", "A soft white leak drifting across. Use as a slow transition.", "on", e_leak),
    ("film_burn", "Film burn", "Film burn transition packs", "Blown patches swallow the frame to white, the next shot burns back in.", "careful", e_burn),
    ("vhs", "VHS / CRT", "VHS / retro scanline plugins", "Scanlines, tracking band, line jitter. A deliberate retro quote only.", "off", e_vhs),
    ("halftone", "Halftone", "Color Halftone / CC Ball Action", "Dots sized by brightness, the same texture as the eyes print.", "on", e_halftone),
    ("pixel_sort", "Pixel sort", "Pixel sorting scripts (popular GFX glitch)", "Bright runs in each row sort into smears. Toggles every second.", "careful", e_sort),
    ("duotone", "Steel duotone", "Tritone / Colorama", "Night blue to steel ice. The only tint MOTION allows.", "on", e_duotone),
    ("freeze_outline", "Freeze outline", "Freeze frame + Find Edges", "The frame freezes, darkens and its edges trace in white.", "careful", e_outline),
    ("posterize_time", "Posterize time", "Posterize Time (built in)", "Held frames at 8 fps: stop-motion choppiness on purpose.", "careful", e_posterize),
    ("invert_hit", "Invert hit", "Invert flash (hype-edit staple)", "The frame inverts on a hit and decays back. Once per edit at most.", "careful", e_invert),
    ("mirror", "Mirror", "CC Kaleida / Mirror", "Symmetric frame. Off-brand except as one deliberate shot.", "off", e_mirror),
]
todo = [e for i, e in enumerate(EFFECTS) if PART < 0 or i % 2 == PART]
meta = []
for key, name, plugin, note, tag, fn in todo:
    rng = np.random.default_rng(7)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-vf", "scale=360:640:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", "-an", f"{OUT}/{key}.mp4"], stdin=subprocess.PIPE)
    for f in range(N):
        enc.stdin.write((np.clip(fn(f, rng), 0, 1) * 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.3", "-i", f"{OUT}/{key}.mp4", "-frames:v", "1", "-q:v", "6", f"{OUT}/{key}.jpg"])
    meta.append({"key": key, "name": name, "plugin": plugin, "note": note, "tag": tag}); print("done", key, flush=True)
json.dump(meta, open(f"{OUT}/effects2_{PART}.json", "w"), indent=1)
