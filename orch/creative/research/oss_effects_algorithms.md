# Open-source video effects: how they work (clean-room notes)

Compiled 17 Oct 2026 for the MOTION fx library (`media/fx/mfx.py`). Every algorithm below is written up **in my own words** from reading the source; no code is copied. The licences are GPL/LGPL/CeCILL, so treat these notes as a spec and write fresh numpy code from them.

Conventions: images are float arrays in [0,1], shape (H,W,3). "lerp(a,b,t)" = a + (b-a)t. "screen(a,b)" = 1-(1-a)(1-b). Where a filter takes a 0..1 GUI value and rescales it internally, I give the internal mapping too.

Status: **verified** = I opened and read the file at the cited URL (commit = default branch on 17 Oct 2026). **Unverified** = not opened, from memory only.

Licence summary:
- frei0r: per-file GPL v2+ or v3+.
- FFmpeg libavfilter files read here: LGPL 2.1+.
- Blender: GPL-2.0-or-later.
- openfx-misc: GPL v2.
- G'MIC stdlib: CeCILL-C / CeCILL 2.1, dual-licensed.

---

## Part 1 — frei0r (github.com/dyne/frei0r, `src/filter/…`)

### 1.1 baltan — afterimage / ghost trail (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/baltan/baltan.cpp. GPL v3+. Original author Fukuchi Kentarou (EffecTV).
- **Look**: moving objects leave a soft, smeared trail of several faded copies, like a long-exposure echo.
- **Algorithm**:
  1. Keep a ring of 32 frame "planes" and a write index `p`.
  2. Each frame, store input/4 into plane `p`.
  3. Let `c = p mod 8`. Output = planes[c] + planes[c+8] + planes[c+16] + planes[c+24]. That is four quarter-weight frames spaced 8 frames apart.
  4. Overwrite plane `p` with output/4. This creates feedback: the output feeds back into the history, so trails decay geometrically instead of cutting off.
  5. p = (p+1) mod 32.
- **Parameters**: none exposed. Constants: 32 planes, stride 8, weight 1/4.
- **numpy notes**: use `buf = np.zeros((32,H,W,3))`. Output = `buf[[c,c+8,c+16,c+24]].sum(0)`. Making stride and depth into parameters gives you an "echo spacing" control. B&W-safe. This is close to our afterimage, but the fixed spacing gives *distinct* repeated copies instead of a smooth smear. Worth offering as a "strobe echo" mode.

### 1.2 vertigo — zoom/rotate feedback tunnel (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/vertigo/vertigo.c. GPL v2+. Fukuchi Kentarou.
- **Look**: the image melts into a spiralling, zooming tunnel of itself. The classic "dizzy" feedback.
- **Algorithm**:
  1. Keep a feedback buffer F, initialised to the first frame.
  2. Each frame, advance `phase += phase_increment`. Compute `dizz = 10·sin(phase) + 5·sin(1.9·phase + 5)`, which is a wobbling rotation amount in pixels.
  3. From dizz, centre (cx,cy) and `tfactor = (cx²+cy²)·zoomrate`, build an affine sampler. Its per-pixel step vector (vx,vy) is a slightly rotated and scaled unit step: vx ≈ (cx(cx−dizz)+cy²)/tfactor and vy ≈ dizz·cy/tfactor (wide frames; the formula swaps for tall frames). The start offset also wobbles by ±2 px: x gets 2cos(5·phase), y gets 2sin(6·phase).
  4. For each output pixel, sample F at that rotated/zoomed coordinate (nearest neighbour, clamped to the buffer).
  5. Output = (3·F_sample + input)/4. Store output back into F.
- **Parameters**: phase_increment default 0.02. zoomrate default 1.01; the GUI value is multiplied by 5 internally, and values >1 zoom in.
- **numpy notes**: build the inverse affine with `M = scale·R(θ)` around the centre, then use `map_coordinates` or a precomputed index grid. Keep the 3:1 feedback mix as a "persistence" parameter (0.6–0.9). It is very strong on B&W club footage and lights. **We don't have this.**

### 1.3 nervous — random frame reorder (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/nervous/nervous.cpp. GPL.
- **Look**: time stutters. It jumps back and forth through the last second of footage, playing short forward or backward runs.
- **Algorithm**:
  1. Keep a ring of the last 32 frames. `stock` = how many are filled.
  2. Default mode: when the run timer is 0, pick a random read index in [0,stock), a random stride in {−2,−1,+1,+2} (never 0) and a run length of 2–7 frames.
  3. Otherwise, step `read += stride` (wrapping inside stock) and decrement the timer.
  4. Output the stored frame at the read index. The alternative mode just picks a random stored frame every frame.
- **Parameters**: none exposed (32 frames, run length 2–7, stride ±1/±2).
- **numpy notes**: trivially cheap. Seed the RNG and drive it from beat markers so the stutters land on the kick. **We don't have this.** It is a strong "Carti" texture.

### 1.4 delaygrab — per-block time displacement (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/delaygrab/delaygrab.cpp. GPL.
- **Look**: different parts of the frame come from different moments, like a slit-scan. Rings mode makes the centre "now" and the edges "the past", so motion ripples outward.
- **Algorithm**:
  1. Keep a ring of 71 past frames.
  2. Split the frame into blocks (default 2×2 px). Each block gets a delay value from a "delay map".
  3. Map modes:
     - (1) random with a squared distribution, d = 16·u²;
     - (2) vertical stripes: |x−centre|/2;
     - (3) horizontal stripes: |y−centre|/2;
     - (4, default) rings: distance from centre / 2 (integer square root), in block units.
     - Clamp every value to [0,70].
  4. Each output block is copied from the frame `delay` steps back in the ring.
