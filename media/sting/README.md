# MOTION sting: the logo "touchdown" (3 s, 30 fps)

Use it at the start and end of every video so the mark becomes the signature.

| Time | Beat |
|---|---|
| 0.0–0.2 s | Black, then two strobe ticks that show a ghost of the logo (no grey frames) |
| 0.27–0.77 s | The four M's land left to right. Each one leaves an **afterimage** trail and fires an **astigmatism** flare (the streaks you see from lights when drunk) |
| 1.0–1.5 s | MOTION fades in **seeing double**, then snaps into focus. COLLECTIVE · AUSTIN follows |
| 1.6–2.4 s | Hold: flicker, grain, a slow flare sweep |
| 2.4–3.0 s | Exit: everything smears right into its afterimage, one white strobe, black |

- Files: `MOTION_sting_9x16.mp4` (Reels/Stories), `_1x1` (feed), `_16x9` (YouTube/landscape).
- They're rendered on black, so they can go over footage with the **Screen** blend mode and the black drops out.
- Red appears only in the MMMM letters. Footage is never tinted.
- Rebuild: render the layers with `src/layers.html` (headless Chrome, transparent background), then run `python3 src/sting.py W H out_dir` and encode the PNGs with ffmpeg.
