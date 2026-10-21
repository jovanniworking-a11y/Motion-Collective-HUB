# Devil's Night matchbook — draft plates

Party favor for Devil's Night · AFTERIMAGE 001. Custom 20-strike fold-over matchbooks, full color. Quantity **100 requested, not ordered**. Nothing here is a purchase.

Same family as the matchbox: the photographic eyes, then Bodoni; the dimensional MMMM, then letterspaced Jost. Adapted to the book. Not a scaled copy of the box.

## Shared plate

| | Value | Label |
|---|---|---|
| Trim | 2.000 in × 1.500 in | **estimate** |
| Bleed | 0.125 in each edge | specified |
| Safe | 0.0625 in inside the trim | specified |
| Resolution | 600 DPI | specified |
| Canvas | 1350 × 1050 px | from the estimate |
| Trim box | x 75–1275, y 75–975 | |
| Safe box | x 113–1237, y 113–937 | |
| Void | `#0A0810` | |
| Bone | `#EDE6DA` | |
| Type | Bodoni Moda italic (opsz 96, weight 500) and Jost | no other faces |
| Mark | `media/brand/MOTION_mark_3d.png` | the dimensional MMMM, not redrawn |
| Eyes | `media/flyers/final_v6/eyes_hc.png` | middle frame only, see front |

Red on the back plate measures **2.89%** of the frame (oxblood trail on the mark). The eyes are neutral black and white. No red tint.

Rebuild: `python3 media/matchbooks/src/render_matchbook.py`. Numbers below are what that script last wrote to `exports/layout.json`.

## 1. Front cover

The middle frame of the triptych, full width, both eyes and the cheeks. The pinprick frame and the blown-oval frame do not fit above the name once the face is held at the trim width. Cropping the sides to squeeze all three frames in would cut the face off. If a taller dieline arrives, use the full stack and keep this width rule.

- Source crop: x 0–1080, y 630–922. That ends on the frame's own black rule, so the photograph meets the void in black.
- Placed at x 0, y 0, 1350 × 365 px. Full bleed left and right. Top of the photograph runs into the top bleed.
- `DEVIL’S NIGHT` in Bodoni Moda italic, 128 px (15.36 pt), bone, tracking 6 px. Ink box x 183–1187, y 437–541. Center (675, 489). On the void, under the photograph, inside the safe box. Nothing else.

## 2. Inside front

Void field. One line, centered in the safe box.

- `INVITE ONLY` in Jost medium, 58 px (6.96 pt), bone, tracking 16 px. Ink box x 424–931, y 503–548.

## 3. Back cover

Lockup centered in the area above the striker. The lower part of the back is empty void so the striker can move without covering type.

- MMMM at x 295, y 158, 760 × 249 px. File `media/brand/MOTION_mark_3d.png`.
- `MOTION COLLECTIVE` in Jost medium, 56 px (6.72 pt), bone, tracking 12 px. Ink x 299–1049, y 443–486.
- `AFTERIMAGE 001` in Jost, 44 px (5.28 pt), bone, tracking 8 px. Ink x 452–892, y 522–555.
- `10.30.26  ·  AUSTIN` in Jost, 44 px (5.28 pt), bone, tracking 8 px. Ink x 412–938, y 577–612. City only. No street.

## 4. Striker

Not a designed graphic. On the print file it is the same void as the cover, with no type and no mark.

- Rectangle inside the trim: x 75–1275, y 675–975. Height 0.50 in. **Estimate.**
- The bottom bleed (y 975–1050) is also clear.
- `exports/MOTION_Matchbook_BACK_striker_PROOF.png` draws the zone and the words `STRIKER · KEEP CLEAR`. That file is a proof. Do not upload it as art.

## Assembly

`exports/MOTION_Matchbook_ASSEMBLY.png` shows the four surfaces in order: front, inside, back, striker proof. Hairlines on that sheet are trim and safe guides. They are not on the three print files.

Print files, guides off:

- `exports/MOTION_Matchbook_FRONT_600dpi.png`
- `exports/MOTION_Matchbook_INSIDE_600dpi.png`
- `exports/MOTION_Matchbook_BACK_600dpi.png`

## Open — vendor dieline

These stay open until the vendor's dieline is the authority:

- Closed trim. This file assumes 2.000 × 1.500 in.
- Striker height and whether it sits inside the trim or on a separate strike panel.
- Fold, staple, and whether the inside front is the reverse of the front or a third panel.
- Bleed and safe, if the vendor's numbers differ from 0.125 in and 0.0625 in.
- Imposition. Do not force this estimate onto a different dieline. Change the constants in `src/render_matchbook.py` and rebuild.

If the new trim is tall enough that the full triptych can sit at this face width with the name still on void, switch the front crop to the whole `eyes_hc.png` stack. Do not crop the cheeks to make the stack fit.