- **Parameters**: mode 4 (rings), block size 2, queue depth 71.
- **numpy notes**: store the history as `(D,H,W,3)` and index it with `hist[delaymap, yy, xx]` (fancy indexing). Any grayscale image can serve as the delay map, for example a gradient, a luma key or the text mask. openfx-misc **SlitScan** is the same idea with a continuous ramp (default: delay = gain·y, gain −10 frames), optionally blending the two nearest frames (https://github.com/NatronGitHub/openfx-misc/blob/master/SlitScan/SlitScan.cpp, verified). **We don't have this.**

### 1.5 delay0r — plain delay (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/delay0r/delay0r.cpp. GPL.
- **Algorithm**: keep timestamped frames, drop any older than `time − delay`, and output the oldest one left. That gives a fixed delay in seconds (default 0). It is mainly useful as a building block, for example mixing a delayed copy with the live frame by difference to make a "motion only" edge.

### 1.6 glow (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/glow/glow.c. GPL. The blur comes from `include/frei0r/blur.h` (box blur via a summed-area table; kernel size = fraction of the larger image side).
- **Algorithm**: B = box_blur(I, size), then out = screen(I, B) per channel.
- **Parameters**: blur, GUI value /20 → kernel fraction (default 0).
- **Note**: we already have deep_glow. The interesting extra is *screen* rather than add, which never clips. That suits B&W.

### 1.7 softglow (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/softglow/softglow.c. GPL v2+. Port of the GIMP softglow.
- **Algorithm**:
  1. L = (max(R,G,B)+min(R,G,B))/2 (HSL lightness).
  2. Sigmoid contrast: s = 255 / (1 + exp(−(2 + 20·sharpness)·(L/255 − 0.5))), then multiply by brightness.
  3. Blur the grey sigmoid image with a box blur.
  4. Blend the blur with the original by screen, overlay or add. GUI ranges: 0–0.33 screen, 0.33–0.66 overlay, above 0.66 add.
- **Defaults**: blur 0.5, brightness 0.75, sharpness 0.85, blend = screen.
- **numpy notes**: the sigmoid key is a better "highlight selector" than a hard threshold. Reuse it for flare and streak sources.

### 1.8 edgeglow (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/edgeglow/edgeglow.cpp. GPL v2+ (Salsaman).
- **Look**: edges are lit like neon, and the non-edge areas can be darkened.
- **Algorithm**:
  1. Per channel, Sobel magnitude ≈ |Gx|+|Gy| using the 3×3 [1,2,1] kernels. Clamp to 255.
  2. Take the edge lightness l = (max+min)/2 of the Sobel colour.
  3. If l > lthresh: new lightness = l·lupscale + (original lightness). Otherwise, if lredscale > 0: new lightness = original lightness × (1−lredscale).
  4. Rebuild the colour from the original pixel's hue and saturation with that new lightness (an HSL round trip).
- **Defaults**: lthresh 0, lupscale 0, lredscale 0. At these defaults the filter does nothing, so you must turn it up.
- **numpy notes**: for B&W, skip the HSL part. out = clip(Y + k·sobel(Y)·[sobel>t]) and darken non-edges by (1−r). That gives a cheap "outline glow" for type and silhouettes.

### 1.9 distort0r — sine grid warp (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/distort0r/distort0r.c. GPL.
- **Look**: wobbly, jelly-like warping that is stronger in the middle and pinned at the edges.
- **Algorithm**:
  1. On a coarse grid (every 8 px), compute source coordinates:
     - x' = x + amp·(W/4)·ex(x)·sin(freq·y/H + t)
     - y' = y + amp·(H/4)·ey(y)·sin(freq·x/W + t)
     - ex(x) = 4x/W·(1 − x/W) is a parabola: 0 at the edges and 1 in the middle (ey is the same in y).
  2. Bilinearly interpolate the coordinates within each 8×8 cell and sample nearest. Out-of-bounds samples are black.
  3. t = host time, or an internal accumulator advanced by `velocity` each frame.
- **Defaults**: amplitude 1.0, frequency GUI×200, speed GUI×2.
- **Note**: the edge pinning parabola is the useful idea, because the frame border never tears. We have liquid already; add the pinning to it.

### 1.10 glitch0r — horizontal block tear + bit-op colour (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/glitch0r/glitch0r.c. GPL.
- **Algorithm**:
  1. Walk rows top to bottom in bands. Each band gets a random height in [1, maxBlockHeight], a random horizontal shift in [1, maxShift], and a "pass" flag set with probability (1 − glitchChance).
  2. Glitched rows are rotated left by the shift, so the wrap-around shows on the right.
  3. Optional colour damage on the two halves of the row (shifted part and wrapped part), each picking a random op 0..colorIntensity:
     - 0: none
     - 1: bitwise invert
     - 2: OR with a random 32-bit seed
     - 3: XOR with the seed
     - 4: AND with the seed
- **Defaults**: maxBlockHeight = H/2, maxShift = W/2, colour intensity 3 (GUI ×5), chance = GUI×100 %.
- **numpy notes**: we have block_glitch. The XOR/AND-with-seed trick on uint8 is new and very "digital". In B&W, use it on luma only (`Y ^ seed_byte`).

### 1.11 rgbsplit0r (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/rgbsplit0r/rgbsplit0r.c. GPL.
- **Algorithm**: red is sampled from (x+dx, y+dy), green from (x,y) and blue from (x−dx, y−dy). Out of range = 0. dx = (GUI−0.5)·W/8 and dy = (GUI−0.5)·H/8. Defaults are 0.
- Already in our library. For B&W, apply the split to two luma copies only: one offset left in white, one offset right at 50% grey.

### 1.12 pixeliz0r (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/pixeliz0r/pixeliz0r.c. GPL.
- **Algorithm**: block average then fill. Block size = 1 + GUI·(W/2) in x and the same in y (default min(8, 1+W/2)). Partial edge blocks average over what is there.
- **numpy**: reshape to `(H/b, b, W/b, b, 3)` and take `mean((1,3))`.

### 1.13 scanline0r (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/scanline0r/scanline0r.cpp. GPL.
- **Algorithm**: process rows in pairs. Even rows are unchanged; the 150/128 gain is capped at the original value, so it is a no-op. Odd rows are multiplied by 64/128 = 0.5.
- **numpy**: `out[1::2] *= 0.5`. For a nicer CRT look, use sin² row modulation with 2–4 px period and a slight vertical blur first.

### 1.14 lenscorrection (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/lenscorrection/lenscorrection.c. GPL.
- **Algorithm**:
  1. r² = ((x−cx)²+(y−cy)²)·4/(W²+H²).
  2. m = 1 + r²·(c_center−0.5) + r⁴·(c_edges−0.5).
  3. Sample the source at centre + m·offset (nearest; outside = transparent black).
- **Defaults**: centre 0.5/0.5, both corrections 0.5 (which means zero distortion).
- Same model as FFmpeg's lenscorrection (k1,k2), see 3.4.

### 1.15 lightgraffiti — light painting (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/lightgraffiti/lightgraffiti.cpp. GPL.
- **Look**: bright moving lights (phones, lighters, LED wands) leave permanent painted streaks while the scene stays normal.
- **Algorithm**:
  1. Keep a background mean image: either the first frame, or a slow moving average with alpha "longAlpha" (default 1/128), or black.
  2. A pixel counts as a light source if all three hold:
     - max channel difference from the background > thresholdDifference;
     - sum of differences > thresholdDiffSum;
     - R+G+B > thresholdBrightness (default 450/765 ≈ 0.59).
  3. For light pixels, add the difference colour × (mean diff × sensitivity) into a float "light mask" accumulator (default sensitivity 0.2). The mask only grows. Optionally dim it each frame.
  4. Compose:
     - clamp the mask;
     - spill any channel overflow above 1 into the other channels, so over-bright red turns white;
     - boost the saturation of dim lights (factor 1 + sat·(1−mean), default 0.25);
     - **add** the result to the current frame and clamp.
- **numpy notes**: the B&W version is simple. `acc = max(acc·decay, where(Y>t & (Y−bg)>d, Y, 0))`, then out = clip(frame + gain·acc). With decay<1 it becomes a long light trail. Unlike lagfun it only keeps *lights*. **Very on-brand for club footage. We don't have this.**

### 1.16 cartoon (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/cartoon/cartoon.cpp. GPL.
- **Algorithm**:
  1. For each pixel, measure the largest squared RGB distance between opposite neighbours at distance d. Check four pairs: horizontal, vertical and both diagonals.
  2. If that contrast > 1/(1−triplevel) − 1, output black (an ink line).
  3. Otherwise output the colour posterised to 8 levels per channel (keep the top 3 bits).
- **Defaults**: triplevel ≈ 0.999 (so threshold ≈ 1000 in squared 0–255 units), diffspace d = 1 px.
- **numpy notes**: compute np.roll differences on luma and threshold. Pair it with posterize or Kuwahara (2.4) for a cel or comic look. B&W ink-line poster frames.

### 1.17 emboss (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/emboss/emboss.c. GPL (GIMP port).
- **Algorithm**:
  1. Bump map B = (R+G+B)/3.
  2. Normal: Nx = left column sum − right column sum (3 px each), Ny = bottom row sum − top row sum, and Nz = 6·255/width45.
  3. Light L = (cos az·cos el, sin az·cos el, sin el)·255.9.
  4. shade = N·L / |N|. If N·L < 0, shade = 0. Flat areas get Lz.
  5. Output grey shade.
- **Defaults**: azimuth 135°, elevation 30°, width45 = 10 (range 1–40).
- **Note**: this gives a metal or relief look on logos. It fits our steel-blue grade: multiply the shade by the steel tint.

### 1.18 posterize (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/posterize/posterize.c. GPL.
- **Algorithm**: LUT level(v) = 255·floor(n·v/256)/(n−1). n = 2 + GUI·48. Default GUI 5/48, which gives n = 7.
- We already have posterize_time; this is the spatial one.

### 1.19 twolay0r / threelay0r — adaptive threshold (verified)
- **Sources**: https://github.com/dyne/frei0r/blob/master/src/filter/twolay0r/twolay0r.cpp and https://github.com/dyne/frei0r/blob/master/src/filter/threelay0r/threelay0r.cpp. GPL.
- **twolay0r**: grey = (R+G+2B)/4.
  1. Build a histogram.
  2. Iterate the isodata threshold: start at t=127. Let low = mean of values below t and high = mean of values at or above t. Set t = (low+high)/2 and repeat until stable.
  3. Output pure black or white.
- **threelay0r**: the same grey value, but the thresholds are the 40th and 80th percentiles. Output is black / mid-grey (0x80) / white.
- **Why useful**: the threshold adapts every frame, so a stark 1-bit or 3-tone look stays balanced through strobe changes. Smooth the threshold over about 10 frames, or it pumps. **Strong B&W brand look; we don't have it.**

### 1.20 sharpness (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/sharpness/sharpness.c. GPL (MPlayer unsharp port).
- **Algorithm**: unsharp mask, out = src + amount·(src − box_blur(src, size×size)). Defaults: amount 0, size 3.

### 1.21 vignette (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/vignette/vignette.cpp. GPL.
- **Algorithm**:
  1. Aspect stretch: s = 1 + 4·(|aspect−0.5|·2)³, applied to x if aspect > 0.5, else to y.
  2. r = |scaled offset| / half-diagonal, minus clearCenter.
  3. If r ≤ 0, the factor is 1. Otherwise r' = r·(5(1−soft)² + 0.01). Factor = cos⁴(r') if r' < π/2, else 0.
  4. Multiply RGB by the factor.
