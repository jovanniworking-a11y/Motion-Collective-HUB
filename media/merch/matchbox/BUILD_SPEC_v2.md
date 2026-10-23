# Matchbox v2 · build spec for Pip (Zazzle 2-inch matchbox, black, non-assembled)
Draft, 23 Oct. Nothing gets ordered off this. Jovanni approves the rebuilt design first.

## Step 1 · Brand, in one paragraph
MOTION is the afterimage: one body, and the ghost your eye keeps. The flyer spends all its boldness on one thing, the stacked-eyes halftone triptych. It sits on a void-black field with no type on it. Everything else is quiet: letterspaced bone caps below the art, with generous black space and one red hairline as the structure. A matchbox is something guests keep after the night, so it should feel like the flyer, not like a party favour.

## Why v1 fails (Pip's read is correct)
1. DEVIL'S NIGHT sits on top of the eyes. The art loses, and so does the type.
2. The info line is crammed along the top edge, so there's no breathing room.
3. "Dongle" is rounded and casual, which is the opposite of Bodoni and Jost.
4. The red line is decoration, not structure.

## Step 4 · Scores (1–5)
| | Brand fit | Glance read | Make-ability | Cost/time | Audience | Longevity |
|---|---|---|---|---|---|---|
| **A · art-only top, type on the back** | 5: the eyes alone *is* the afterimage | 5: one thing at 2 inches | 4: one upload per face; type in customizer fonts | 5: same box, same price | 5 | 4: swap the date for later chapters |
| **B · flyer in miniature on top** | 4 | 2: at 2 inches the type block falls to about 4–5 pt under a 60% art band, too small | 3: needs the art and type in one face | 5 | 3 | 3 |
| **C · A, with the back typeset as an image (pick)** | 5 | 5 | 5: real Bodoni and Jost, no customizer font limits | 5 | 5 | 4 |

- **1s and 5s:** B scores 2 on glance read because a 2-inch face can't hold the flyer's lower third. C scores 5 on make-ability because the back goes up as one image, so the fonts don't depend on the customizer.

## Step 5 · Pick
- **Pick: C.** It's A's layout, with the back face uploaded as a typeset image, so it uses real Bodoni Moda and Jost.
- **Runner-up: A**, using customizer fonts for the back.
- **What would change the pick:** if Zazzle's proof shows the uploaded back-face type going soft or blurry below about 7 pt, switch to A and set the back in the customizer with the closest fonts listed below.

## Step 6 · Fact check (public copy)
- **On the box:** DEVIL'S NIGHT · MOTION · AFTERIMAGE 001 · 10.30.26 · AUSTIN. All confirmed.
- **Kept off:** DJ names, the address, prices, set times, and any "limited" or "exclusive" wording.
- **Art:** the eyes art (`eyes_hc.png`) has no text or logos baked in. ✔

## Build, face by face
The files are in this folder; re-render them with `python3 render.py`. Proof: `matchbox_v2_PROOF.png`.

| Face | Upload | Content (top to bottom) | Size | Spacing | Colour |
|---|---|---|---|---|---|
| **Top (cover)** | `matchbox_v2_TOP.png` | Eyes triptych only, centred, full height inside the safe area, uncropped. No type. | — | — | art on the art's own black |
| **Back** | `matchbox_v2_BACK.png` | 1. MOTION | 6.5 pt Jost caps | wide | bone #EDE6DA |
| | | 2. Vertical red hairline, 14 pt tall | 0.5 pt wide | — | red, the only accent |
| | | 3. DEVIL'S NIGHT, the headline | 11 pt Bodoni Moda caps (about 1.7× the details) | wide | bone |
| | | 4. AFTERIMAGE 001 | 7 pt Jost caps | wide | dim #9A92A8 |
| | | 5. 10.30.26 · AUSTIN, at the bottom with space above | 6 pt Jost caps | medium | dim |
| **Long side** | `matchbox_v2_SIDE.png` | MOTION, small, centred | 6.5 pt Jost caps | wide | bone |
| **Other side** | none | Plain black | — | — | — |
| **Striker strip** | — | **Completely clear.** Nothing on it or touching it. | — | — | — |

**Fallback A (customizer fonts):** if the back is built in Zazzle's customizer instead of uploaded:
- **Headline:** the closest high-contrast serif in caps (a Didot or Bodoni-style font if one is listed, otherwise Playfair Display), with letter-spacing as wide as the option allows.
- **Details:** a clean geometric sans in caps (Montserrat, Raleway or Lato), with letter-spacing on.
- **Never** Dongle or anything rounded.
- **Red divider:** if the customizer can't draw a hairline, upload it as a tiny image, or drop it rather than fake it with a thick bar.

## Numbers
| Item | Value | Label |
|---|---|---|
| Face sizes used in the files (2.0 × 1.5 in faces, 2.0 × 0.5 in side, 1/16 in bleed, 600 dpi) | — | **estimate**: match Zazzle's template size before uploading |
| 100 boxes (2 × 50-packs), with the 15% code | $73.02 + shipping | **confirmed** at design time (v1); re-check after the rebuild |
| Express shipping, arrives Tue 27 Oct | — | **confirmed** at design time; **order by the date Zazzle shows for Express** |
| Crew assembly time | — | **open** |
