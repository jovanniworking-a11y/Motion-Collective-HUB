# MOTION sting: the logo "touchdown" (3 s, 30 fps)

Use it at the start and end of every video so the mark becomes the signature.

| Time | Beat |
|---|---|
| 0.0–0.2 s | Black, then two strobe ticks that show a ghost of the logo (no grey frames) |
| 0.27–0.77 s | The four M's land left to right. Each one leaves an **afterimage** trail and fires an **astigmatism** flare (the streaks you see from lights when drunk) |
| 1.0–1.5 s | MOTION fades in **seeing double**, then snaps into focus. COLLECTIVE · AUSTIN follows |
| 1.6–2.4 s | Hold: flicker, grain, a slow flare sweep |
| whole sting | Camera: a slow push-in, plus a punch-in when the last M lands |
| 2.4–3.0 s | Exit: the mark breaks into slices that slide apart, then only its afterimage is left, fading to black (no white frame) |

- Files: `MOTION_sting_9x16.mp4` (Reels/Stories), `_1x1` (feed), `_16x9` (YouTube/landscape).
- They're rendered on black, so they can go over footage with the **Screen** blend mode and the black drops out.
- Red appears only in the MMMM letters. Footage is never tinted.
- The M's are the dimensional mark from `media/brand/src/logo3d.py`: chiselled, lit, stacked front-over-back, and each one casts a shadow on the one behind it.
- Rebuild: `python3 media/brand/src/logo3d.py layers W H <sting dir>` (needs the glyph masks from `glyphs.html`), then `python3 src/sting.py W H out_dir`, then encode the PNGs with ffmpeg.
