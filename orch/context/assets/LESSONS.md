# Flyer lessons (shared, append-only)
Every agent reads this before starting and appends what it learned at the end. Newest at the bottom.

## From the client so far (MOTION collective, Jovanni = creative director)
- LOVED: ref_loved_original.png (top-left Ice one). Hairline high-contrast lettering, soft grainy photo with ONE hue, small spaced-out caps, quiet neon glow. "Keep the integrity of the lettering."
- HATED: "deep fried" images (crushed contrast, blown-out glow blobs), random colour pops, blackletter/gothic fonts, big italic gimmicks. "Looks tacky."
- Photo: top half only, three eye bands stacked, scaled down. One hue on all of it, the same treatment for every band.
- Words should take up more of the page than in the original.
- Colour: Ice template + a little red (accent only).
- No set times on the flyer.
- he/they = the duo project of co.b_nguyen b2b Nioon: project name, then their names under it. Keep he/they SMALL-ish (not a headline).
- Bodoni Moda needs "opsz" 96 set explicitly (embed the TTF as base64 @font-face and use font-variation-settings), otherwise the hairlines go thick.

## c_classic (thin classical / fashion-house lettering: Cormorant Garamond, Cinzel)
- Cormorant Garamond defaults to old-style figures ("01" looks lowercase). Set `font-variant-numeric: lining-nums` for event numbers and dates.
- Wide-tracked wordmarks: fix the tracking in em (Cormorant ~.26em, Cinzel ~.34em) and solve the font SIZE so the ink spans the text measure. If you fix the size and solve the tracking instead, you get .5–.6em and the word falls apart into loose letters.
- Remove the trailing letter-space (`margin-right: -tracking`) or centred and justified wordmarks sit off-axis by one space.
- Light classical faces need a smaller, lower-alpha glow than Bodoni (2/10/28 px at .45 alpha). The full neon stack smears hairlines, and at thumbnail size it turns a light face into a bold one. For he/they, a change of face (Cormorant italic or Cinzel caps) at about row size gives it "a bit more presence" without shouting. Keep it white with an accent slash, not glowing blue.
- Rows: use `display:grid; grid-template-columns:1fr auto; align-items:baseline; align-content:center` with `flex:1` rows. That keeps name and note on one baseline while the rows stretch to fill the lower half (flex plus baseline pins tall rows to the top).
- Story (1080×1920): bump the type scale about 1.2× over print×0.72, keep about 150 px clear top and bottom for the IG UI, and put a light top scrim (≤.6 alpha) under the MMMM mark and event name. Brighten the dark end of the MMMM ramp, otherwise the first two Ms vanish over the photo.

## a_didone (Bodoni Moda + Playfair concepts)
- Optical size is per element, not per family: opsz 96 is right for the 250–340 px wordmark, but at ~40 px (event name) its hairlines vanish ("AFTERIMAGE" read as "\FTERI\I\GE"). Use opsz ~18 for small Bodoni, ~48 for the ~80 px Devil's Night italic.
- Playfair 2.0 (`@fontsource-variable/playfair`, the "standard" woff2 carries opsz 5–1200 + wdth + wght) at opsz 1200 is the best non-Bodoni didone for this look; Italiana is low-contrast (no thick/thin), Gloock and DM Serif Display are too heavy. Playfair defaults to old-style figures: add `font-feature-settings:"lnum"` or "01" reads as "o1".
- The reference row system survives without times by putting an accent index (01–04) in the time column: name on one left edge, note right-aligned, `display:grid; align-items:baseline` so a two-line row (he/they + names) still baselines its note to the first line.
- Jost beat Hanken Grotesk and Manrope side by side: its geometric caps echo the didone's round O / pointed M (the Futura–Bodoni pairing); the others look generic/techy next to hairlines. Keep Jost.
- Story: don't push the corner marks down onto the photo (they vanish on bright skin and the red dot fights the eye glints). Give the story a ~180 px dark header strip with an accent hairline under it and set the marks there; the bottom 130 px stays clear for the IG reply bar.
- In a single HTML `style="..."` attribute, `font-variation-settings` values with double quotes break the attribute silently and the font falls back; use single-quoted attributes or put the settings in the stylesheet.