- **Defaults**: aspect 0.5, clearCenter 0, soft 0.6. The cos⁴ falloff is the physically motivated part.

### 1.22 colorhalftone (verified)
- **Source**: https://github.com/dyne/frei0r/blob/master/src/filter/colorhalftone/colorhalftone.c. GPL (port of a JH Labs filter).
- **Algorithm**: per channel, using a screen angle (C 108°, M 162°, Y 90°):
  1. Rotate the pixel into screen space and snap it to the centre of its grid cell (grid = 2·radius·√2).
  2. For that cell and its 4 neighbours, read the channel value v at the cell centre. Dot radius = (1−v²)·half_grid·√2.
  3. Coverage = 1 − smoothstep(R, R+1, dot radius), where R is the distance to the dot centre. Take the min over the 5 cells.
  4. Channel = 255·coverage.
- **Defaults**: radius GUI 0.4 → ceil(4) px.
- We already have halftone. Two ideas to borrow: check the 5 neighbouring cells so big dots don't clip at cell borders, and use the smoothstep edge for antialiasing.

### 1.23 kaleid0sc0pe (verified README + core)
- **Source**: https://github.com/dyne/frei0r/tree/master/src/filter/kaleid0sc0pe (README.md, kaleid0sc0pe.cpp). GPL v3+, Brendan Hack.
- **Algorithm**:
  1. Polar angle around the origin: a = atan2(dy,dx) − start_angle. segment_width = 2π/N.
  2. Reference angle = |a| + width/2. Segment index k = floor(ref/width).
  3. Reflection angle = k·width. For odd k, subtract (width − 2·(ref − k·width)), which mirrors alternate wedges.
  4. Negate the angle depending on the sign of a. Rotate the offset by that angle and sample.
  5. If the result leaves the frame, reflect it back in (reflect_edges=true) or use the bg colour.
  6. By default the source wedge is the one pointing at the furthest corner, so it always has image data.
- **Defaults**: origin (0.5,0.5), segmentation 16/128·128 = 16 segments, reflect edges on.
- **Note**: we have mirror but not N-fold symmetry. It is easy to vectorise with `np.arctan2`.

