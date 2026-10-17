"""Render a 2 s demo clip of every MOTION FX effect for the gallery (360x640 h264, small).
usage: python3 gallery_clips.py <video_dir> <sting_frames_dir> <word_layer.png> <out_dir>"""
import sys, os, subprocess, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mfx
from mfx import W, H

VID, STING, WORD, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
A = mfx.plate(f"{VID}/a.mov", deflicker=True); B = mfx.plate(f"{VID}/b.mov")
RAW_A = mfx.plate(f"{VID}/a.mov", denoise=False)
SLOW = mfx.plate(f"{VID}/a.mov", 2.55, 3.45, fps=90, interp=True, deflicker=True)
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
fin = lambda g, rng: mfx.finish(g, rng=rng, mist=0.35, grain_amt=0.05, vig=0.3)
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("L")).astype(np.float32) / 255
wa = np.asarray(Image.open(WORD).convert("RGBA")).astype(np.float32)[..., 3] / 255
N = 60

def fa(t, z=1.06, **kw): return mfx.cover(A[int(min(len(A) - 1, 30 + t))], z, **kw)
def fb(t, z=1.06, **kw): return mfx.cover(B[int(min(len(B) - 1, 280 + t))], z, **kw)

def fx_raw_vs_look(f, rng):
    raw = mfx.cover(RAW_A[60 + f], 1.12); raw = np.clip((raw - .06) * 1.4, 0, 1)
    new = fin(look(mfx.cover(A[60 + f], 1.12)), rng)
    out = new.copy(); out[:, :W // 2] = raw[:, :W // 2]; out[:, W // 2 - 2:W // 2 + 2] = 1
    return out
def fx_promist(f, rng):
    g = look(fb(f)); return mfx.grain(mfx.promist(g, 0.0 if (f // 30) % 2 == 0 else 0.6), .04, rng=rng)
def fx_deep_glow(f, rng):
    g = look(fb(f)); return mfx.grain(mfx.deep_glow(g, 0.0 if (f // 30) % 2 == 0 else 0.7, thr=.6), .04, rng=rng)
def fx_grain(f, rng):
    g = look(fa(f)); return np.clip(g if (f // 30) % 2 == 0 else mfx.grain(g, .07, rng=rng), 0, 1)
def fx_motion_blur(f, rng):
    zf = lambda t: 1.0 + 0.5 * mfx.expo_io(((t % 30) / 30))
    sharp = (f // 30) % 2 == 0
    r = lambda t: look(fa(f, zf(t)))
    return fin(r(f) if sharp else mfx.mblur(r, f, 0.5, 8), rng)
def fx_shake(f, rng):
    hit = 0 if f < 30 else 30
    dx, dy, rot = mfx.shake(f, hit, amp=26, seed=hit)
    return fin(mfx.mblur(lambda t: look(fb(f, 1.1, dx=mfx.shake(t, hit, 26, seed=hit)[0], dy=mfx.shake(t, hit, 26, seed=hit)[1], rot=mfx.shake(t, hit, 26, seed=hit)[2])), f, .5, 4), rng)
def fx_speed_ramp(f, rng):
    sp = [3.0 if i < 12 else 3 - 2 * mfx.ease_io((i - 12) / 10) for i in range(N)]
    idx = int(min(len(SLOW) - 1, sum(sp[:f])))
    return fin(look(mfx.cover(SLOW[idx], 1.08)), rng)
def fx_whip(f, rng):
    a, b = look(fa(f)), look(fb(f))
    p = mfx.clamp01((f - 20) / 16)
    g = a if f < 20 else (b if f >= 36 else mfx.whip(a, b, p))
    return fin(g, rng)
def fx_zoom_through(f, rng):
    a, b = look(fa(f)), look(fb(f)); p = mfx.clamp01((f - 22) / 14)
    return fin(a if f < 22 else (b if f >= 36 else mfx.zoom_transition(a, b, p, .5)), rng)
def fx_luma_fade(f, rng):
    a, b = look(fa(f)), look(fb(f)); return fin(mfx.luma_fade(a, b, mfx.ease_io((f - 15) / 30)), rng)
def fx_defocus(f, rng):
    a, b = look(fa(f)), look(fb(f)); p = mfx.clamp01((f - 15) / 30)
    return fin(a if f < 15 else (b if f >= 45 else mfx.defocus(a, b, p)), rng)
def fx_flash(f, rng):
    a, b = look(fa(f)), look(fb(f)); g = a if f < 30 else mfx.flash(b, (f - 30) / 6, .85)
    return fin(g, rng)
def fx_slices(f, rng):
    g = look(fb(f)); amt = 0 if f < 20 else 300 * ((f - 20) / 25) ** 1.4
    return fin(mfx.slices(g, amt, seed=3) * (1 - mfx.clamp01((f - 40) / 15)), rng)
ECHO = {}
def fx_echo(f, rng):
    e = ECHO.setdefault("e", mfx.Echo((H, W)))
    g = look(fa(f, 1.0 + 0.25 * mfx.ease_io(f / 60), dx=200 * math.sin(f / 9)))
    return fin(e(g, .8, .6), rng)
def fx_letterbox(f, rng):
    g = look(fb(f)); h = 420 + (H - 420) * mfx.expo_out(max(0, f - 25) / 12)
    return fin(mfx.letterbox(g, h), rng)
def fx_triptych(f, rng):
    fr = [look(fa(f)), look(fb(f)), look(fa(f + 90 if 30 + f + 90 < len(A) else f))]
    return fin(mfx.triptych(fr), rng)
def fx_astig(f, rng):
    g = look(fb(f)); return mfx.grain(np.clip(mfx.astig(g, 0.0 if (f // 30) % 2 == 0 else 0.6, thr=.7), 0, 1), .04, rng=rng)
def fx_cutout(f, rng):
    lit = np.clip(look(fb(f), 1.8) * 1.3 + .2, 0, 1); s = 1 + 0.14 * (1 - mfx.expo_out(f / 8))
    a = np.asarray(Image.fromarray(wa).transform((W, H), Image.AFFINE, (1 / s, 0, W / 2 * (1 - 1 / s), 0, 1 / s, H / 2 * (1 - 1 / s)), resample=Image.BILINEAR))
    return mfx.grain(lit * a, .03, rng=rng)
def fx_logo(f, rng):
    return STF(min(89, 4 + f))
def fx_sweep(f, rng):
    return STF(min(89, 32 + f // 2 * 1 + f // 2))

EFFECTS = [
    ("raw_vs_look", "The MOTION look", "Film curve + Pro-Mist + 35 mm grain (Dehancer / FilmConvert)", "Left: raw phone clip upscaled. Right: our look. Every shot gets this, so the edit has one grade.", fx_raw_vs_look),
    ("promist", "Pro-Mist diffusion", "Tiffen Black Pro-Mist filter", "Highlights bloom softly, low-res blocks melt. Fashion-film staple. Toggles every second.", fx_promist),
    ("deep_glow", "Deep Glow", "Deep Glow / Sapphire S_Glow", "Bloom on light sources and the logo. Use on lights, never on faces.", fx_deep_glow),
    ("grain", "Film grain", "FilmConvert / Dehancer grain", "Clumped grain strongest in the mids. Goes over type too, so graphics sit in the image.", fx_grain),
    ("motion_blur", "Motion blur", "ReelSmart Motion Blur (RSMB)", "Same zoom without (first half) and with real sub-frame blur. Blur is what makes moves feel shot, not slid.", fx_motion_blur),
    ("shake", "Impact shake", "Sapphire S_Shake / Universe Shake", "A decaying hit on the kick. Only in the drop, small, with motion blur.", fx_shake),
    ("speed_ramp", "Speed ramp", "Twixtor (optical-flow slow motion)", "Real time, then eases to 1/3 speed with new in-between frames. One hero moment per edit.", fx_speed_ramp),
    ("whip", "Whip pan", "Transition packs / Film Impact", "Both shots smeared by their own speed. Use on a direction change, matched left-to-left.", fx_whip),
    ("zoom_through", "Zoom-through", "CC Radial Fast Blur / Motion Bro zoom", "Punch into A, land out of B; the cut hides at the peak of the blur. Once per section, on a bar line.", fx_zoom_through),
    ("luma_fade", "Luma fade", "Luma key transition", "B arrives through its brightest parts first (the lights). Elegant for slow sections.", fx_luma_fade),
    ("defocus", "Rack-focus dissolve", "Lens blur transition", "A goes soft, B resolves. The luxury-campaign transition.", fx_defocus),
    ("flash", "Exposure flash", "Sapphire S_Flicker / flash frame", "Exposure pushes then falls back, never a flat grey card. Max two per teaser.", fx_flash),
    ("slices", "Break-up", "Sapphire S_Zap / Universe Glitch (clean)", "Horizontal slices slide apart. Our exit move for scenes and the logo.", fx_slices),
    ("echo", "Afterimage", "Echo / Time Displacement", "A decaying copy trails the motion. The AFTERIMAGE signature.", fx_echo),
    ("letterbox", "Letterbox open", "Film-frame bars", "Builds feel cinematic in a thin frame; the bars snap open on the drop.", fx_letterbox),
    ("triptych", "Triptych", "Split-screen bands", "Three moments in three bands, the same layout as the eyes.", fx_triptych),
    ("astig", "Astigmatism streaks", "Optical Flares / S_Rays (neutral)", "Light streaks off hot points, like lights when you're drunk. White only.", fx_astig),
    ("cutout", "Footage cut-out type", "Track matte (luma / alpha)", "Footage plays inside the letters; the word lands with a scale settle.", fx_cutout),
    ("logo", "Logo fly-in", "Element 3D-style logo + RSMB", "The dimensional mark: flies in, red M's peel out, motion blur, glow.", fx_logo),
    ("sweep", "Light sweep", "CC Light Sweep / specular wipe", "One specular pass across the mark. Luxury signature, once.", fx_sweep),
]

meta = []
for key, name, plugin, note, fn in EFFECTS:
    rng = np.random.default_rng(7)
    if key in ("logo", "sweep"):                     # colour clips straight from the sting frames (red M's)
        start = 0 if key == "logo" else 30
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-start_number", str(start), "-i", f"{STING}/f%03d.png",
                        "-frames:v", "60", "-vf", "crop=1080:1080:0:420,scale=360:360:flags=lanczos,pad=360:640:0:140", "-c:v", "libx264",
                        "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", f"{OUT}/{key}.mp4"], check=True)
        meta.append({"key": key, "name": name, "plugin": plugin, "note": note}); print("done", key, flush=True); continue
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-vf", "scale=360:640:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", "-an", f"{OUT}/{key}.mp4"], stdin=subprocess.PIPE)
    for f in range(N):
        g = fn(f, rng)
        enc.stdin.write((np.clip(g, 0, 1) * 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    meta.append({"key": key, "name": name, "plugin": plugin, "note": note})
    print("done", key, flush=True)
json.dump(meta, open(f"{OUT}/effects.json", "w"), indent=1)