## b_wide (wide_light / wide_mono)
- Fontsource woff2 in a data: URL needs `format("woff2")` plus `font-weight:100 900; font-stretch:62% 125%` ranges in @font-face, or the width/weight axes silently do nothing (Archivo looked identical at wght 100 and 200 until fixed). `document.fonts.check()` returns true either way, so check by eye with a test strip of weights/widths.
- Fit the wordmark to the column with JS after fonts load (measure the inline width, scale font-size). Exclude the last letter's tracking (`MOTIO<span style="letter-spacing:0">N</span>`), or a tracked wordmark stops short of the right margin.
- Light wide sans (Unbounded 200, Archivo 100 tracked) keeps the hairline feel of the loved Bodoni only if the glow is low-alpha: a 2px core plus 10/28px halos at about 50% alpha. Stronger glow fattens thin strokes.
- Story: don't put the MMMM/event header over the photo. The bright eye detail swallows it. A ~190px dark masthead strip holding the header, with the photo below and type scaled ~1.06x the print ratio, reads better and leaves ~150px clear at the bottom for IG UI.
- Jost has no alternate J. Its descending Futura J is part of the face, so accept it rather than swapping fonts. Low tracking (≤.03em) on lowercase Jost notes avoids the "for mat" gap after r.
- A mono row face (JetBrains Mono 300) plus 01–04 indices gives a set-list feel without times. Keep he/they as the same mono at weight 400 and +4px so it isn't a headline.

## d_merge (client round 2, 1 Oct)
- Client picked: poster 6's centred heading layout + the lettering/neon of 1 (Bodoni) and 2 (Playfair). Option 1's wordmark was too big and covered the third photo; ~205–220 px print with overlap ≈95 px into the fade is right.
- Red for Devil's Night: client liked both Bodoni italic (1) and Cinzel spaced caps (6).
- Plain Jost caps rows felt "too bland for the artists and sets": set the artist names in the display serif (opsz ~48, ~70 px print) with a faint ice glow; notes in small spaced Jost caps.
- MMMM mark wants "a little more redness": ramp dark-red → red → white (#3E1A20, #7A2A30, #C2605E, #F4EEEE).

## f_logo_corner (Brief 2: MMMM + AFTERIMAGE 001 placement)
- MMMM drawing: the muddy cluster came from -.32em overlap at opsz 96. Bodoni's M has its thick stroke on the first diagonal and right stem, so at -.18em each M's heavy right stem sits just clear of the next M's hairline left stem: four distinct Ms with a tight trailing rhythm. Use opsz 36 / wght 500 at 60–80 px (opsz 96 hairlines vanish there). Ramp lifted to #A13B42 → #C8555A → #EC9A97 → #FFF so M1 survives a 300 px thumbnail.
- One type system: mark and event name both Bodoni, mark font-size = exactly 2 × event font-size (so cap heights are 2:1), `display:flex; align-items:baseline` so they share a baseline. A 1px ice hairline (.45 alpha) under the header, spanning the same 96 px margins as the rows, turns the two corners into one masthead.
- In the story the masthead sits on the bright brow band. A .6 scrim isn't enough there: use .9 → .72 → 0 over ~400 px, or the letters break up over the highlight.
- A footer sign-off costs ~70 px of print height, so the rows drop to about 75 px each (tight but clean). In the story, shrink the photo to .43 H so the sign-off clears the 300 px IG zone. A short centred 120 px rule reads as a sign-off; a full-width rule just repeats the row rules.
- v4's story footer already ran into the bottom 300 px (foot bottom at 1670). Check the getBoundingClientRect numbers, not just the eye.

## e_logo_centre (Brief 2: MMMM + AFTERIMAGE 001 placement)
- The "muddy" mark was the -.32em overlap: each M's left hairline landed inside the previous M's thick diagonal. At -.2em the thick diagonals line up as a clean rhythm (thick, hairline, thick...) and it reads as four Ms trailing. Test strips of overlap × opsz/wght beat guessing.
- Mark at ~70–120 px: opsz 32 / wght 560, not opsz 96. The opsz 96 hairlines drop out at thumbnail and the mark reads "VVVM". Ramp #A8363E → #CB4A50 → #EC918E → #FFFFFF keeps the redness and the first M still clears navy.
- A radial scrim clipped by its own box shows a hard rectangular edge on the photo. Keep the ellipse (centre + radius) inside the element height and fade to 0 at 100%.
- Story centre-top lockup: from y=170 the mark (≈69 px) + event (≈22 px) just fits inside the first band (ends ≈297). A bigger story mark puts AFTERIMAGE on the band divider.
- v4_story actually ran 50 px into the bottom 300 px IG zone (foot at 1670). Fixed here with a vertical-spacing factor k (~.55–.6) on margins and row padding, not by shrinking type.
- Mark-above-MOTION lockup costs ~110 px of text half. In print, k=.55 absorbs it. In story, photo goes .47 → .42 of height.
- An event name as a boxed label straddling the photo/text edge (navy fill, 1 px ice border) reads clearly and leaves the photo completely clean.

## g_logo_edge (Brief 2 · MMMM + AFTERIMAGE 001 placement)
- The "muddy" MMMM had two causes: the -.32em overlap drove each M's thick right stem into the next M's left hairline, and at opsz 96 the dark-red Ms' hairlines are invisible, so they read as "\|" smudges. Fix: overlap -.14em (stems sit next to each other and don't collide), opsz 60 + wght 500 for the mark (hairlines survive in the dark Ms), ramp #9E3038 → #CC4A4F → #EE9A97 → #FFF, soft red glow only (drop the black text-shadow ring).
- Bodoni Moda at line-height:1 puts the cap centre at ~.49em from the top of the box, so `display:flex; align-items:center` with line-height:1 on both the mark and the event name centres their caps on one midline, whatever their sizes. Good for a header strip.
- Vertical edge label (writing-mode: vertical-rl): 28 px print Bodoni opsz 18 needs wght 600 plus a right-edge dark gradient (≈.7 alpha) to survive a 300 px thumbnail on the photo. Start it on the mark's cap-top line so the two corners relate. It may cross a band divider; that reads as film edge printing.
- Header strip: same navy as the ground (BG) plus a 1px ice hairline at .3 alpha, so it reads as page, not a black bar. On the story the strip has to be ~250 px (content centred in the part below the IG 170 px band), not 6%.

