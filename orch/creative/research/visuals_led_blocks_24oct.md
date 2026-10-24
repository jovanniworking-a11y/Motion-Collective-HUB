# Visual reference · festival LED stage (Jovanni, 24 Oct)
Clips: IMG_2616 (3.2 s, 4K 24 fps, overhead crowd shot of a truss stage) and IMG_2615 (1.25 s, mostly black: the phone moving, lights smearing). Source clips and stills stay out of git (other event, crowd faces in frame).

## What's actually happening on screen
| Element | What it does | Timing (measured, estimate) |
|---|---|---|
| **Round LED panels** (big circles across the top truss, plus X-truss boxes) | Content is chunky **stepped blocks**: a circle fills in staircase clusters from one corner, flips to a **checker**, then **erodes** back to black. Never smooth gradients. | Big panel changes land roughly every 0.12–0.25 s, i.e. on the 8th notes; they get faster in the last second (a build). |
| **Colour** | One colour family at a time (acid green) plus white strobes. Black between hits. | The green wash pulses about every 0.29 s (about every 7 frames). |
| **Beams** | Lasers (purple/red), moving heads and 8-cell blinders cut through haze. | Constant movement; this is what fills the room. |
| **Camera** (2615) | A fast move turns every light into streaks and trails. That smear is literally an afterimage. | 1 s of motion, then black. |

## What we take (and what we can't)
- **Take:** circles with block-build, checker flip and erode on the 8ths, black space between hits, one colour family, and the light trail.
- **Map to MOTION:** the three circles = **the 3x eyes**, on the eye wall behind the DJ. Bone and steel blue on void, with red only as one hairline. In the second half the blocks reveal the eyes art.
- **Can't take:** lasers and haze (banned: smoke detectors, house rules), and acid green (off-palette). Without haze, projection carries the look, not beams.

## What's built
- `media/visuals/block_eyes.py` renders the loop: 1280×1280 (the TouchDesigner free-licence cap), 30 fps, 128 BPM, 8 bars (15.00 s), loops on the beat. Other tempos: `python3 media/visuals/block_eyes.py out.mp4 --bpm 132`.
- `media/visuals/MOTION_block_eyes_128bpm_1280.mp4` is the fallback loop for the projector if TouchDesigner isn't up.
- `live-ops/touchdesigner/NETWORK.txt` scene e is the same look as a live, beat-driven TouchDesigner network (for Chaka / the booth machine).

| Bars | Section |
|---|---|
| 1–2 | Build |
| 3 | Checker |
| 4 | Erode |
| 5–8 | The same, revealing the eyes |
| 7 | Stutter on the 16ths |
| 8 | Hairline under the centre eye |

## Open
- Projector: rent or borrow (open). Position it so the three circles land on the eye wall. Check corner-pin on 29 Oct.
- Tempo per set (open): the loop is 128 BPM. Re-render at each DJ's tempo, or let TouchDesigner follow the DJM.
