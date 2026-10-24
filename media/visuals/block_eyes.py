"""Block-build eyes loop for the projector (fallback if TouchDesigner isn't up).

Look learned from Jovanni's festival reference (24 Oct): round LED panels whose content builds in and
erodes in chunky stepped blocks on the 8th notes, checker flips on the beat, everything on black.
MOTION version: three circles = the 3x eyes, bone + steel blue on void, red only as one hairline,
an afterimage trail (light persistence) instead of haze and lasers (both banned).

    python3 media/visuals/block_eyes.py out.mp4 [--bpm 128] [--bars 8]

1280x1280 (TouchDesigner free-licence size), 30 fps, the loop is exactly N bars so it repeats on the beat.
"""
from __future__ import annotations

import argparse
import subprocess as sp
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
EYES = ROOT / "media" / "flyers" / "final_v6" / "eyes_hc.png"
S, FPS = 1280, 30
VOID = np.array([10, 8, 16], np.float32) / 255
BONE = np.array([237, 230, 218], np.float32) / 255
STEEL = np.array([143, 179, 207], np.float32) / 255
RED = np.array([200, 38, 30], np.float32) / 255
CELL = 40                      # chunky: reads from across a room, fine for the 1280 cap
R = 184                        # circle radius (keeps a 40 px margin to the frame edge)
CENTERS = [(S // 2 - 404, S // 2), (S // 2, S // 2), (S // 2 + 404, S // 2)]


def circle_cells():
    """Cells (row, col) of the grid that sit inside each circle, plus the pixel mask per circle."""
    yy, xx = np.mgrid[0:S, 0:S]
    out = []
    for cx, cy in CENTERS:
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= R * R
        cells = sorted({(y // CELL, x // CELL) for y, x in zip(*np.nonzero(mask[::CELL // 2, ::CELL // 2] * 1)) for y, x in [(y * CELL // 2, x * CELL // 2)]})
        out.append((mask, cells))
    return out


def stair_order(cells, rng, corner):
    """Order cells as a stepped staircase growing from one corner, with a little jitter (the LED look)."""
    r0 = min(r for r, _ in cells); r1 = max(r for r, _ in cells)
    c0 = min(c for _, c in cells); c1 = max(c for _, c in cells)
    def key(rc):
        r, c = rc
        dr = (r1 - r) if corner in ("bl", "br") else (r - r0)
        dc = (c - c0) if corner in ("bl", "tl") else (c1 - c)
        return max(dr, dc) * 3 + (dr + dc) * 0.5 + rng.random() * 2.2
    return sorted(cells, key=key)


def eyes_texture():
    """The eyes art (no baked text), one horizontal strip per circle, greyscale, contrast up."""
    im = Image.open(EYES).convert("L")
    w, h = im.size
    strips = []
    for k in range(3):
        m = int(h / 3 * 0.07)        # trim the black seams between the three strips
        band = im.crop((0, k * h // 3 + m, w, (k + 1) * h // 3 - m))
        band = band.resize((2 * R + 40, int((2 * R + 40) * band.size[1] / w)))
        side = 2 * R
        canvas = Image.new("L", (side, side), 0)
        canvas.paste(band, ((side - band.size[0]) // 2, (side - band.size[1]) // 2))
        arr = np.asarray(canvas, np.float32) / 255
        strips.append(np.clip((arr - 0.06) * 1.7, 0, 1))   # LED-bright, black stays black
    return strips


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--bpm", type=float, default=128.0)
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("--seed", type=int, default=31)
    a = ap.parse_args(argv)

    beat = 60.0 / a.bpm
    total = a.bars * 4 * beat
    n_frames = int(round(total * FPS))
    rng = np.random.default_rng(a.seed)
    circles = circle_cells()
    corners = ["bl", "tr", "br"]
    orders = [stair_order(cells, rng, corners[i]) for i, (_, cells) in enumerate(circles)]
    eyes = eyes_texture()
    tint = [BONE, STEEL, BONE]

    p = sp.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{S}x{S}",
                  "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                  "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], stdin=sp.PIPE)
    trail = np.zeros((S, S, 3), np.float32)
    for f in range(n_frames):
        t = f / FPS
        b = t / beat                      # beats since start
        bar, inbar = int(b // 4) % a.bars, b % 4
        eighth = int(inbar * 2)           # 0..7 within the bar
        kick = np.exp(-6.0 * (b % 1.0))   # decays across each beat
        frame = np.zeros((S, S, 3), np.float32)
        frame[:] = VOID
        for i, (mask, cells) in enumerate(circles):
            order = orders[i]
            n = len(order)
            phase = bar % 4
            if phase in (0, 1):           # build: one stepped cluster per 8th, full at the end of bar 2
                k = int(n * min(1.0, ((bar % 2) * 8 + eighth + 1) / 16))
                lit = set(order[:k])
            elif phase == 2:              # checker flips on every beat
                flip = int(inbar) % 2
                lit = {rc for rc in order if (rc[0] + rc[1] + flip + i) % 2 == 0}
            else:                         # erode back to black on the 8ths
                k = int(n * max(0.0, 1 - (eighth + 1) / 8))
                lit = set(order[n - k:])
            if bar == a.bars - 2 and inbar >= 3:          # stutter on the 16ths before the last bar
                if int(inbar * 4) % 2:
                    lit = set()
            cx, cy = CENTERS[i]
            block = np.zeros((S, S), np.float32)
            for r, c in lit:
                block[r * CELL:(r + 1) * CELL - 3, c * CELL:(c + 1) * CELL - 3] = 1.0   # 3 px gap = LED seams
            block *= mask
            if bar >= a.bars // 2:        # second half: the blocks reveal the eyes art, not flat fill
                tex = np.zeros((S, S), np.float32)
                tex[cy - R:cy + R, cx - R:cx + R] = eyes[i]
                block *= 0.1 + 0.9 * tex
            gain = 0.82 + 0.18 * kick
            frame += block[..., None] * (tint[i] * gain - VOID)
        # afterimage: lights leave a fading trail (our name, and clip 2615's smear) instead of haze
        trail = np.maximum(trail * 0.78, frame - VOID)
        out = np.clip(VOID + np.maximum(frame - VOID, trail * 0.55), 0, 1)
        if bar == a.bars - 1 and inbar < 2:              # one red hairline under the centre eye, then gone
            y = CENTERS[1][1] + R + 36
            out[y:y + 2, S // 2 - 60:S // 2 + 60] = RED
        p.stdin.write((out * 255).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    print(f"{a.out}: {n_frames} frames, {total:.2f}s = {a.bars} bars at {a.bpm:g} BPM")


if __name__ == "__main__":
    main()