### 1.24 elastic_scale (verified)
- **Source**: https://github.com/dyne/frei0r/tree/master/src/filter/elastic_scale. GPL.
- **Look**: 16:9 → 9:16-style stretch that keeps the centre undistorted and squeezes the sides, like "smart stretch".
- **Algorithm**:
  1. Pick a centre band [L,R] that scales linearly by factor f. The outer bands map nonlinearly by ratio(t) = t + a·sin(πt − π), with t in [0,1] across each side band and a = GUI·0.4 − 0.2.
  2. Precompute a per-column source x and interpolate linearly between the two nearest columns.
- **Defaults**: centre 0.5, linear width 0, linear factor 0.7, nonlinear 0.7125.
- **Use**: reformatting wide club footage to 9:16 stories without visibly squashing faces. A practical utility.

### 1.25 Bonus frei0r filters worth knowing (verified by reading their headers and params)
- **pixels0rt** (src/filter/pixels0rt/pixels0rt.c, GPL v2+, 2026):
  - Walk each column (or row). Start a new segment when the mean |ΔRGB|/765 between the segment's first pixel and the current pixel exceeds the threshold (default 0.3), or at transparency.
  - Counting-sort each segment by grey = (R+G+B)/3, optionally reversed.
  - Directions: vertical top/bottom, horizontal left/right.
- **squigglevision** (src/filter/squigglevision/squigglevision.cpp, GPL v3+, 2026): the "boiling line" animation look.
  1. Build a coarse grid with cell = 4 + scale·124 px (default scale 0.15 → about 23 px).
  2. Each grid point gets a displacement vector at angle = value_noise(i+frame·π, j+frame·e)·4π and magnitude strength·0.025·W (or H), default strength 0.08.
  3. The noise only re-rolls at fps = 30·0.2 = 6 changes per second.
  4. Interpolate the vectors across the frame and displace.
  - **Good for hand-drawn type on promo.**
- **gateweave** (gateweave.c): random target offsets re-chosen every `interval` (default 0.6), max move 0.2 (GUI) in x and y, with smooth interpolation between keys. This is film gate weave. Our `shake` covers some of it, but the slow hold-then-drift pattern is different.
- **filmgrain** (filmgrain.c): per-channel grain amounts plus a softening blur and a "dust" amount.
- **shake0scillate**: sinusoidal x/y/rotation oscillation, each with its own amount and speed, plus a mirror-extend edge mode.
- **ntsc** (crt_core.c / crt_ntsc.c): a full composite-signal NTSC simulation (encode to a 1D signal, add noise, decode). Heavier than our vhs. Treat as reference only.

---

## Part 2 — Blender compositor (github.com/blender/blender, GPL-2.0-or-later)

Files read:
- `source/blender/nodes/composite/nodes/node_composite_glare.cc`
- `…/node_composite_lens_distortion.cc`
- `…/node_composite_kuwahara.cc`
- `…/node_composite_defocus.cc`
- `source/blender/compositor/shaders/compositor_glare_*.glsl`
- `compositor_radial_lens_distortion.glsl`
- `compositor_kuwahara_classic.glsl` and `…_anisotropic.glsl`
- `compositor_defocus_radius_from_depth.glsl`
- `source/blender/compositor/cached_resources/intern/fog_glow_kernel.cc`

### 2.1 Glare node — shared front and back end (verified)
- **Inputs and defaults**:

  | Input | Default | Range |
  |---|---|---|
  | Type | Streaks | Streaks, Fog Glow, Ghosts, Simple Star, Bloom, Sun Beams, Kernel |
  | Quality | Medium | High = full res, Medium = ½, Low = ¼ |
  | Highlights Threshold | 1.0 | |
  | Smoothness | 0.1 | |
  | Clamp | off | Maximum 10 |
  | Strength | 1 | |
  | Saturation | 1 | |
  | Tint | white | |
  | Size | 0.5 | |
  | Streaks | 4 | 1–16 |
  | Streaks Angle | 0 | |
  | Iterations | 3 | 2–5 |
  | Fade | 0.9 | 0.75–1 |
  | Color Modulation | 0.25 | |
  | Diagonal Star | on | |
  | Sun Position | (0.5,0.5) | |
  | Jitter | 0 | |

- **Highlight extraction**:
  1. Downsample to the quality size by 2×2 or 4×4 averaging.
  2. Convert to HSV.
  3. Clamp V between threshold and max with a *smooth* clamp. The smooth min is a quadratic polynomial smooth-min, min(a,b) − h²·k/4 with h = max(k−|a−b|,0)/k. The smoothness is limited so that values at the threshold still map exactly to the threshold.
  4. V ← clamped − threshold. Convert back to RGB.

  The point is soft-kneed highlights, so the glare has no hard edge.
- **Mix**: glare HSV saturation × Saturation, then output = max(input,0) + glare·tint·strength/normalisation. The mix is additive.
- **numpy notes**: for B&W we work in luma. Smooth-clamp Y and subtract the threshold. Our footage is LDR (0–1), so use a threshold around 0.7–0.85 instead of 1.0.

### 2.2 Glare: Streaks (verified)
- **Look**: anamorphic or star-filter lines radiating from highlights.
- **Algorithm** (per streak k of N):
  1. Direction angle θ_k = streak_angle + 2πk/N, unit vector d = (cos θ, sin θ).
  2. Run 'Iterations' passes. In pass i, the magnitude m = 4^i px.
  3. In each pass, every pixel = ½·[centre + f·s(+1·m·d) + f²·s(+2·m·d) + f³·s(+3·m·d)], where s() is a bilinear sample (zero outside) and f = fade^m.
  4. Colour modulation (spectral fringe): with c = 1 − colmod^(i+1), the three neighbours have their (G,B), (R,G) and (R,B) channels multiplied by c respectively. **Skip this for MOTION**, because it makes coloured fringes.
  5. Sum all N streak images, then scale by 1/(5+1−iterations) so short streaks keep similar brightness.
- **numpy notes**:
  - each pass is 3 shifted-and-weighted copies; use fractional shifts with `scipy.ndimage.shift` or a two-tap lerp;
  - 4 streaks × 3 passes = 36 shifts, which is cheap at ½ res;
  - this gives the "Drake album cover" star glints on jewellery and phone lights;
  - **we have rays/lens_flare but not true streak glare**.