## k_centred_bill (Brief 3 · "centrebill": lineup as a centred playbill)
- A centred bill is taller than ruled rows: each act stacks name / (names) / note, so 3 acts need ~85 px more than 4 one-line rows. Took it from the photo (print .50 → .46, story .46 → .39) rather than shrinking the act names (72 px print). The photo is still the largest block.
- Fill the lower half with `.bill{flex:1;display:flex;flex-direction:column;justify-content:space-evenly}` and give the ornaments a fixed margin (1.5 U). Without the margin, space-evenly collapses to 0 when the column is full and the hairline-diamond ornament touches the note above it (round 1).
- Proximity check: the gap inside an act (name → note, ≈1 U) must be clearly smaller than the gap between acts (ornament + 2×1.5 U), or the notes float between acts.
- One spacing unit U = 12 px × type scale; every vertical gap is 1, 1.5, 2, 3 or 3.5 U.
- Variant b ("DRINKS INCLUDED" as a perk) fits only if the perk replaces the footer hairline: centred caps with flex:1 hairlines either side, footer padding removed. A separate perk line overflowed the text box by 22–46 px.
- Centred stacks need `margin-right:-<tracking>` on every tracked line (date, venue, notes, SOUNDS BY), or the lines drift right of the axis by one space and the centred column looks ragged.
- Story: the masthead's first dark-red M still breaks up over the brow band at story scale even at scrim .94 → .8. A later pass could lift the story ramp's dark end again.

## i_big_names (Brief 3 · "bignames": 3 acts, rows grow to fill the lower half)
- With three acts, set every size on one modular scale (ratio 1.25 from a 24 px print base): labels 24 (step 0), member line 30 (1), date 37.5 (2), artist names 91.6 (6), Devil's Night 179 (9). Names at about half the headline read second, never first, at a 300 px thumbnail. Rows are `flex:1 1 0` and fill whatever height is left, so the dead band disappears without adding content.
- Put spacing on a 12 px unit (1u/2u/3u/4u) with proximity rules: date→info line 1u (one group), info→SOUNDS BY 3u (new group), label→rows 1u.
- Equal rows only hold if the he/they row's min-content (name + member line) fits the flex share. In the story it didn't at first (117/90/90 px). Fix by shrinking the story photo (.46 → .41), not the type. Check row heights in getBoundingClientRect output, not by eye.
- Story legibility: base the story on 1.2× the print scale (×0.72 width ratio). At 1.12 the labels came out 15–19 px, which is about 5–7 pt on a phone. At 1.2 the he/they note collides with the name, so break it in the story only: "UKG · TRANCE / ELECTRO · BASS HOUSE", right-aligned on two lines. It mirrors the two-line name + member stack.
- When DRINKS INCLUDED moves to the footer, set it as its own brighter line above "02:00 CLOSE · ADDRESS…". On one line it wraps in the story.
- The `scrollWidth > clientWidth` overflow test throws false positives on tracked text that uses `margin-right:-tracking`. Check for clipping by eye.

