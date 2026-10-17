"""MOTION artist announcement: IAMARIOLOGY (opening Devil's Night, b2b raymixes). ~12.6 s, 9:16, his own set audio (142 bpm).
  sting -> the neon eye tilts down to reveal him (graphic match with our eye triptych) -> beat-cut punch-ins + stutter
  -> name stack -> announcement card -> the point to camera: speed ramp, freeze, outline, name slam
  -> black, Devil's Night 10.30.2026 -> the mark + RSVP, while the music echoes out.
usage: python3 announce_iam.py <video_dir> <sting_dir> <out.mp4>"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fx"))
import mfx
from mfx import W, H, FPS
VID, STING, OUT = sys.argv[1:4]; D = os.path.dirname(os.path.abspath(__file__))
SPB = 60 / 142.1 * FPS; kf = lambda b: 1.5 + SPB * b
rng = np.random.default_rng(8)
Dp = mfx.plate(f"{VID}/d.mov", bw="blue")       # blue-filter B&W: yellow wall goes dark, neon stays white                                   # in sync with the audio: index = frame
HERO = mfx.plate(f"{VID}/e.mov", 1.9, 2.9, fps=90, interp=True, bw="blue")   # the point peaks at 2.4 s  # 3x frames for the point
def rgba(p):
    a = np.asarray(Image.open(p).convert("RGBA")).astype(np.float32) / 255; return a[..., :3], a[..., 3]
IAM = rgba(f"{D}/P_iam.png")[1]; STK = mfx.stack(IAM, 9, .55)
ANN, DEVIL, HUD, CTA = (rgba(f"{D}/P_{n}.png") for n in ("announce", "devil", "hud142", "endcta"))
STF = lambda i: np.asarray(Image.open(f"{STING}/f{i:03d}.png").convert("RGB")).astype(np.float32) / 255
look = lambda g, k=1.0: mfx.film_curve(g * k, black=0.13, gain=1.6, gamma=1.3)
g3 = lambda g: np.repeat(g[..., None], 3, 2)
KICKS = [kf(b) for b in range(6, 24)]
def env(f, decay=4):
    last = max([h for h in KICKS if h <= f], default=None); return 0 if last is None else math.exp(-(f - last) / decay)
def hud(rgb, f):
    hc, ha = HUD; ha = ha.copy()
    if (f - kf(6)) % SPB >= SPB / 2: ha[140:190, 70:110] = 0
    return rgb * (1 - ha[..., None] * .9) + hc * ha[..., None] * .9
def dshot(f, z, cy, cx=.5, rot=0, dx=0):
    return look(mfx.cover(Dp[int(min(len(Dp) - 1, f))], z, dx, 0, rot, cx=cx, cy=cy), 1.0)
END_AUDIO = 9.86 * FPS; N = int(12.6 * FPS)
E_DEVIL, E_MARK, E_EXIT = kf(20), kf(22.5), kf(22.5) + 31
af = (f"[1:a]asplit[m][t];[m]atrim=0:9.86,afade=t=out:st=9.4:d=0.46[mm];"
      f"[t]atrim=9.3:9.86,asetpts=PTS-STARTPTS,aecho=0.8:0.88:280|560|840:0.55|0.4|0.3,apad=pad_dur=3.4,afade=t=out:st=0.4:d=3.2,adelay=delays=9300:all=1[tt];"
      f"[mm][tt]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{VID}/d.mov", "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-t", f"{N / FPS:.3f}",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-maxrate", "14M", "-bufsize", "28M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
echo = mfx.Echo((H, W)); nerv = mfx.Nervous(18, seed=2); freeze = None
for f in range(N):
    ga = .05
    if f < 64: rgb = STF(f); ga = 0
    elif f < kf(6): rgb = mfx.zoom_blur(STF(min(87, 74 + f - 64)), .3 if f > kf(6) - 4 else 0); ga = 0
    elif f < kf(10):                                             # the eye: tight on the neon, tilt down to him
        q = mfx.ease_io((f - kf(6)) / (kf(10) - kf(6)))
        g = dshot(f, 2.2 - 1.1 * q, .23 + .22 * q)
        g = mfx.fog_glow(mfx.streaks(g, 2, 0, thr=.8, k=.7), .5, .45)
        if f - kf(6) < 5: g = mfx.zoom_blur(g, .3 * (1 - (f - kf(6)) / 5))
        g = echo(g, .6, .3); rgb = hud(g3(mfx.vignette(mfx.promist(g, .3), .3)), f)
    elif f < kf(14):                                             # beat-cut punch-ins, stutter in the last bar
        b = (f - kf(10)) / SPB; ti = f - kf(10 + int(b))
        fr = [(1.9, .82, .5), (1.05, .5, .5), (1.7, .32, .5), (1.9, .82, .45)][min(3, int(b))]
        mb = lambda tt: dshot(tt, fr[0] * (1 - .04 * min(1, (tt - kf(10 + int(b))) / SPB)), fr[1], fr[2])
        g = mfx.mblur(mb, f, .5, 3) if ti < 4 else mb(f)
        g = mfx.fisheye(g, .55 * math.exp(-ti / 4) + .18)
        g = mfx.bulge(g, .22 * env(f), .55)
        if b >= 3: g = nerv(g, hit=(ti % (SPB / 2)) < 1)
        g = echo(g, .55, .3 if ti < 6 else .16)
        rgb = hud(g3(mfx.vignette(mfx.promist(g, .28), .3)), f)
    elif f < kf(15):                                             # name stack
        m = f - kf(14); bg = dshot(f, 1.1, .45) * .25
        st = mfx.shift(STK, 0, -m * 12); st = mfx.liquid(st, 45 * (1 - mfx.ease_out(m / 6)), f) if m < 6 else st
        rgb = hud(g3(mfx.bulge(np.maximum(bg, st), .25 * env(f), .6)), f)
    elif f < kf(17):                                             # announcement card
        m = f - kf(15); bg = dshot(f, 1.15, .42) * .3
        bg = mfx.bulge(bg, .2 * env(f), .55)
        cc, aa = ANN; s = 1 + .08 * (1 - mfx.expo_out(m / 8))
        aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / s, 0, W / 2 * (1 - 1 / s), 0, 1 / s, H / 2 * (1 - 1 / s)), resample=Image.BILINEAR))
        rgb = g3(mfx.invert_hit(bg, m / 5) if m < 5 else bg); rgb = rgb * (1 - aa[..., None]) + cc * aa[..., None]
        rgb = hud(rgb, f)
    elif f < E_DEVIL:                                            # the point: ramp into slow motion, freeze, outline, slam
        ti = f - kf(17)
        p = min(1.0, ti / (kf(19) - kf(17)))                    # decelerate into the point (clip 2.13 s = index 21, the sharpest frame of the point), then hold
        idx = int(min(len(HERO) - 1, 21 * (1 - (1 - p) ** 2.2)))
        if f >= kf(19) and freeze is None: freeze = 21
        if freeze is not None: idx = freeze
        g = look(mfx.cover(HERO[idx], 1.12, cx=.47, cy=.42), 1.0)
        g = mfx.fisheye(g, .3 + .4 * math.exp(-ti / 5))
        if freeze is not None:
            m = f - kf(19); g = np.clip((g - .5) * (1 + .25 * min(1, m / 3)) + .5, 0, 1)   # freeze: contrast pop, no outline
            if m < 4: g = mfx.flash(g, m / 4, .7)
        g = echo(g, .82, .4)
        rgb = g3(mfx.vignette(mfx.promist(g, .3), .3))
        if freeze is not None:
            k_ = min(1, (f - kf(19)) / 2); band = np.clip(1 - np.abs(np.arange(H) - 960) / 300, 0, 1)[:, None, None] * .6 * k_
            rgb = rgb * (1 - band)                                   # keep the name readable over the white jacket
            aa = IAM * k_; rgb = rgb * (1 - aa[..., None]) + np.array([.95, .93, .9]) * aa[..., None]
        rgb = hud(rgb, f)
    elif f < E_MARK:                                             # black, one line
        z = 1 + .04 * (f - E_DEVIL) / (E_MARK - E_DEVIL); cc, aa = DEVIL
        aa = np.asarray(Image.fromarray(aa).transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), resample=Image.BILINEAR))
        rgb = cc * (aa * min(1, (f - E_DEVIL) / 4))[..., None]; ga = .03
    elif f < E_EXIT:
        rgb = STF(int(min(70, 40 + (f - E_MARK)))); cc, aa = CTA; aa = aa * min(1, (f - E_MARK) / 6)
        rgb = rgb * (1 - aa[..., None]) + cc * aa[..., None]; ga = .02
    else: rgb = STF(int(min(89, 74 + (f - E_EXIT)))); ga = .02
    if ga: rgb = mfx.grain(rgb, ga, rng=rng)
    enc.stdin.write((np.clip(rgb, 0, 1) * 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print("done", N)