### 2.3 Glare: Simple Star (verified)
- **Algorithm**:
  - Axis-aligned version, per column:
    1. For each iteration i, run a causal recursive filter top→bottom: v[y] = lerp(v[y], (v_out[y−i] + v_in[y+i])/2, fade).
    2. Then run an anti-causal one bottom→top the same way.
    3. Do the same per row.
    4. Add the vertical and horizontal results.
  - Diagonal version: run the same recursion along both diagonals.
- **Note**: recursive (IIR) passes give long exponential tails for very little compute. It is a cheap 4- or 8-point star.

### 2.4 Glare: Ghosts (verified)
- **Look**: lens-flare ghost blobs mirrored through the frame centre.
- **Algorithm**:
  1. Base ghost:
     - blur the highlights twice, with r_small = 16/quality_factor and r_big = 2·r_small;
     - sample the small blur with coordinates scaled about the centre by 2.13 (a shrunk copy);
     - sample the big blur scaled by −0.97 (flipped through the centre);
     - attenuate each by max(0, 1 − 2·dist_to_centre·|scale|) and sum.
  2. Accumulate over iterations 1..n−1 (iteration 0 is skipped). Each iteration adds 4 rescaled copies of the previous result:
     - scales come from an arithmetic progression of 4n values from 2.1 down towards 0, shifted by 0.5 for odd n;
     - every odd copy has its scale replaced by −0.99/scale (flipped and inverted);
     - each copy is attenuated by max(0, 1 − 2d·|scale|)/4;
     - copies 2–4 get the channel modulation (skip it).
- **numpy notes**: scaling about the centre is a single `map_coordinates` call with `(uv−0.5)·s+0.5`. In B&W the ghosts read as soft grey discs, which suits the "eyes" teaser.

