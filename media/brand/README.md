# MOTION mark, dimensional version

- `MOTION_lockup_3d.png`: MMMM + MOTION + COLLECTIVE · AUSTIN, transparent, 2328 px wide.
- `MOTION_mark_3d.png`: MMMM only, transparent.

What makes it read as an object instead of typed letters:
- **Chiselled bevel**, like letters cut in stone or metal, lit from the top left.
- **Lacquer gloss** on the red trail; **satin pearl** on the front M.
- **Depth:** the trail recedes, so each M behind is a little smaller and darker, and all four share one baseline.
- **Stacking:** each M sits in front of the one behind it and casts a soft shadow on it. They are never merged or added together.
- **Fine sandblasted texture** on the surface.

Red appears only in the trail, so it stays an accent.

Rebuild: render the masks with `src/glyphs.html` (headless Chrome, transparent; save as `A_M.png`, `A_word.png` and `A_sub.png`), then run `python3 src/logo3d.py lockup out.png 3`.
