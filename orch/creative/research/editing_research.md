# MOTION: editing research and director's bible notes

Scope: 9:16 hype teasers, 10-20 s, cut to music at about 127 bpm. The look is black and white or steel blue, chic and fashion-film, never trippy or acid. Red appears only as a tiny accent and never tints an image. Tools are Python, numpy and ffmpeg, with no After Effects.

**How sure each claim is.** Each claim is marked one of three ways:
- **[src]** comes from a source listed at the end.
- **[local]** was checked on this machine. That means ffmpeg 6.1.1, where every filter named below exists.
- **[craft]** is common editor practice or my own reasoning. It is not checked against a source.

**Network limits.** The sandbox could reach only github.com and pypi.org. Most other pages appear here through search-result summaries, not full reads, and the Sources section separates the two kinds.

---

## 0. Beat math at 127 bpm (use this everywhere)

| Unit | Seconds | Frames @30 | Frames @24 |
|---|---|---|---|
| 1 beat | 0.4724 | 14.17 | 11.34 |
| 1 bar (4 beats) | 1.890 | 56.7 | 45.4 |
| 4 bars | 7.56 | 226.8 | 181.4 |
| 8 bars | 15.12 | 453.5 | 362.8 |

- **Plan an 8-bar teaser.** Eight bars runs 15.1 s, which sits in the middle of the 10-20 s target. Shape it as 4 bars of build and 4 bars of payoff, or as 6 + 2 with the drop at bar 7.
- **Frame drift.** A beat is not a whole number of frames, so per-beat lengths can't be rounded. Compute each cut as `round(t_beat_n * fps)` from an absolute beat time. Adding rounded 14-frame beats drifts by about 1 frame per 6 beats. **[craft]**
- **Formula.** Frames per beat = (60 / BPM) x fps. **[src: beat-sync skill page]**

---

## 1. Cut theory, and why it works

### 1.1 Murch's Rule of Six
Walter Murch, in *In the Blink of an Eye*, weights a cut by these criteria: **[src]**
- Emotion 51%
- Story 23%
- Rhythm 10%
- Eye-trace 7%
- 2D plane of screen 5%
- 3D space of action 4%

These are his judgment calls, not measurements. Use them as a priority order. When a cut can't satisfy all six, give up criteria from the bottom of the list first. Emotion alone outweighs the other five combined. **[src]**

For a teaser, that means:
- **Emotion.** Does this frame raise desire or tension? If not, cut it, however pretty it is.
- **Story.** A teaser has a micro-arc: tease, reveal, name, date. Every shot has to advance it.
- **Rhythm.** The music grid sets the rhythm (see 1.6).
- **Eye-trace.** Put the next shot's point of interest where the viewer's eye already is.
- **2D and 3D.** Screen direction and spatial logic matter least in a non-narrative teaser. You may break them for impact, but only one at a time.

### 1.2 Edit blindness and Tim Smith's Attentional Theory of Cinematic Continuity
Tim Smith's attentional theory (AToCC) explains continuity editing through visual attention. It accounts for match-action, matched exits and entrances, shot/reverse-shot, the 180-degree rule and POV cuts. **[src]**

Two findings matter for editors:
- **Edit blindness.** In Smith and Henderson (2008), viewers missed about a quarter of cuts between viewpoints of the same scene. When the cut coincided with a sudden onset of motion, that rose to about a third. **[src]**
- **Match-action.** Smith and Martin-Portugues Santacreu (Media Psychology, 2017) removed motion *after* a cut. Viewers then spotted cuts faster and missed fewer. Removing motion *before* the cut had no effect. Without the soundtrack, edit blindness mostly disappeared. **[src]**

Rules that follow:
1. **Motion after the cut hides it.** A smooth, expensive cut needs movement starting in the first frames of the incoming shot: a head turn, a hand, a camera drift. Use a static incoming shot only when you want the cut to be felt, as on a drop or a hard title.
2. **Sound carries continuity.** Keep the music continuous across cuts, and put a transient (kick, snare) on the cut. A cut on silence is exposed.
3. **Attention is the glue.** If the viewer's attention is pulled to one region, changes elsewhere go unseen. That is why eye-trace matching works.

### 1.3 Event segmentation
- **The research.** Magliano and Zacks (2011, *Cognitive Science*) had viewers segment a film while in an fMRI scanner. In a well-edited film, cuts that mark scene changes are perceived as event boundaries. Ordinary continuity cuts are not; shots are usually not experienced as events. **[src, abstract-level only]**
- **What the brain does.** At a big discontinuity, the brain does not try to reconcile the change. It opens a new mental model. **[src]**
- **Practical rule.** Spend your "big change" cuts deliberately, at most one per 4 bars plus the drop. Use them to mark the teaser's sections (tease, build, drop, title). Make every other cut a continuity-style cut, with matched motion, matched eye-trace or a held subject, so the piece reads as one flowing event. Random cuts register as constant new events, and that reads as chaos. **[craft]**

