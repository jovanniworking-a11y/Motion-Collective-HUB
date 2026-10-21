# Matchbook plates — continue from here

Draft artwork for 100 full-color 20-strike matchbooks. Not ordered. Not uploaded.

## When a dieline arrives

1. Read `SPEC.md`. The vendor dieline replaces the estimated trim and the estimated 0.50 in striker.
2. Edit the constants at the top of `src/render_matchbook.py` (`TRIM_W_IN`, `TRIM_H_IN`, `STRIKER_H_IN`, bleed, safe).
3. Run `python3 media/matchbooks/src/render_matchbook.py`.
4. Open the three `*_600dpi.png` print files at full size. The striker proof and the assembly are for checking, not for the vendor's upload slot.
5. If the new cover is tall enough, put the whole eyes triptych on the front and keep the face at the full trim width. Do not crop the sides of the face to force the stack.

## Do not

- Redraw the MMMM. Use `media/brand/MOTION_mark_3d.png`.
- Tint the eyes, or fade them through grey. Black and white only. Red stays inside the mark, at or under 10% of the plate. The script refuses a plate that breaks that.
- Set type on the photograph or inside the striker.
- Put a street address on any plate. Austin and the date are the location line.
- Order, pay, or send files to a vendor. That waits for Jovanni.

Fonts in `fonts/` are Bodoni Moda and Jost under the SIL Open Font License (`fonts/OFL.txt`).
