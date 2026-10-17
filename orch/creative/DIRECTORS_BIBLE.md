# MOTION · Director's Bible (video)

The direction in one line: **cool, modern, directed. Pop culture, not corporate.** Our taste is the product.

**Updated 17 Oct (Jovanni):** less corporate, more warping, more pop-culture video references:

| Reference | What we take |
|---|---|
| Lucki / Carti | Fisheye punch-ins, lo-fi distortion, bulge on the kick |
| Yeat | Type stacks, glitch blocks, pixel sort, techy graphics |
| Kettama / Prospa / Boiler Room / Raw Cuts | Camcorder HUD, raw rave energy, the logo opening and closing every video |
| Kanye set design | Monumental endings: black, one line of type, negative space |
| Peso Pluma | Confident, cinematic framing, flashy but clean |
| Drake / OVO | The moody open: letterbox, slow motion, anamorphic streaks, fog glow, one small line of type |
| Bad Bunny / reggaeton | Cut and pop on the dembow accents (the "chick" of boom-ch-boom-chick), fisheye close-ups, one kaleidoscope hit, chrome type |

The combo (teaser v6): Drake open, then Carti/Bad Bunny energy, Yeat type, Boiler Room HUD, Kanye ending, all cut to the clip's own reggaeton track.

Still never: preset transitions on every cut, a flash or glow on every cut, red tinting the footage, or acid colour washes.

Full sourced research: `orch/creative/research/editing_research.md`. Effects library: `media/fx/mfx.py`. Effects gallery: see the hub links in `CLAUDE.md`.

## 1. Every cut needs a reason
A cut feels random when it has no motivation. Before keeping a cut, name at least one of these reasons out loud:
1. **Motion:** the action continues or starts on the cut. Cut about a third of the way into the move, so the incoming shot finishes it.
2. **Eye-trace:** the subject sits in the same third of the frame on both sides of the cut.
3. **Graphic:** the shapes or the brightness rhyme across the cut, like a diagonal arm into diagonal beams, or a bright centre into a bright centre. In black and white this is our strongest tool.
4. **Music:** the cut lands on a kick, a bar line or a phrase change.
5. **Story:** the incoming shot shows something new, such as the name, the eyes or the date.

If a cut has none of these, move it onto the beat grid or pick a different shot. Every teaser ships with a cut list that gives the reason for each cut (see `media/teasers/*_cutlist.md`).

### Why it works (the science, briefly)
- **Edit blindness:** viewers miss about a quarter of cuts within a scene, and more when motion starts on the cut (Tim Smith). Motion *after* the cut hides it. Music playing across a cut hides it too.
- **Event segmentation:** a big visual change registers as a new chapter (Zacks, Magliano). Spend those big changes on section changes only (build, drop, ending); everywhere else the cuts should flow.
- **Murch's Rule of Six**, in priority order: emotion > story > rhythm > eye-trace > 2D plane > 3D space. When a cut can't satisfy all six, give up the ones at the bottom first.

## 2. Rhythm: tension, then release
At 127 bpm: 1 beat = 0.472 s = 14.17 frames at 30 fps; 1 bar = 1.89 s; 8 bars = 15.1 s.
- **Compute every cut from its absolute beat time.** Rounding beat by beat drifts about a frame every 6 beats.
- **Build density:** cut every 4, then 2, then 1 beat, and use half-beats only in the last bar. Don't cut on every beat the whole way through; that reads as frantic, not hype.
- **One beat of black (or a held frame) before the drop.** The silence is what makes the drop hit.
- **The drop frame gets the single best image**, a full frame with real motion, plus an impact shake.
- **Use one designed transition per section, on a bar line.** All other edits are hard cuts.
- **One hero speed ramp per edit:** real speed, then ease down to 1/3. Hold it once, the way a luxury campaign does.

## 3. Expensive vs CapCut
| We do | We never do |
|---|---|
| Real sub-frame motion blur on every move (RSMB look) | Crisp, strobing digital zooms |
| One grade on every shot: film curve, Pro-Mist, one grain | A different filter on every clip |
| Grain over everything, including the type | Clean type pasted on top of grainy footage |
| Bodoni Moda and Jost, wide tracking, negative space | Bouncing, shaking or multi-coloured text |
| At most 2 flash frames per teaser | Flashes and glows on every cut |
| Cuts for 95% of edits, one designed transition per section | A preset transition pack on every cut |
| Red only on MMMM and b2b | Red tints, colour washes, RGB-split fringes |

## 4. Low-res phone footage
- Denoise **before** upscaling (`hqdn3d`), and resample only once (Lanczos/bicubic from the native plate).
- Deflicker phone clips that strobe (`deflicker`), so the frames don't flash white. Keep the club clip's own on-beat strobes.
- Apply the house look: film curve, Black Pro-Mist diffusion, then 35 mm grain at the output resolution. This turns compression blocks into something that reads as film.
- Don't zoom past about 1.15x on a 320 px clip. Put low-res clips in the fast sections and keep the long holds for the best plates.
- Hero shots only: Real-ESRGAN `realesr-general-x4v3` at 4x, then down to 1080x1920. It's slow on CPU, so it's worth it only for 2-4 s of footage.
- The real fix is at capture. The videographer shoots at 1080p or 4K, at 60 or 120 fps for slow motion, with a 180° shutter.

## 5. The logo
- **Material:** the MMMM is a physical object: chiselled bevel, extruded thickness, lacquer gloss on the red trail, a satin pearl front M, and each M casting a soft shadow on the one behind it. It's never four flat letters added on top of each other.
- **Motion:** the white M flies in from depth on an expo curve with a small spring settle (overshoot about 102-105%). The red M's peel out of it, staggered 4 frames apart. Motion blur on all of it, one light sweep, and bloom only on the landing.
- **Placement:** the logo opens and closes every video. The only change between videos is the edit that sits between them.

## 6. The crew and the learning loop
| Role | Who | Does |
|---|---|---|
| Creative director | **Jovanni** (human) | Taste, music choice, the never-list, final yes on everything that goes out |
| Director / editor | Claude Code session | Builds the cut list with a reason per cut, renders 2-3 variants, keeps this bible current |
| VFX | Claude Code + `media/fx/mfx.py` | Owns the effects presets, the logo, the sting, and the low-res treatment |
| Reference scout | Gemini (watches YouTube/IG at about 1 fps) | Describes references: mood, shot types, pacing. Not frame-accurate |
| Measurement | ffmpeg + Claude | Cut detection, average shot length, cuts per bar, contact sheets, so references become numbers |
| Videographer | a human with a camera | Real moves, light, 60/120 fps, clean plates; capture fixes what no upscaler can |

**The loop:**
1. **Collect:** one sheet, one row per reference (link, brand, timestamp, why it's good, tags such as `hold`, `speed-ramp`, `graphic-match`, `flash`, `type-lockup`, `grain`).
2. **Analyse:** Gemini writes a 5-line description. ffmpeg and Claude measure the shot lengths and cuts per bar.
3. **Encode:** turn the findings into presets in `mfx.py` and rules in this bible.
4. **Make:** 2-3 variants per teaser.
5. **Review:** Jovanni scores each variant 1-5 on four questions: expensive? on-beat? readable type? red used correctly?
6. **Learn:** every two weeks, promote what scores 4-5 and retire what doesn't. Every correction Jovanni makes becomes a hard rule here and in `CLAUDE.md`.

What doesn't work: fully autonomous agents "scouring YouTube" on their own. Gemini only samples about 1 frame per second, so it misses the cuts that matter. Taste stays with the creative director. The tools gather the material, measure it and execute.