## j_big_photo (Brief 3 · "bigphoto": bigger photo split, tightened text)
- Don't fill the lower half with `flex:1` rows. With 3 acts that stretches row gaps into air and still leaves a dead band. Use a fixed-gap stack and fit ONE factor `--t` in JS (iterate t *= avail/height ~10x) so the footer's bottom lands exactly on the bottom margin (print: = 96 px side margin; story: y=1620, the IG 300 px line).
- Fit factor with three behaviours: display type × t, small spaced caps × max(t, .92) (legibility floor at 300 px thumbnail), gaps × t² (whitespace gives way before type does). Uniform scaling made the notes and footer unreadable at t≈.72.
- Split test (print): 55/45 → t .87 (Devil's Night ≈155 px), 60/40 → t .76 (≈136 px), 61.8/38.2 → t .72 (≈127 px, cramped, date starts competing with the title). Rule that picks the winner: the largest photo where t ≥ .85. That gives print .55 and story .50. Golden ratio looks clever but conflicts with the client note "words should take up more of the page".
- Bands stay equal: `photo()` divides the height by 3 and the crop half-height scales with the band, so taller bands show more face and don't upscale.
- Date at Jost 500 competed with the lineup at thumbnail size. Dropping it to 400 (#DCE4EB) keeps the order Devil's Night → lineup → details.
- Story: the bottom 300 px stays plain navy (IG reply bar). It reads as empty only in a flat file review, not on a phone.

## i_big_names/final (client pick: bignames b + he/they headliner + 4 story bottom-zone treatments)
- To make the headliner one modular step up (he/they at step 7 ≈ 114 px print), its genre note has to wrap to two right-aligned lines in print as well, or it collides with the bigger name. Use `flex:1 1 auto` rows (content height plus an equal share of the leftover): the headliner row grows on its own and the bottom stays filled.
- In the story, the bigger headliner squeezed Glamz and Rohan Rali to 99 px rows. Shrinking the story photo to .39 H brought them back to 112 px. Shrink the photo, not the type.
- IG bottom zone: the safe-zone guides say 250–340 px from the bottom, and link/CTA stickers want about 20% of the bottom clear. Text should end by 1620. A non-text treatment can go down to about 1780 and should stop before the reply bar (about 1800+).
- Bleed: a dim (≤.32 alpha, ramped from 0) blurred repeat of the third eye band fading in to the bottom edge reads as an afterimage, not a fourth band, and no flat navy is left. Keep it blurred (1.6 px) so it never competes with the real bands.
- Sign-off lockup in the zone: mark at about 0.78 of the masthead size, a 48 px (×s) gap between MMMM and AFTERIMAGE 001, a 120 px rule above it, from about 1660 to 1730.
- Sticker slot: a 1 px ice frame (.42 alpha), 60% of the width, about 116 px tall, with an "INVITE ONLY" notch label cut into the top edge and "DM FOR AN INVITE" inside. It works on its own, and a link/question sticker can sit on it.


## 5 Oct 2026 · Playbook added
All agents: read /home/claude/motion/AGENT_PLAYBOOK.md first (editing, compositing, GFX, marketing triggers, serendipity, pre-handback checklist). Client taste in this file still wins over the playbook. Glamz is cut from all promo until confirmed; date is written 10.30.2026.

## teaser (6 Oct · first IG post: eyes + 10.30.26)
- A date over a 3-panel eye stack belongs on the panel 1/2 seam. On the 2/3 seam it gets wedged between the glowing pupils and the white ovals and competes with both. Never put the date over panel 3: it covers the payoff eyes.
- Readability over artwork: use a soft radial void ellipse (about 65% centre, fading to 0) behind the date, not a box or a heavy stroke.
- Afterimage mark over texture: the first impression needs about 50% opacity or it drops out and the mark reads "VIM". Over plain void, 30% is enough.
- Story: start the masthead at y 300 or lower (the IG top bar), keep the artwork uncropped, and keep text out of the bottom 340 px.
- Check every export at 390 w and at the 180 px grid thumbnail before presenting.
- Repeating a date per panel: centre it on the measured nose axis, not the canvas. The face sits right of centre. Panel 3's gap between the ovals sets the maximum date size (≈ 88 px at 1080 w).
- Bodoni at 80–90 px needs opsz ~48. At opsz 96 the flag on the "1" detaches and reads as a stray dot.
- Echo opacity 60/80/100 top to bottom works as an afterimage. 50% on a bright nose highlight is too faint.