### 2.5 Glare: Fog Glow (verified)
- **Look**: a physically based wide halo around highlights (the eye's own glare).
- **Algorithm**:
  1. Convolve the highlights in the frequency domain with a kernel the size of max(W,H). Zero-pad to the image size + kernel − 1.
  2. The kernel is from Spencer et al. 1995, "Physically-Based Glare Effects for Digital Images", eq. 5. With θ = distance in degrees = pixel radius × (FOV / kernel_size):
     - f0 = 2.61e6·exp(−(θ/0.02)²)
     - f1 = 20.91/(θ+0.02)³
     - f2 = 72.37/(θ+0.02)²
     - K = 0.384·f0 + 0.478·f1 + 0.138·f2
  3. Normalise by the kernel sum.
  4. FOV = lerp(180°, 10°, Size^(1/3)), so a bigger Size means a narrower FOV and a wider-looking glow.
- **numpy notes**: build K once per size, then `np.fft.rfft2` the image and kernel and multiply. 1080p is about 0.3 s on CPU, so cache the kernel FFT. The formula is from a published paper, not from Blender's code, so it is safe ground. **This is a better "promist / deep glow" base than Gaussian stacks.**

### 2.6 Glare: Bloom (verified)
- **Algorithm** (after the Call of Duty: Advanced Warfare talk by Jimenez, 2014):
  1. Chain length = floor(log2(min(W,H)·Size)).
  2. Downsample repeatedly by 2 with the 13-tap filter. The weights are 4 for the centre 2×2 group and 1 for each of 4 overlapping corner groups, out of 8 (= 0.5 + 4×0.125).
  3. The **first** downsample uses a Karis average: weight each group by 1/(1+luma), which suppresses fireflies.
  4. Upsample back with a 3×3 tent filter, adding each level to the next larger one.
  5. Normalise and add to the image.
- **numpy notes**: we probably already approximate this in deep_glow. The Karis weight is the bit to steal, because it stops single bright pixels (LED) from pulsing.

### 2.7 Glare: Sun Beams (verified)
- **Algorithm**: for each pixel:
  1. March towards the source point S. steps = min(max_steps, distance in px), where max_steps = Size·diagonal.
  2. Sample along the line. Weight each sample by (1 − i/steps)², a quadratic falloff away from the pixel.
  3. Accumulate a weighted average and stop when leaving the frame.
  4. With jitter, the sample positions get a per-pixel hash offset and the step count is cut by (1−jitter) for speed.
- **Note**: we have `rays`. The quadratic falloff and the per-pixel jitter (noise instead of banding) are worth copying. Compare openfx-misc GodRays (Part 5), which uses 2^steps transformed copies instead.

### 2.8 Lens Distortion node (verified)
- **Inputs**: Type (Radial / Horizontal), Distortion (default 0, range −0.999..1), Dispersion (0..1), Jitter (off), Fit (off).
- **Radial model**:
  1. uv = scale·(p − centre)/centre, r² = uv·uv.
  2. Per-channel distortion: green = D, red = D + disp/4, blue = D − disp/4, all clamped and then multiplied by 4 (DISTORTION_SCALE).
  3. Distortion scale s(d, r²) = 1/(1 + sqrt(max(0, 1 − d·r²))). Distorted coordinate = (uv·s + 0.5)·size.
  4. If any channel has d·r² > 1, output transparent black.
  5. **Dispersion is integrated, not just shifted**:
     - to get red, step from the red distortion to the green one in n steps (n ≈ pixel separation + 1);
     - at each step t = (i + 0.5)/n, sample the image at that intermediate distortion;
     - add (1−t)·sample into red and t·sample into green;
     - do the same between green and blue;
     - finally multiply the colour by 2/n.

     This turns RGB "ghost copies" into a smooth smeared fringe.
  6. Jitter replaces the 0.5 with a random hash, using about √(distortion+1) steps (minimum 2). That gives a grainy, noisy fringe.
  7. Fit scale: 1/(1+2·maxD) if Fit, else 1/(1+maxD).
- **Horizontal mode**: R and B are sampled ±(dispersion·5/W) horizontally (a plain shift).
- **numpy notes**: the integration idea also helps our B&W rgb_split. Integrating several luma copies along the distortion path gives a "motion-smear barrel" look without colour. This is our fisheye plus a dispersion smear.

### 2.9 Kuwahara (verified)
- **Inputs**: Size default 6, Type default Anisotropic, Uniformity 4, Sharpness 1, Eccentricity 1, High Precision off.
- **Classic**: for each pixel:
  1. Look at 4 overlapping (r+1)×(r+1) quadrants (TL, TR, BL, BR) that share the centre pixel.
  2. Compute each quadrant's mean and the variance summed over RGB.
  3. Output the mean of the lowest-variance quadrant.
  4. Optionally use summed-area tables for O(1) per pixel.
- **Anisotropic** (Kyprianidis, Kang & Döllner 2009, plus the 2010 polynomial-weights paper and the 2011 multi-scale sector weights):
  1. Build a structure tensor from Sobel gradients and smooth it with a Gaussian ("Uniformity").
  2. From its eigenvalues, take the orientation (minimum-change eigenvector) and anisotropy A = (λ1−λ2)/(λ1+λ2).
  3. The filter window is an ellipse aligned to that orientation. It is elongated by A, controlled by eccentricity.
  4. Split the ellipse into 8 sectors with smooth polynomial weights.
  5. Per-sector weighted mean and variance. The output is a weighted mean of sector means with weight ∝ 1/(1+σ)^q, where Sharpness sets q.
- **Look**: painterly, oil-paint flattening that keeps edges sharp. Excellent on faces in B&W.
- **numpy notes**: classic Kuwahara with `uniform_filter` on I and I² is about 10 lines and fast. The anisotropic version is heavier but doable at ½ res. **We don't have it.**

### 2.10 Defocus (verified, overview)
- Radius from depth uses the Potmesil & Chakravarty 1981 thin-lens model:
  - image distance of the object: Vu = f·z/(z − f);
  - circle of confusion: C = |(Vu − V_focus)·f/(N·Vu)|, converted to px by pixels-per-metre of the sensor and clamped to max radius.
- The radius map is dilated (so foreground blur can spread), then a variable-size bokeh blur runs with a kernel image built from blade count, rotation and roundness (`COM_bokeh_kernel`).
- **numpy notes**: we have no depth maps, so use a mask (subject = 0 radius, background = R). Use a polygon bokeh kernel for the "hexagon highlight" look and a variable-radius gather (quantise the radius into ~6 bands, blur each band, then composite).

---

## Part 3 — FFmpeg libavfilter (github.com/FFmpeg/FFmpeg, LGPL 2.1+)

### 3.1 lagfun — max-hold decay trail (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_lagfun.c
- **Algorithm**: out_t = max(in_t, out_{t−1}·decay) per pixel and plane. Default decay 0.95, all planes.
- **Look**: bright things leave trails while dark things vanish instantly. It is the cheapest light trail.
- We have afterimage; check that it uses *max*, not a mix. A max-hold is what keeps the blacks clean, which is essential for B&W.

### 3.2 tmix — weighted temporal average (verified, in vf_mix.c)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_mix.c
- **Algorithm**: out = Σ w_i·frame_{t−i} · (1/scale). If scale = 0 it defaults to 1/Σw.
- **Defaults**: frames 3, weights "1 1 1". The weights can be negative, which gives an edge or difference echo. Example: "1 −1" shows motion only.
- **Use**: fake shutter or motion blur, and a "stutter-echo" with weights like "1 0 0 0.5 0 0 0.25".

### 3.3 minterpolate — overview (verified options only)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_minterpolate.c
- **Options**: fps 60, mi_mode mci (others dup/blend), mc_mode obmc (overlapped block MC) or aobmc, me_mode bilat (bilateral) or bidir, me = epzs (also esa/tss/tdls/ntss/fss/ds/hexbs/umh), mb_size 16, search_param 32, vsbmc 0, scene-change detect fdiff with threshold 10.
- **How it works**:
  1. Block motion estimation between neighbouring frames gives a vector per 16×16 block.
  2. Clean the vectors up.
  3. Synthesise intermediate frames by overlapped-block motion compensation, warping both neighbours toward time t and blending with a window.
  4. On a scene cut, fall back to frame blending.
- **Use**: "Twixtor-style" smooth slow motion and speed ramps. Outside numpy scope; call ffmpeg directly. Its artefacts (warping limbs) are themselves a look.

### 3.4 lenscorrection (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_lenscorrection.c
- **Algorithm**:
  1. r² = ((x−cx)² + (y−cy)²)/(¼(W²+H²)), which is normalised so the half-diagonal = 1.
  2. m = 1 + k1·r² + k2·r⁴, source = centre + m·offset.
  3. A precomputed fixed-point per-pixel table holds m. Nearest or bilinear sampling. Unmapped pixels are filled with colour fc (default transparent black).
- **Defaults**: cx = cy = 0.5, k1 = k2 = 0 (range −1..1).
- **Note**: negative k1 = barrel (fisheye-ish) and positive = pincushion. Animating k1 from 0 to −0.4 on a drop gives a "lens punch-in". We have fisheye; add k2 for the moustache shape.

### 3.5 displace (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_displace.c
- **Algorithm**: three inputs (source, xmap, ymap). out(x,y) = src(x + xmap(x,y) − 128, y + ymap(x,y) − 128), with 8-bit maps centred on 128.
- **Edge modes**: blank (black), smear (clamp, the default), wrap (mod) and mirror.
- **Use**: any greyscale video becomes a warp. Text displacing footage, noise for heat haze, or a ripple render. Our liquid/warp already does this internally; expose an "external map" input and the 4 edge modes.

### 3.6 chromashift / rgbashift (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_chromashift.c (both filters live there).
- **chromashift**: shifts the Cb and Cr planes by integer px (cbh, cbv, crh, crv, range −255..255). Edge = smear or wrap.
- **rgbashift**: independent integer h/v shifts for R, G, B and A with the same edge modes.
- **Note**: shifting chroma rather than RGB keeps the luma sharp, so the image stays readable. For B&W this is irrelevant except as a VHS-colour-bleed variant.

### 3.7 deflicker (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_deflicker.c
- **Algorithm**:
  1. Mean luma per frame comes from a histogram.
  2. Keep a window of `size` frames (default 5, range 2–129).
  3. Combine the window's means with one of: am (arithmetic, default), gm, hm, qm, cm, pm (power) or median.
  4. Gain f = smoothed / current mean, applied to the current frame (output = in·f, clipped).
- **Use**: a utility for phone footage under PWM club lights. The inverse is also useful: deliberately *exaggerate* flicker (f^−k) for a strobe look.

### 3.8 xfade (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_xfade.c
- **Options**: transition default `fade`, duration 1 s, offset 0.
- **Transition list**: custom (expression), fade, wipeleft, wiperight, wipeup, wipedown, slideleft, slideright, slideup, slidedown, circlecrop, rectcrop, distance, fadeblack, fadewhite, radial, smoothleft, smoothright, smoothup, smoothdown, circleopen, circleclose, vertopen, vertclose, horzopen, horzclose, dissolve, pixelize, diagtl, diagtr, diagbl, diagbr, hlslice, hrslice, vuslice, vdslice, hblur, fadegrays, wipetl, wipetr, wipebl, wipebr, squeezeh, squeezev, zoomin, fadefast, fadeslow, hlwind, hrwind, vuwind, vdwind, coverleft, coverright, coverup, coverdown, revealleft, revealright, revealup, revealdown.
- **Conventions**: progress P runs **1 → 0** over the transition (P = 1 − elapsed/duration). mix(a,b,t) = a·t + b·(1−t), with a = outgoing frame and b = incoming frame.
- **fadeblack**: with phase 0.2, out = mix( mix(A, black, smoothstep(0.8, 1, P)), mix(black, B, smoothstep(0.2, 1, P)), P ). A dips fully to black before B rises.
- **dissolve**: noise threshold. s = rand(x,y)·2 + 2P − 1.5, and each pixel is A if s ≥ 0.5 else B. That is a hard, per-pixel random dissolve, a very "digital" look.
- **pixelize**: d = min(P, 1−P) and the block size grows to a maximum at mid-transition (sq ∝ ceil(50d)/50·min(W,H)/10). Both frames are block-sampled at that size and cross-mixed by P.
- **hblur**: per row, a box blur whose width = 1 + (W/2)·prog, with prog peaking at P = 0.5. The blurred A and B are mixed by P, so it reads as a horizontal smear-through. Whip-pan-like.
- **zoomin**: A is sampled with coordinates scaled about the centre by zf = smoothstep(0.5, 1, P) (zooming into A), then mixed toward B with smoothstep(0, 0.5, P).
- **radial**: a clock wipe. s = atan2(x−W/2, y−H/2) − (P − 0.5)·2.5π, and pixel = mix(B, A, smoothstep(0, 1, s)).
- **wind (hlwind etc.)**: a per-row random offset r = rand(0,y) feeds a smoothstep edge, so the wipe front is ragged. **Good, cheap, B&W-friendly.**
- **squeeze**: the outgoing frame is scaled to 0 along one axis while the incoming one shows.

### 3.9 vibrance (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_vibrance.c
- **Algorithm**:
  1. sat = max(RGB) − min(RGB), luma = 0.2127R + 0.7152G + 0.0722B.
  2. Per channel c: gain = 1 + I·bal_c·(1 − sign(I·bal_c)·sat).
  3. Channel = lerp(luma, c, gain).
- **Defaults**: intensity 0 (range −2..2) and balances 1. Low-saturation pixels are boosted most. With negative intensity it is a gentle "desaturate the colourful bits" control, which is handy for pulling stray stage colour toward B&W without killing skin tones completely.

### 3.10 edgedetect (verified)
- **Source**: https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_edgedetect.c
- **Algorithm**: Canny.
  1. Gaussian blur, then Sobel.
  2. Non-maximum suppression (thin edges to 1 px along the gradient direction).
  3. Double threshold with hysteresis: high 50/255 and low 20/255.
- **Modes**: wires (white/grey lines on black, the default), colormix (edges mixed over the image) and canny (per plane).
- **Use**: "wires" on B&W footage is a ready-made line-art look. Combine it with lagfun for neon line trails.

---

## Part 4 — G'MIC (github.com/GreycLab/gmic, `src/gmic_stdlib.gmic`, CeCILL-C or CeCILL 2.1)

Verified: https://raw.githubusercontent.com/GreycLab/gmic/master/src/gmic_stdlib.gmic (commands `glow`, `halftone`, `pixelsort`, `_pixelsort`).

### 4.1 pixelsort
- **Algorithm**:
  1. Inputs: a *sorting criterion* image (default = sum of channels) and a *mask* (default = all on).
  2. For each row (axis x; y, z, xy and yx are done by permuting axes), find contiguous runs where the mask is on.
  3. Sort each run's pixels by the criterion in increasing or decreasing order.

  The help example makes the mask from "norm ≥ 30%", so only bright regions sort. The method credits satyarth.me's pixel-sorting article.
- **Note**: matches our pixel_sort. The idea to copy is the **separate criterion and mask images**. Sort by luma but mask with a person matte or a brightness band. That gives control over *where* the streaks happen.

### 4.2 halftone
- **Defaults**: levels 5, dark size 8, bright size 8, shape 5 = inverted circle (others: square, diamond, circle, inverted square, inverted diamond), smoothness 0.
- **Algorithm**:
  1. Quantise each channel to n levels.
  2. For each level k, build a tile of size s_k = round((dark·k + bright·(n−1−k))/(n−1)) holding a distance-field shape (distance to the tile centre, using the chosen metric).
  3. Threshold that tile at k/(n−1.1) to get a dot of the right area.
  4. Tile it across the image and paste it where the quantised level equals k. Optionally blur by the smoothness.
- **Note**: the dot *pitch* changes with tone, not only the dot size. That gives a "screen-printed gig poster" look that differs from classic AM halftone. Worth a variant in our halftone.

### 4.3 glow
- **Default**: amplitude 1%. As read: it splits off the opacity, blurs a copy by the amplitude, normalises the blur to the original's range, and blends it back with G'MIC's `edges` blend mode (smoothness 1).
- **Unverified**: the exact maths of that blend.

(gmic-community filters such as VHS and glitch were not opened; **unverified**.)

---

## Part 5 — Natron openfx-misc (github.com/NatronGitHub/openfx-misc, GPL v2)

- **Glow**: openfx-misc has **no Glow plugin** (checked the repo tree). Natron's glow options live in the community PyPlugs repo (github.com/NatronGitHub/natron-plugins):
  - **fxT_Glowy** (Filter/fxT_Glowy, verified README): tolerance threshold, then a glow built from a stack of blurs whose radius grows exponentially (a "more realistic falloff"), then a plus/screen/under blend, tint, gain, saturation and an anamorphic option.
  - Also present (not opened): GLSL/Blur/Bloom_GL and Crok_bloom_GL.
  - **Takeaway**: an exponentially spaced blur stack (r, 2r, 4r, 8r… summed with decreasing weights) is the common glow recipe. It approximates the Spencer kernel in 2.5.
- **GodRays** (GodRays/GodRays.cpp, verified):
  - average the image over 2^steps transformed copies (default steps 5 = 32 copies), interpolating the transform between identity and the user transform (scale about the light centre, plus optional rotation or translation);
  - each copy is multiplied by a colour that runs from fromColor to toColor. Their interpolation is geometric: col1·(col2/col1)^(i/n), optionally done in a gamma space;
  - with toColor black and gamma 1 the decay is exponential, like real crepuscular rays;
  - also usable as a fixed-sample directional or zoom blur.
- **SlitScan** (SlitScan/SlitScan.cpp, verified): per-pixel retime.
  - time offset = offset + gain·f(x,y), where f is a vertical ramp (default horizontal slit, 0 at the bottom and 1 at the top), a horizontal ramp, or a retime map image;
  - gain default −10 frames;
  - nearest-frame or interpolated sampling;
  - reference: Golan Levin's slit-scan catalogue.
- **Shadertoy** (Shadertoy/Shadertoy.md, verified): runs Shadertoy 0.8.8 single-pass fragment shaders (GLSL ES 1.0, no multipass, no sound) with iChannel inputs.
  - Presets folder (verified listing): CRT, barrel blur chroma, bloom postproc, bokeh disc, chromatic aberration, CMYK halftone, cubify, DoF bokeh, fisheye, film grain, glitch01/02/A/B, HDR bloom, image cel-shade and many more.
  - **Licence note**: each preset carries its *own* Shadertoy author licence, often CC BY-NC-SA. Do not port them; read them only for ideas.
- Other notable openfx-misc plugins: TimeBlur (shutter accumulation), FrameBlend (temporal min/max/average), Anaglyph, ReConverge, Rand (noise generator), Distortion (IDistort/STMap), CImg wrappers (Bilateral, Guided filter, RollingGuidance, SharpenShock, Median, Erode, Plasma). Only the tree and descriptions were read.

---

## Part 6 — Edit-language breakdown (craft knowledge, not from source code)

**Status: craft knowledge.** This comes from general familiarity with these artists' visual output up to my training cutoff. It is not a frame-by-frame study, so treat it as a starting brief and check it against references in Gemini.

### Drake / OVO
- **Colour → B&W translation**: the colour language is dark, warm-black, low-key, with skyline night palettes and lots of negative space. Convert to deep blacks with highlights held back, a slight steel lift in the shadows, and no crushed whites.
- **Lens**:
  - long lenses and slow push-ins;
  - wide anamorphic-style frames with horizontal flares and streaks off car lights and city light;
  - soft halation or promist on highlights.
  - Borrow: Blender-style **streak glare with 2 horizontal streaks** (Streaks=2, angle 0), monochrome.
- **Speed**: languid. Slow motion (60→24 conform), long held shots, slow drone glides over the city. It rarely cuts on every beat; it cuts on phrase changes.
- **Transitions**: hard cuts and dips to black, plus fade-from-black title cards. Very few flashy wipes.
- **Typography**:
  - restrained;
  - small, widely tracked caps or a single serif/blackletter-adjacent word, centred;
  - lots of empty frame around it;
  - the owl / OVO mark is used tiny.
  - Maps directly onto Bodoni Moda caps with tight leading, small, plus one thin red rule.
- **Camera**: locked-off or slow dolly. Silhouettes against windows and light sources, and shooting through glass.
- **Borrowable for MOTION**: low-key B&W grade, fog glow on practicals, 2-point horizontal streaks, slow push-ins (our zoom with expo ease), dip-to-black between artists, tiny centred type.

### Playboi Carti (Whole Lotta Red / Opium era)
- **Colour**: mostly already high-contrast B&W or harsh single-colour (red) punk aesthetics. **Use the B&W part and drop the red flood**; red stays as the small MMMM accent only.
- **Texture**:
  - photocopy and xerox grain;
  - 1-bit thresholding (→ **twolay0r/threelay0r adaptive threshold**);
  - halftone and posterisation;
  - VHS and camcorder artefacts;
  - fisheye skate-video lens (→ lenscorrection k1 < 0, or fisheye).
- **Speed and time**:
  - stutter and repeat frames (→ **nervous**, **tmix echo**);
  - abrupt speed ramps;
  - strobe flashes on the beat;
  - very short shots, 2–8 frames, in bursts.
- **Transitions**: flash frames (white or inverted single frames), hard glitch cuts (→ glitch0r tears with XOR luma), and zoom-punch cuts.
- **Typography**: gothic or blackletter, distressed, often huge and cropped off-frame, jittering (→ **squigglevision** boil on type). Also stamped, scratched and rotated letters.
- **Camera**: handheld, chaotic, low angles, fisheye close to the face, crowd and mosh footage with flash photography.
- **Borrowable**: adaptive 1-bit threshold, xerox grain, nervous frame shuffle on hi-hats, fisheye punch-ins, boiling type, inverted flash frames. Our invert_hit and twitch already cover part of this.

### Bad Bunny / reggaeton videos
- **Colour**: saturated, sunny, neon pinks and greens, Caribbean daylight vs. club neon. Translate to bright, airy B&W with lifted mids and *very* clean whites for day scenes, and deep black with hard backlight for the club.
- **Lens**:
  - wide-angle close-ups;
  - fisheye in the dancehall/perreo sections;
  - Dutch angles;
  - frequent zoom punches (digital crop zooms on the beat, 105–120% scale).
- **Speed and rhythm**: the dembow pattern (3+3+2 feel) drives the cuts. Cut or zoom on the "boom-ch-boom-chick". Speed ramps into slow motion on a dancer's hit, then snap back.
- **Transitions**:
  - whip pans (→ **xfade hblur** / our whip);
  - spin transitions;
  - shake on bass hits;
  - split screens and triptychs (we have triptych);
  - mirror and kaleidoscope sections (→ **kaleid0sc0pe**, N=4–8).
- **Typography**:
  - big, bold, playful;
  - lyric or onomatopoeia text popping on the beat;
  - 3D or extruded type and stickers;
  - Y2K chrome (→ in B&W: **emboss/chrome** on type).
- **Camera**: dancers in tight framing, orbits (360° spins), low angles on the crowd, car culture, high-energy handheld.
- **Borrowable**: beat-synced zoom punches with an expo ease, whip/hblur transitions, kaleidoscope breaks, chrome-embossed type in steel blue, and "wind" ragged wipes. The crowd-energy look stays B&W.

### Common rules for MOTION
- Do every look in **luma**, then apply the steel-blue tint once at the end. Never put chromatic fringes on footage, so turn off colour modulation in all glare.
- Red appears only as small overlay marks (MMMM trail, thin rules, b2b labels), drawn *after* every effect so no effect can smear it into the frame.
- Beat-sync is the shared language across all three: cut on phrases (Drake), on hats (Carti), on dembow (Bad Bunny). Drive `nervous`, zoom punches and flash frames from one beat-marker list.
