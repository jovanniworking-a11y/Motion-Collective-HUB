"""Matchbox v2 faces (Zazzle 2-inch matchbox). python3 render.py
Face size is an ESTIMATE (2.0 x 1.5 in + 1/16 in bleed) - match Zazzle's template before upload."""
from PIL import Image, ImageDraw, ImageFont
import os, sys
FD = "/tmp/claude-0/-home-user-Motion-Collective-HUB/c9bcd1bd-3003-5afd-a2e0-b12c16463067/scratchpad/deck/fonts"
BOD = FD + "/fontsource-variable-bodoni-moda-5.1.0/package/files/bodoni-moda-latin-standard-normal.woff2"
JOST = FD + "/fontsource-variable-jost-5.1.0/package/files/jost-latin-wght-normal.woff2"
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..", "..")
DPI = 600; BLEED = int(DPI / 16)
W, H = int(2.0 * DPI) + 2 * BLEED, int(1.5 * DPI) + 2 * BLEED
VOID, BONE, DIM, RED = (10, 8, 16), (237, 230, 218), (154, 146, 168), (200, 51, 60)
pt = lambda p: int(round(p * DPI / 72))
def spaced(d, xy, text, font, fill, track, anchor_center=True):
    widths = [d.textlength(c, font=font) for c in text]; tw = sum(widths) + track * (len(text) - 1)
    x = xy[0] - tw / 2 if anchor_center else xy[0]
    for c, w in zip(text, widths): d.text((x, xy[1]), c, font=font, fill=fill); x += w + track
    return tw

# TOP: eyes triptych alone, centred, full art height inside the safe area. No type.
art = Image.open(os.path.join(ROOT, "media/flyers/final_v6/eyes_hc.png")).convert("RGB")
top = Image.new("RGB", (W, H), art.getpixel((2, art.height - 3)))   # match the art's own black: no seam
safe_h = H - 2 * BLEED - 2 * pt(6)
art = art.resize((int(art.width * safe_h / art.height), safe_h), Image.LANCZOS)
top.paste(art, ((W - art.width) // 2, (H - art.height) // 2))
top.save(os.path.join(HERE, "matchbox_v2_TOP.png"), dpi=(DPI, DPI))

# BACK: type only, letterspaced caps, one red hairline. Mirrors the flyer's lower third.
back = Image.new("RGB", (W, H), VOID); d = ImageDraw.Draw(back); cx = W / 2
f_mark = ImageFont.truetype(JOST, pt(6.5)); f_head = ImageFont.truetype(BOD, pt(11)); f_sub = ImageFont.truetype(JOST, pt(7)); f_det = ImageFont.truetype(JOST, pt(6))
y = BLEED + pt(12)
spaced(d, (cx, y), "MOTION", f_mark, BONE, pt(3.2)); y += pt(6.5) + pt(9)
d.rectangle([cx - pt(0.25), y, cx + pt(0.25), y + pt(14)], fill=RED); y += pt(14) + pt(8)       # hairline red vertical divider
spaced(d, (cx, y), "DEVIL’S NIGHT", f_head, BONE, pt(2.2)); y += pt(11) + pt(8)
spaced(d, (cx, y), "AFTERIMAGE 001", f_sub, DIM, pt(2.4))
spaced(d, (cx, H - BLEED - pt(10) - pt(6)), "10.30.26  ·  AUSTIN", f_det, DIM, pt(1.8))
back.save(os.path.join(HERE, "matchbox_v2_BACK.png"), dpi=(DPI, DPI))

# SIDE (long edge, ~2.0 x 0.5 in estimate): MOTION small, centred
SW, SH = int(2.0 * DPI) + 2 * BLEED, int(0.5 * DPI) + 2 * BLEED
side = Image.new("RGB", (SW, SH), VOID); d = ImageDraw.Draw(side)
spaced(d, (SW / 2, SH / 2 - pt(3.5)), "MOTION", f_mark, BONE, pt(3.2))
side.save(os.path.join(HERE, "matchbox_v2_SIDE.png"), dpi=(DPI, DPI))

# proof sheet at true-ish size for review
proof = Image.new("RGB", (W * 2 + 60, H + SH + 90), (40, 40, 44))
proof.paste(top, (20, 20)); proof.paste(back, (W + 40, 20)); proof.paste(side, (20, H + 60))
proof.resize((proof.width // 3, proof.height // 3), Image.LANCZOS).save(os.path.join(HERE, "matchbox_v2_PROOF.png"))
print("faces", (W, H), "side", (SW, SH))