### 1.4 The Kuleshov effect
The same neutral face reads differently depending on the adjacent shot. **[src]**
- **Evidence.** Mobbs et al. (2006, fMRI, n=14) and Barratt et al. (2016) support it. Prince and Hensley (1992) failed to replicate it in a single-trial design. The original Kuleshov footage is lost. **[src]**
- **Teaser use.** A neutral, expressionless model or DJ face gets its meaning from the cutaway next to it. Pair it with a crowd surge to read as power, an empty room to read as anticipation, or the eyes teaser to read as surveillance or allure. Luxury campaigns rely on blank-faced talent for exactly this reason. **[craft]**

### 1.5 Cut types to use
- **Cut on action.** Cut mid-movement, with the outgoing shot about 1/3 through the action and the incoming shot completing it. The motion masks the cut (see 1.2).
- **Graphic match.** Match shape, position or luminance across the cut, for example a circle to a circle, or a bright centre to a bright centre. In B&W this is the strongest tool you have, because luminance *is* the image. **[craft]**
- **Motion match.** Carry the same direction and speed across the cut, such as a left whip into a left whip.
- **Sound match.** Bridge two images with one sound event, such as a snare hit landing on the cut.
- **J-cut and L-cut.**
  - J-cut: the incoming audio starts before its picture.
  - L-cut: the outgoing audio continues over the next picture.

  Over a music bed these mean voice or ambience: a crowd roar, a DJ mic drop, or the line "MOTION" whispered. Let the crowd roar enter 1 bar before the crowd shot. **[craft]**
- **Eye-trace continuity.** Track where the focus point sits at the last frame. Frame the next shot's subject within roughly the same third of the 9:16 frame, unless the cut is meant to jolt. **[src: Murch's definition; craft for the specifics]**

### 1.6 Rhythm and beat sync
- **Downbeats and phrases.** Cut on the beat, favour phrase boundaries, and place edits on the "1". Listeners hear music in 4- and 8-bar phrases, so a cut that ignores a phrase change feels wrong. **[src: Artlist, Routenote]**
- **Don't cut on every beat.** Cutting on every beat reads as frantic. Default to cuts every 2, 4 or 8 beats, and save every-beat or half-beat bursts for the bar just before the drop. **[src: beat-sync skill page]**
- **The drop.** Reserve the single strongest image for the exact drop frame, on the loudest transient. Build toward it with micro-reveals in the preceding 4-8 bars. **[src: Splice]**
- **Offbeats.** Cuts on the "and" (offbeats or hats) create syncopation and push. Use them sparingly inside the build and never on the drop. **[craft]**
- **Tension and release.** In the build, accelerate cut density (8, 4, 2, 1 beats), shorten holds and shrink the frame, for example with slow push-ins. One beat before the drop, cut to **black or a held frame for 1 beat**. Then the drop lands on a full-frame, high-motion image. A quiet beat before the drop makes the drop hit harder. **[craft]**
- **Cut a frame early.** Many editors put a cut 1-2 frames before the transient so the eye registers the image as the sound hits. **[craft, unverified]** Test both at full speed.
- **How often real videos sync.** A 2021 study of 95 music videos found the modal shot length matched the bar length in only about a fifth of clips. Strict bar-locked cutting is a style choice, not a law. **[src, search summary]**

### 1.7 Shot length (ASL) and pacing
- **Measured cases.** "I Took a Pill in Ibiza" averages about 2 s per shot, mostly close-ups, and longer shots go with wider framings. ASL also varies by genre. **[src]** Film ASL fell from about 8-11 s in the 1930s to 3-4 s by the 1980s, a trend linked to MTV-style editing. **[src]**
- **Luxury holds.** Luxury fashion editors deliberately hold shots longer, sometimes "past the point of comfort" (Dominik Braz Bittrich, an editor for YSL and Cartier). **[src]**
- **MOTION recipe [craft].** In an 8-bar teaser:
  - bars 1-4: cuts every 4 beats, so about 1.9 s each, about 4 shots
  - bars 5-6: every 2 beats, so about 0.95 s each, about 4 shots
  - bar 7: every beat, or a hold-then-black
  - bar 8: the drop image held, plus the title card

  That is about 12-14 shots, an ASL of about 1.1-1.3 s, with one long hold at both ends. Wide shots get the longer durations and close-ups the shorter ones (consistent with the Ibiza study).

### 1.8 Why random cuts feel random
A cut feels motivated when it has at least one reason:
1. motion (an action continues or begins)
2. eye-trace (attention lands where the eye already was)
3. graphic (shape or luminance rhymes)
4. musical (a transient or phrase boundary)
5. story or emotion (a new piece of information)

A random cut has none. Concretely: it falls between beats, the incoming shot is static, the subject jumps across the frame, the luminance flips with no rhyme, and nothing new is revealed. **[craft, synthesised from 1.1-1.6]**

**Editor's test.** For every cut, name its reason out loud. If you can't, move the cut onto the grid, or re-pick the shot so it carries motion or a graphic match.

---

## 2. How luxury and fashion edits are cut, and what reads as expensive

### 2.1 Observed patterns
- **Saint Laurent under Vaccarello.** Black-and-white studio portraiture is "standard fare". Films open slowly and let fabrics become tactile. Super slow motion appears, as in the Summer 2021 Indya Moore fall. Light and dark contrast is hard. Some films are built from intimate B&W vignettes rather than a narrative (Nathalie Canguilhem's "Evening"). Not every film is monochrome: the Gaspar Noe film is deep red, black and gold. **[src: The Impression, Document Journal]**
- **Luxury editors.** They let images linger, rely on one-takes, and "keep things simple and tasteful" (Braz Bittrich on Ami Paris). Studio briefs explicitly reject "loud, trend-driven", "fast-cut" work. **[src]**
- **SHOWstudio and Nick Knight.** The ethos is fashion represented through sound and motion, with the process shown openly. In the "Editing Fashion" project, many editors cut the same footage. Their Comme des Garcons film used morph and glitch, but as art direction, not as decoration. **[src]**
- **Club recaps (Boiler Room-style).** The premium versions keep a real camera close in the booth, with long handheld takes and grain. Cuts follow phrases, not every kick. **[craft, not verified by source]**

### 2.2 Expensive vs. "CapCut", technique by technique [craft]

| Expensive | Cheap |
|---|---|
| One idea per shot, held 1-4 s | Every shot under 0.5 s with no hierarchy |
| Real camera moves: slow push-in, drift, a parallax dolly | Digital zoom punch on every beat |
| Speed ramps with an eased curve (fast-slow-fast) on *one* hero moment | Ramps on every clip, or linear speed changes |
| Motion blur that matches movement (180-degree shutter look) | Crisp strobing frames from fast pans and digital shakes |
| Consistent grade across all shots (one LUT, one contrast curve, one grain) | Every clip graded differently |
| Fine, even grain over everything, including the type | Grain on footage only, with "clean" type pasted on top |
| Typography: Bodoni Moda / Jost, generous tracking, lots of negative space, static or slow fade, small and centred or a corner lock-up | Bouncing, shaking, multi-coloured, giant text |
| Flash frames: 1-2 frames of white, max 2 per teaser | Flashes and glows on every cut |
| Silence or black for 1 beat as punctuation | Wall-to-wall effects |
| Transitions are cuts (95%) plus at most one designed transition | Preset zoom/spin/glitch transition packs on every cut |

---

## 3. Plugin catalog and how to emulate each one

Shorthand:
- `F` is a float32 frame in [0,1], shape H x W x 3 (or H x W for B&W).
- `gb(x,s)` means a Gaussian blur, via `scipy.ndimage.gaussian_filter` or ffmpeg `gblur`.
- All ffmpeg filters named here exist in the local build. **[local]**

Grade in linear-ish light for glows: `F**2.2`, then the op, then `**(1/2.2)`. **[craft; Deep Glow's "linear results via gamma correction" points the same way, src]**

| Plugin or effect | What it looks like / typical use | Emulation |
|---|---|---|
| **ReelSmart Motion Blur (RSMB)** | Tracks every pixel's motion and smears along it. Natural blur on fast moves, speed ramps and CG. **[src]** | Use optical flow (OpenCV Farneback, or RAFT if a GPU exists). For each pixel, average N samples along `-v*shutter/2..+v*shutter/2`, using `cv2.remap` per sample with N=8-16. Cheap alternative: `tmix=frames=3:weights='1 2 1'` on 60 fps material, then decimate to 30 (a frame-blend shutter). |
| **Twixtor / optical-flow retime** | Synthesises in-between frames for slow motion and ramps. Tears and smears on busy scenes; best with a single moving subject. **[src]** | `minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:vsbmc=1` (slow and single-threaded). **[src]** Better: RIFE (see 4.4). For a ramp, interpolate to 4x, then build a time map `t_src(t_out)` from an eased curve and pick or blend the nearest frames. |
| **Velocity ramps (Vegas velocity envelope, AE time remap)** | Speed keyframes from 300% down to 0% freeze and -100% reverse. The classic hype "slow on the drop". **[src]** | Same time-map approach. Integrate speed s(t) to get the source time, and use a smoothstep or cubic-bezier for the speed curve. A freeze is s=0. Pair it with motion blur on the fast parts. |
| **Sapphire S_Glow / BCC Film Glow / Deep Glow** | Highlight bloom with a soft falloff. Deep Glow claims inverse-square falloff and HDR thresholding. **[src]** | `hi = clip((F-thr)/(1-thr),0,1)`. Sum `gb(hi, r)*w` for r in (4, 16, 48, 128) px with weights about 1/r to approximate inverse-square. Then `out = 1-(1-F)*(1-k*glow)` (screen). Keep it monochrome. |
| **Pro-Mist / Black Pro-Mist** | A physical diffusion filter. It lowers highlight intensity and contrast, adds a soft halo around highlights, and keeps sharpness. **[src, retail-level]** | `out = F*(1-a) + gb(F, ~1.5% of width)*a` with a=0.15-0.3, limited to highlights by a luminance mask. Lift blacks by 0.01-0.03 for the "black" variant. Hides upscale blockiness well (see 4). |
| **Halation (Dehancer, FilmConvert)** | A red-orange halo around bright sources and high-contrast edges, from light bouncing back through the film base. It hits the red layer most. Distinct from bloom, though usually combined. Controls: source limiter, smoothness, diffusion radius, hue. **[src]** | `h = gb(clip(F-0.8,0,1), r)`, subtracted from F's own blur to get an edge-only ring. **MOTION rule: do monochrome halation.** Add it to luminance only, or tint steel-blue at very low saturation. Red halation would break the "red never tints" rule. |
| **Film grain (Dehancer, FilmConvert Nitrate)** | Emulsion-modelled grain, with grain controls and camera profiles. **[src]** | Make a per-frame Gaussian noise field at **output resolution** and blur it slightly (sigma 0.6-1.0) for clumping. Weight it by `4*L*(1-L)`, the midtone curve, so grain is strongest in midtones. Add it after all scaling. ffmpeg fallback: `noise=alls=10:allf=t`. |
| **S_Shake / Universe Shake / Vegas Pan-Crop shake** | Camera-shake impact on hits. | 2D Perlin or sum-of-sines offsets plus a small rotation, decaying over about 6-10 frames after a beat (`A*exp(-t/τ)`). Overscan the frame by about 4% so edges never show. Add a little directional blur (`dblur`) along the shake vector. Use it once on the drop, not on every beat. |
| **S_Flicker** | Exposure or brightness flicker, like an old projector or a strobe. | Multiply the frame by `1 + a*noise(t)` with a=0.03-0.08. For a strobe, pulse to 1.3x on beats. `deflicker` is the inverse tool. |
| **S_Rays / CC Radial Fast Blur** | Light rays or zoom streaks from a point. | Radial blur: average the frame scaled about the centre by factors 1, 1+d, 1+2d... (N=12-24, d=0.005). Or warp to polar coordinates, blur along the radius, and warp back. Apply to the thresholded highlights only to get "rays". |
| **S_Zap / Saber** | Electric arcs, energy beams, neon strokes. Saber does glow falloff, outlines text and masks, and is free. **[src]** | Draw a polyline jittered by noise each frame, then apply the stacked glow above. For MOTION, a thin white or 1-px red stroke tracing the MMMM is the only acceptable use. |
| **S_Transitions / Motion Bro / transition packs** | Zoom-through, whip pan, spin, slide, luma fade, flash, glow dissolve. | `xfade` has 58 transitions built in, including fade, fadeblack, fadewhite, slide*, smooth*, zoomin, hblur, dissolve and pixelize. **[local]** A **whip pan** is the outgoing frame translated fast along x with a heavy `dblur`, cut at peak blur, then the incoming shot decelerating. A **luma fade** reveals the incoming shot where `L_out < t` as t ramps. A **flash** is a 1-2 frame cross to white over a log ramp. A **zoom transition** scales outgoing 1 to 1.5 with radial blur and incoming 0.7 to 1. |
| **Universe Glitch / RGB split** | Channel offset, block displacement, scanlines. | `rgbashift=rh=-6:bh=6` or `chromashift`. Block glitch is random row-band offsets with `np.roll`. **Off-brand for MOTION** except as a 2-frame accent. In B&W a channel split adds colour, so avoid it or use it at 1-2 px. |
| **Shift Channels / chromatic aberration** | Lens CA at the frame edges. | Scale the R and B channels about the centre by ±0.2-0.5%. That conflicts with strict B&W, so apply it before desaturation only to soften edges, or skip it. |
| **Optical Flares / BCC Lens Flare** | Lens flares with real textures, chromatic aberration, dirt, light tracking. **[src]** | A streak: a horizontal anamorphic smear `gb` with sigma_x much larger than sigma_y on thresholded highlights. Add a few ghost discs mirrored through the centre. Keep it white or steel. Use sparingly; flares read as 2010s. |
| **BCC Light Leaks** | Warm colour washes. | Animate a large-sigma blurred noise blob and screen it in. **Off-brand in colour.** In B&W, a soft white leak on a transition is acceptable. |
| **Element 3D** | Imports OBJ and C4D models and text into AE, with clones and particle arrays. **[src]** | Use Blender headless (`blender -b -P script.py`) to extrude the SVG logo, bevel it, light it with an HDRI, and render a PNG sequence with alpha. Or fake 2.5D in numpy (see 5). |
| **Heat Distortion / Turbulent Displace** | Organic wavy warp for heat haze or mirage. Amount 20-50 is subtle; animate Evolution and loop it. **[src]** | `cv2.remap` with displacement maps from 2-3 octaves of smooth noise drifting over time. ffmpeg: the `displace` filter with two noise maps. Keep the amplitude at 2-6 px for chic; anything more looks psychedelic. |
| **Echo / Time Displacement** | Trails (echo) or per-row time offsets (slit-scan). | Echo: `tmix=frames=5` or `lagfun=decay=0.9` (a bright-trail persistence). Time displacement: build `out[y] = buffer[t - k*y/H][y]` from a ring buffer. Use it on a dancer for one beat at most. |
| **Animation Composer (Mister Horse)** | A free preset library of text and shape animations and transitions. **[src]** | It is easing presets. See 5.2 for the curves, and implement `ease_out_expo`, `ease_in_out_cubic` and `spring` in Python. |

---

## 4. Making 320x568 phone footage look intentional at 1080x1920

The scale factor is about 3.38x. **Any detail the eye expects at 1080p is not in the plate.** The strategy is to (a) reconstruct some detail, (b) then *style over* what can't be reconstructed, so softness reads as a choice. **[craft]**

### 4.1 AI upscalers on a Linux CPU box
- **Real-ESRGAN (PyTorch).**
  - Install: clone the repo, `pip install basicsr facexlib gfpgan`, `pip install -r requirements.txt`, `python setup.py develop`. Needs Python 3.7+ and PyTorch 1.7+. It ships `inference_realesrgan_video.py`. **[src: GitHub]**
  - Models: `RealESRGAN_x4plus` (default, general), `realesr-general-x4v3` (tiny general model with a `-dn` denoise strength, **the best fit for noisy phone footage**), and `realesr-animevideov3` (animation). **[src]**
  - PyTorch runs on CPU, but slowly. **[craft; the README does not state CPU speed]**
- **realesrgan-ncnn-vulkan / realesrgan-ncnn-py.**
  - Install with `pip install realesrgan-ncnn-py` (Linux x86-64 wheels for Py 3.8-3.12). It needs `apt install libomp5 libvulkan-dev`. The project is **archived**, last release 2.0.0 (Dec 2023).
  - Models: animevideov3 x2/x3/x4, x4plus-anime, x4plus. It has `process_bytes` for raw ffmpeg pipes. **[src: PyPI]**
  - **CPU selection is not documented** on PyPI. Its sibling RIFE-ncnn uses `-g -1` for CPU. **[unverified for ESRGAN]** Without a Vulkan device, it may need a software Vulkan driver (`mesa-vulkan-drivers`/lavapipe). **[unverified]**
- **Topaz Video AI.** Linux builds exist only as alpha/beta (Ubuntu 22.04, NVIDIA CUDA). Users report a working CLI through ffmpeg. Support is unofficial, updates have slowed, and it is a paid license. **Not a practical option for a CPU box.** **[src: Topaz forum]**
- **Recommendation.**
  1. Run `realesr-general-x4v3` at x4 (320x568 to 1280x2272).
  2. Lanczos down to 1080x1920. The aspect ratios match within 0.2%.
  3. Run it only on **hero shots**, about 2-4 s of footage. CPU time per frame is likely seconds. **[estimate]**

### 4.2 Classic ffmpeg chain, for when the AI pass is too slow
Denoise **at native resolution first**: upscaling noise turns it into blocks. Then scale, sharpen gently, and add grain last, at output resolution. **[craft]**
```
ffmpeg -i in.mp4 -vf "hqdn3d=3:2:6:4,\
scale=1080:1920:flags=lanczos,\
cas=0.35,\
format=gray,eq=contrast=1.15:gamma=0.95,\
noise=alls=9:allf=t,format=yuv420p" -c:v libx264 -crf 16 -preset slow out.mp4
```
- **`nlmeans=s=3:p=7:r=15`** replaces `hqdn3d`. It is stronger and slower, and better on static shots.
- **`cas`** (contrast adaptive sharpen) gives fewer halos than `unsharp`. If you use `unsharp`, keep it mild, for example `unsharp=5:5:0.5`.
- **Over-sharpening** an upscale exposes the blocks. Stop as soon as edges look clean at 100%.
- All filters are present locally. **[local]** The parameter values are starting points. **[craft]**

### 4.3 Treatments that hide resolution [craft]
1. **High-contrast B&W, crushed blacks.** Blocks and compression mush live in the shadows, so crush them to black and let silhouettes carry the shot. This is also the Saint Laurent look.
2. **Diffusion / Pro-Mist plus monochrome halation.** These soften edges by design, so softness becomes "lens character".
3. **Heavy, fine grain at output resolution.** Grain adds high-frequency texture that the eye reads as detail, and it masks banding. It must be 1080p grain, never upscaled grain.
4. **Motion blur / frame blending.** Low-res footage judders and shows macro-blocks on motion. Blur on movement hides both.
5. **Keep plates small or moving.** Don't push in past 100% on a low-res plate. Every 10% of zoom costs another 10% of detail. Use the full frame or less: a plate floated in black negative space at 70% size reads as "framed".
6. **Halftone or dither texture** is an option for one graphic beat. It turns low-res into a print aesthetic.
7. **Speed.** Slow motion exposes low frame rates; fast footage hides resolution. Put low-res clips in fast sections and HD clips on the holds.

### 4.4 Frame interpolation
- **ffmpeg minterpolate.** `minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=60'` is on the FFmpeg wiki. The default mc_mode is `obmc`, so set `aobmc` explicitly. It is very slow and single-threaded; chunk it and run processes in parallel. It warps on complex motion. **[src]**
- **RIFE.**
  - **Practical-RIFE** (PyTorch, Python 3.11 or earlier) runs `inference_video.py --multi=4 --scale=1.0`. v4.25 is recommended, and `.lite` variants are cheaper. CPU support isn't stated. **[src]**
  - **rife-ncnn-vulkan** works on frame folders or frame pairs. `-g -1` = CPU, `-n` sets the target frame count, and `-s` sets the time step. It's a portable binary with no PyTorch. **[src]**
  - Interpolate *after* denoise and *before* upscale. That makes it about 10x cheaper at 320x568. **[craft]**
- **Interpolation fails on busy scenes** like crowds, strobes and hair. Use it on single-subject shots. Elsewhere, a frame-blended slow-mo (`tmix`) looks more "film" than a warped one. **[src + craft]**

---

## 5. 3D logo animation for "MMMM"

### 5.1 What makes a text logo feel dimensional and premium [craft unless marked]
- **Extrusion depth.** Use a thin extrusion, about 3-8% of the letter height. Thick extrusions read as 2000s broadcast.
- **Bevel.** A small chamfer or round bevel, about 1-2% of height. The bevel is where the light lives: it creates the bright edge line that sells "metal" or "glass".
- **Environment reflections.** Use an HDRI with a few hard, large softboxes on black. Chrome needs something to reflect. Template makers advertise "environment reflections, smooth bevels" and "light catching sharp edges" for this reason. **[src, template-level]**
- **Specular sweep (light wipe).** A single soft highlight band crosses the face and bevel once, over about 0.6-1.0 s, eased.
  - 2D fake: multiply a rotated linear gradient band (a smoothstep with a narrow width) by an "edge mask" of the logo (the logo alpha minus its eroded alpha gives the bevel ring), then add it.
  - Templates sell exactly "light sweeps with adjustable shine and glint". **[src]**
- **Glint.** At the sweep's end, a 4-point star or tiny anamorphic streak appears on one corner for 4-6 frames. Use it once only.
- **Depth of field.** Rack focus from blurred to sharp as the logo settles. In 2D, interpolate `gb(logo, σ(t))` toward σ = 0.
- **Motion blur** on any move (see the RSMB row). For a logo, blur along the known velocity vector analytically.
- **Bloom.** A subtle glow on the specular only, never on the whole logo.
- **Fake 2.5D without 3D software.** Render the logo alpha, then:
  1. stack offset copies, shifted by 1 px along the depth vector and darkening, to make the extrusion
  2. compute a bevel normal map from `-grad(gb(alpha, 2))`
  3. shade with `max(0, n·l)^k` against a moving light vector l(t)

  This gives a convincing specular sweep in numpy.
- **Real 3D.** Script Blender headless (`blender -b`): import the SVG, convert to mesh, extrude, bevel, apply an HDRI, render EEVEE with bloom and motion blur, and output PNGs with alpha. **[craft; Blender availability on this box not checked]**

### 5.2 Fluid motion principles for four overlapping Ms
- **Easing.** Nothing moves linearly. For entrances use ease-out (expo or cubic): fast start, long settle. For moves between positions use ease-in-out cubic. Logo animations typically run 30-60 frames on a custom curve. **[src]**
- **Anticipation.** Add 2-4 frames of reverse motion, or a slight scale-down, before the main move. **[src]**
- **Overshoot / spring.** For example, `x(t) = 1 - e^(-ζωt)·cos(ωt)` with ζ≈0.5-0.7 and 2-3 visible oscillations max. **Luxury rule: undershoot the overshoot.** Generic guides suggest 120-150% scale overshoot. **[src]** For a fashion brand, cap it at about 102-105%, or use an over-damped spring with no visible bounce. **[craft]**
- **Overlapping action and staggered offsets.** Animate the four Ms with a per-index delay, `t_i = t - i·Δ`, with Δ of 2-4 frames at 30 fps. That reads as one gesture rippling through, not four separate moves. Mild overlap means each M starts before the previous one finishes. **[src: stagger/offset by index]** For the MMMM trail, an echo works well: M1 is the solid M, and M2-M4 are trailing copies at decreasing opacity (100/60/35/15%) that converge onto M1. The trail is "motion" made visible. **[craft]**
- **Follow-through.** After the main M lands, the trailing Ms settle 2-6 frames later.
- **Motion blur on every move.** Without it, eased motion still strobes at 30 fps.
- **Hit the beat.** The logo lock (final position) lands *on* a downbeat, usually bar 8 beat 1 or the drop. The specular sweep starts on the next beat. The red accent (a thin rule or "b2b" mark) appears last, small, on an offbeat. **[craft]**

---

## 6. AI-assisted creative team with a closed learning loop

### What AI can genuinely do today
- **Gemini watches video.** It accepts YouTube URLs directly (`file_uri`), and by default samples **about 1 frame per second**. **[src, search-level; the official doc page could not be opened from the sandbox]** At 1 fps it **will miss sub-second cut detail**. Use it for "what happens, mood, shot types, overall pacing", not frame-accurate cut lists.
- **Claude can't watch video but can read frames precisely.** The workflow is to have ffmpeg extract frames and measure the cuts, then have Claude analyse them. **[craft]**
  - Cut detection: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -` prints cut timestamps, from which you can calculate ASL and cuts per bar. **[craft; select/showinfo standard]**
  - Contact sheet: `ffmpeg -i ref.mp4 -vf "fps=2,scale=270:-1,tile=6x5" sheet.png`.
  - Claude can then compare grade, framing, type, negative space and red usage against the brand rules, and turn the measurements into parameters for the effects library.
- **Code agents** (Claude Code, Codex) build and run the numpy/ffmpeg library and render variants.

### What stays human
- **Creative director (Jovanni).** Taste, final yes/no, music choice, what the brand will never do. Approves every publish.
- **Videographer.** Real camera moves, light, shutter angle, shooting at 60/120 fps for hero slow-mo, and collecting clean plates. **Fixing low resolution at capture beats every upscaler.**
- **VFX/editor.** Owns the effects library presets and the cut. Judges at full size, on a phone, at full speed.

### Lightweight reference-library loop [craft]
1. **Collect.** Use one shared sheet, with one row per reference: URL, brand, why it's good, a timestamp. Tag each row with technique tags (`hold`, `speed-ramp`, `graphic-match`, `flash`, `type-lockup`, `grain`).
2. **Analyse.** Gemini watches the reference and writes a 5-line description. ffmpeg plus Claude add measured data: ASL, cuts per bar against the track's BPM, a luminance histogram and the grain level.
3. **Encode.** Turn the findings into named presets in the effects library (for example `promist_soft`, `halation_mono`, `ramp_hero`, `whip_left`) and into rules in this bible.
4. **Make.** Render 2-3 variants per teaser from the presets.
5. **Review.** The CD scores each variant (1-5) on four questions: "expensive?", "on-beat?", "readable type?", "on-brand red use?". Record the scores and notes in the same sheet.
6. **Learn.** Every 2 weeks, raise the defaults of presets that scored 4-5 and retire the rest. Turn new corrections into hard rules, the way "red is an accent, never a tint" became one.

---

## Sources

**Opened directly (full page read in this session):**
- https://github.com/xinntao/Real-ESRGAN
- https://pypi.org/project/realesrgan-ncnn-py/
- https://github.com/hzwer/Practical-RIFE
- https://github.com/TNTwise/rife-ncnn-vulkan
- Local: `ffmpeg -filters` and `ffmpeg -h filter=xfade` (ffmpeg 6.1.1-3ubuntu5)

**Consulted via search-result summaries.** The sandbox blocked direct fetches of these domains, so treat specifics as second-hand:
- Murch, Rule of Six: https://cloud.wikis.utexas.edu/wiki/spaces/rtf318/pages/80022510/Murch+s+Rule+of+Six ; https://nofilmschool.com/2016/11/6-rules-good-cutting-according-oscar-winning-editor-walter-murch ; https://artlist.io/blog/eye-trace-and-rule-of-six-editing/
- Smith, AToCC (Projections 2012): https://ualresearchonline.arts.ac.uk/id/eprint/21187/
- Smith & Henderson 2008, Edit Blindness (JEMR): https://bop.unibe.ch/JEMR/article/view/2264
- Smith & Martin-Portugues Santacreu, Match-Action (Media Psychology): https://ualresearchonline.arts.ac.uk/id/eprint/21152/ ; https://eprints.bbk.ac.uk/14904/
- Magliano & Zacks 2011, event segmentation: https://pmc.ncbi.nlm.nih.gov/articles/PMC3208769
- Kuleshov effect: https://en.wikipedia.org/wiki/Kuleshov_effect ; https://experimental.psychologie.uni-mainz.de/files/2024/06/2017baranowski-kuleshov.pdf
- Music video cuts vs bars: https://arxiv.org/pdf/2108.00970
- Shot length, "I Took a Pill in Ibiza": https://repositorioinstitucional.ceu.es/handle/10637/8769?locale=en
- ASL decline: https://entertainment.time.com/2013/04/15/what-a-feeling-10-legacies-of-flashdance/slide/mtv-style-fiilmmaking
- Beat sync: https://spliceapp.com/blog/what-video-editors-optimize-drop-timing-edits ; https://artlist.io/blog/how-to-add-music-to-a-video/ ; https://licensing.routenote.com/blog/?p=9560 ; https://www.claudemarket.ai/skills/iart-ai/motion-design-skills/beat-sync-editing
- Saint Laurent films: https://theimpression.com/saint-laurent-fall-2022-ad-campaign/ ; https://theimpression.com/saint-laurent-summer-of-2021-ad-campaign-film-review/ ; https://www.documentjournal.com/2016/11/nathalie-canguilhem-anthony-vaccarellos-saint-laurent/
- Fashion film editing: https://www.kaltblut-magazine.com/spotlight-on-film-editor-dominik-braz-bittrichs-fashion-film-work-for-cartier-magda-butrym-and-yves-saint-laurent/ ; https://www.upwork.com/freelance-jobs/apply/Video-Editor-for-High-End-Social-Media-Content_~022065401886627609285/
- SHOWstudio: https://www.showstudio.com/project/moving_fashion ; https://www.missionmag.org/showstudios-nick-knight-25-years-of-fashion-and-film/
- RSMB: https://www.toolfarm.com/?p=6779 ; https://www.mactech.com/2014/04/14/kool-tools-reelsmart-motion-blur-5
- Twixtor and retiming: https://borisfx.com/blog/best-twixtor-alternative-in-2024/ ; https://community.adobe.com/bug-reports-728/optical-flow-and-frame-blending-haven-t-worked-on-speed-ramps-for-about-7-years-1331908
- Sapphire: https://www.cgchannel.com/2023/04/boris-fx-releases-sapphire-2023 ; https://www.provideocoalition.com/review-sapphire-2019-from-boris-fx/amp/
- Deep Glow: https://aescripts.com/deep-glow ; https://aescripts.com/learn/deep-glow-review-physically-accurate-glows-inside-after-effects
- Dehancer halation and bloom: https://blog.dehancer.com/articles/halation/ ; https://dehancer.com/learn/article/bloom-how-it-works
- Pro-Mist: https://www.lensrentals.com/buy/4-x-4-black-pro-mist-1-filter ; https://www.adorama.com/tf45pmb1.html
- Video Copilot: https://www.videocopilot.net/products/opticalflares/ ; https://blog.motionarray.com/learn/post-production/video-copilots-free-saber-plug-in-review/
- Turbulent Displace: https://www.storyblocks.com/resources/?p=26212 ; https://www.provideocoalition.com/cmg_hidden_gems_chapter_23_effects_roundup/
- Vegas velocity envelopes: https://www.dvinfo.net/article/post/using-envelopes-in-sony-vegas.html ; https://www.vegascreativesoftware.info/us/forum/velocity-envelopes--42688
- FilmConvert Nitrate: https://www.cined.com/jp/filmconvert-nitrate-next-generation-film-look-conversion/
- Animation Composer: https://aescripts.com/animation-composer-pro/ ; https://www.g2.com/sellers/mister-horse
- minterpolate: https://trac.ffmpeg.org/wiki/How%20to%20speed%20up%20/%20slow%20down%20a%20video?version=13 ; https://lists.ffmpeg.org/pipermail/ffmpeg-user/2021-January/051600.html
- Topaz on Linux: https://community.topazlabs.com/t/topaz-video-ai-linux-alpha-v3-2-3-1-l/43902 ; https://community.topazlabs.com/t/topaz-video-ai-linux-beta-v5-0-3-0-b/68739?page=4
- Motion principles: https://www.lynda.com/After-Effects-tutorials/Overshoot-staggering-animation/756333/776029-4.html ; https://skills.cat/skills/dylantarre/animation-principles/video-motion-graphics
- Logo reveal look: https://videobolt.net/author/luisbranco/chrome-stroke-logo-reveal ; https://www.framer.com/marketplace/components/7F4RCdpjSmqm4kJktNSQ/
- Gemini video: https://ai.google.dev/gemini-api/docs/generate-content/video-understanding ; https://discuss.ai.google.dev/t/gemini-2-0-video-understanding/58261

**Not verified:**
- S_Flicker, S_Zap and S_Rays as individually documented effects
- Motion Bro specifics
- Boiler Room editing conventions
- "Cut 1-2 frames early"
- Real-ESRGAN-ncnn CPU mode and CPU speeds
- Gemini's exact fps parameter syntax
