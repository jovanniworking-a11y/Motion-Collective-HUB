#!/usr/bin/env python3
"""Devil's Night matchbook plates. Draft. Estimates until a vendor dieline arrives.

Closed trim is an estimate (2.000 in × 1.500 in). Bleed 0.125 in. Safe inset
0.0625 in inside the trim. 600 DPI. Change the constants and re-run when the
dieline is in hand. Do not order or upload from this script.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "media" / "matchbooks" / "exports"
FONT_DIR = ROOT / "media" / "matchbooks" / "fonts"
EYES = ROOT / "media" / "flyers" / "final_v6" / "eyes_hc.png"
MARK = ROOT / "media" / "brand" / "MOTION_mark_3d.png"

DPI = 600
TRIM_W_IN = 2.0  # estimate — vendor dieline wins
TRIM_H_IN = 1.5  # estimate — vendor dieline wins
BLEED_IN = 0.125
SAFE_IN = 0.0625
STRIKER_H_IN = 0.50  # estimate — sandpaper strip on the back, bottom

VOID = (10, 8, 16)
BONE = (237, 230, 218)
# Proof marks only. Never on a print plate.
GUIDE = (237, 230, 218)

# Full triptych. Scaled to the height left above the name so all three
# frames stay intact. Sides stay uncropped; the void field fills the rest.


def px(inches: float) -> int:
    return int(round(inches * DPI))


BLEED = px(BLEED_IN)
SAFE = px(SAFE_IN)
W = px(TRIM_W_IN + 2 * BLEED_IN)
H = px(TRIM_H_IN + 2 * BLEED_IN)
TRIM = (BLEED, BLEED, BLEED + px(TRIM_W_IN), BLEED + px(TRIM_H_IN))
SAFE_BOX = (
    TRIM[0] + SAFE,
    TRIM[1] + SAFE,
    TRIM[2] - SAFE,
    TRIM[3] - SAFE,
)
# Striker sits inside the trim, at the bottom. Bottom bleed stays empty too.
STRIKER = (
    TRIM[0],
    TRIM[3] - px(STRIKER_H_IN),
    TRIM[2],
    TRIM[3],
)


def static_font(variable: Path, axes: dict, dest: Path) -> None:
    font = TTFont(variable)
    inst = instantiateVariableFont(font, axes, inplace=False)
    inst.save(dest)


def load_fonts(tmp: Path) -> dict[str, ImageFont.FreeTypeFont]:
    bodoni = tmp / "bodoni.ttf"
    jost_m = tmp / "jost-medium.ttf"
    jost_r = tmp / "jost-regular.ttf"
    static_font(FONT_DIR / "BodoniModa-Italic.ttf", {"opsz": 96, "wght": 500}, bodoni)
    static_font(FONT_DIR / "Jost.ttf", {"wght": 500}, jost_m)
    static_font(FONT_DIR / "Jost.ttf", {"wght": 420}, jost_r)
    return {
        "display": ImageFont.truetype(str(bodoni), 128),
        "collective": ImageFont.truetype(str(jost_m), 56),
        "sub": ImageFont.truetype(str(jost_r), 44),
        "invite": ImageFont.truetype(str(jost_m), 58),
        "label": ImageFont.truetype(str(jost_m), 28),
    }


def text_width(font: ImageFont.FreeTypeFont, text: str, tracking: float) -> float:
    if not text:
        return 0
    return sum(font.getlength(ch) for ch in text) + tracking * (len(text) - 1)


def draw_tracked(
    base: Image.Image,
    text: str,
    center: tuple[float, float],
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    tracking: float,
) -> tuple[int, int, int, int]:
    """Draw tracked text. center is the visual center. Returns the ink bbox."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    width = text_width(font, text, tracking)
    # getbbox y is relative to the top-left origin Pillow uses for text.
    probe = font.getbbox(text)
    height = probe[3] - probe[1]
    x = center[0] - width / 2
    y = center[1] - height / 2 - probe[1]
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill + (255,))
        x += font.getlength(ch) + tracking
    base.alpha_composite(layer)
    bbox = layer.getbbox()
    if bbox is None:
        raise SystemExit(f"no ink for {text!r}")
    return bbox


def new_plate() -> Image.Image:
    return Image.new("RGBA", (W, H), VOID + (255,))


def eyes_bw() -> Image.Image:
    # Full triptych, neutral black and white. No grade, no red, no crop.
    return Image.open(EYES).convert("L").convert("RGB")


def fit_mark(max_w: int) -> Image.Image:
    mark = Image.open(MARK).convert("RGBA")
    alpha = mark.getchannel("A")
    box = alpha.getbbox()
    if box is None:
        raise SystemExit("MMMM mark has no pixels")
    mark = mark.crop(box)
    scale = max_w / mark.width
    size = (max_w, max(1, int(round(mark.height * scale))))
    return mark.resize(size, Image.Resampling.LANCZOS)


def red_fraction(im: Image.Image) -> float:
    rgb = im.convert("RGB")
    pixels = rgb.getdata()
    red = 0
    for r, g, b in pixels:
        # Oxblood trail on the dimensional mark, not only bright #FF3B30.
        if r > 40 and r > g * 1.45 and r > b * 1.45 and (r - max(g, b)) > 18:
            red += 1
    return red / len(pixels)


def assert_inside(bbox: tuple[int, int, int, int], box: tuple[int, int, int, int], name: str) -> None:
    if bbox[0] < box[0] or bbox[1] < box[1] or bbox[2] > box[2] or bbox[3] > box[3]:
        raise SystemExit(f"{name} leaves the safe box: ink {bbox} safe {box}")


def build_front(fonts: dict) -> tuple[Image.Image, dict]:
    """All three frames, then the name on the void under them."""
    title = "DEVIL’S NIGHT"
    src = eyes_bw()
    gap = 16
    tracking = 3
    bottom = SAFE_BOX[3] - 4
    # Largest name that still leaves the whole triptych above it.
    bodoni = fonts["display"].path
    chosen: tuple | None = None
    for size in range(96, 55, -2):
        font = ImageFont.truetype(bodoni, size)
        probe = font.getbbox(title)
        title_h = probe[3] - probe[1]
        image_h = bottom - gap - title_h
        image_w = int(round(src.width * (image_h / src.height)))
        if image_w > W or image_h < 1:
            continue
        if text_width(font, title, tracking) > image_w - 8:
            continue
        chosen = (size, font, image_w, image_h, title_h)
        break
    if chosen is None:
        raise SystemExit("DEVIL’S NIGHT does not fit under the triptych")
    size, font, image_w, image_h, title_h = chosen
    fitted = src.resize((image_w, image_h), Image.Resampling.LANCZOS)
    plate = new_plate()
    origin_x = (W - image_w) // 2
    plate.paste(fitted.convert("RGBA"), (origin_x, 0))
    center_y = image_h + gap + title_h / 2
    bbox = draw_tracked(plate, title, (W / 2, center_y), font, BONE, tracking)
    assert_inside(bbox, SAFE_BOX, title)
    if bbox[1] < image_h:
        raise SystemExit("title overlaps the photograph")
    spec = {
        "surface": "front",
        "eyes": "full triptych, uncropped",
        "eyes_source_px": [src.width, src.height],
        "eyes_placed": [origin_x, 0, image_w, image_h],
        "title": {
            "text": title,
            "font": "Bodoni Moda italic, opsz 96, wght 500",
            "size_px": size,
            "size_pt": round(size / DPI * 72, 2),
            "tracking_px": tracking,
            "color": "#EDE6DA",
            "ink_bbox": list(bbox),
            "center": [W / 2, center_y],
        },
    }
    return plate, spec


def build_back(fonts: dict) -> tuple[Image.Image, dict]:
    plate = new_plate()
    content_bottom = STRIKER[1] - SAFE
    content_top = SAFE_BOX[1]
    # Shrink the mark until red stays at or under 10% of this plate.
    mark_w = 760
    chosen = None
    fraction = 1.0
    while mark_w >= 480:
        trial = plate.copy()
        mark = fit_mark(mark_w)
        # Rough vertical stack to measure red before the final centering.
        trial.alpha_composite(mark, (int((W - mark.width) / 2), content_top + 20))
        fraction = red_fraction(trial)
        chosen = mark
        if fraction <= 0.10:
            break
        mark_w -= 40
    if chosen is None or fraction > 0.10:
        raise SystemExit(f"MMMM red fraction {fraction:.3f} exceeds 0.10")

    # Measure the type stack, then center mark + type in the area above the striker.
    lines = [
        ("MOTION COLLECTIVE", fonts["collective"], 12),
        ("AFTERIMAGE 001", fonts["sub"], 8),
        ("10.30.26  ·  AUSTIN", fonts["sub"], 8),
    ]
    gaps = [36, 22, 16]
    line_h = []
    for text, font, _track in lines:
        probe = font.getbbox(text)
        line_h.append(probe[3] - probe[1])
    stack_h = chosen.height + sum(gaps) + sum(line_h)
    avail = content_bottom - content_top
    if stack_h > avail:
        raise SystemExit(f"back stack {stack_h}px does not fit above the striker ({avail}px)")
    y = content_top + (avail - stack_h) / 2
    mark_xy = (int(round((W - chosen.width) / 2)), int(round(y)))
    plate.alpha_composite(chosen, mark_xy)
    y = mark_xy[1] + chosen.height + gaps[0]
    ink = []
    for (text, font, tracking), h, gap in zip(lines, line_h, gaps):
        bbox = draw_tracked(plate, text, (W / 2, y + h / 2), font, BONE, tracking)
        assert_inside(bbox, (SAFE_BOX[0], content_top, SAFE_BOX[2], content_bottom), text)
        ink.append({"text": text, "ink_bbox": list(bbox), "tracking_px": tracking})
        y += h + gap
    # Nothing in the striker: sample the print plate there for non-void pixels.
    crop = plate.crop(STRIKER)
    if crop.getbbox() and any(px != VOID + (255,) for px in crop.getdata()):
        # getbbox is non-empty because the void is opaque. Check channels instead.
        pass
    rgb = crop.convert("RGB")
    stray = sum(1 for p in rgb.getdata() if p != VOID)
    if stray:
        raise SystemExit(f"striker zone has {stray} non-void pixels")
    spec = {
        "surface": "back",
        "mark": {
            "file": "media/brand/MOTION_mark_3d.png",
            "placed": [mark_xy[0], mark_xy[1], chosen.width, chosen.height],
        },
        "red_fraction": round(red_fraction(plate), 4),
        "lines": ink,
        "striker": {
            "rect": list(STRIKER),
            "height_in": STRIKER_H_IN,
            "label": "estimate",
            "ink": "none — same void as the cover",
        },
    }
    return plate, spec


def build_inside(fonts: dict) -> tuple[Image.Image, dict]:
    plate = new_plate()
    bbox = draw_tracked(
        plate,
        "INVITE ONLY",
        ((SAFE_BOX[0] + SAFE_BOX[2]) / 2, (SAFE_BOX[1] + SAFE_BOX[3]) / 2),
        fonts["invite"],
        BONE,
        tracking=16,
    )
    assert_inside(bbox, SAFE_BOX, "INVITE ONLY")
    spec = {
        "surface": "inside",
        "text": "INVITE ONLY",
        "font": "Jost, wght 500, letterspaced caps",
        "size_px": 58,
        "size_pt": round(58 / DPI * 72, 2),
        "tracking_px": 16,
        "color": "#EDE6DA",
        "ink_bbox": list(bbox),
    }
    return plate, spec


def guides(base: Image.Image, striker: bool) -> Image.Image:
    out = base.convert("RGBA").copy()
    draw = ImageDraw.Draw(out)
    # Trim
    draw.rectangle([TRIM[0], TRIM[1], TRIM[2] - 1, TRIM[3] - 1], outline=GUIDE)
    # Safe
    draw.rectangle(
        [SAFE_BOX[0], SAFE_BOX[1], SAFE_BOX[2] - 1, SAFE_BOX[3] - 1],
        outline=(237, 230, 218, 90),
    )
    if striker:
        draw.rectangle(
            [STRIKER[0], STRIKER[1], STRIKER[2] - 1, STRIKER[3] - 1],
            outline=BONE,
        )
    return out


def assembly(panels: list[tuple[str, Image.Image]], fonts: dict) -> Image.Image:
    gap = 70
    label_h = 70
    margin = 60
    pw, ph = panels[0][1].size
    width = margin * 2 + len(panels) * pw + (len(panels) - 1) * gap
    height = margin + label_h + ph + margin
    sheet = Image.new("RGBA", (width, height), VOID + (255,))
    x = margin
    for name, panel in panels:
        draw_tracked(sheet, name, (x + pw / 2, margin + 24), fonts["label"], BONE, 4)
        sheet.alpha_composite(panel, (x, margin + label_h))
        x += pw + gap
    return sheet


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_name:
        fonts = load_fonts(Path(tmp_name))
        _render(fonts)


def _render(fonts: dict) -> None:
    front, front_spec = build_front(fonts)
    back, back_spec = build_back(fonts)
    inside, inside_spec = build_inside(fonts)
    # Striker is not a separate print. The proof shows the keep-clear zone.
    striker_proof = guides(back, striker=True)
    font_label = fonts["label"]
    draw_tracked(
        striker_proof,
        "STRIKER  ·  KEEP CLEAR",
        ((STRIKER[0] + STRIKER[2]) / 2, (STRIKER[1] + STRIKER[3]) / 2),
        font_label,
        BONE,
        3,
    )

    plates = {
        "MOTION_Matchbook_FRONT_600dpi.png": front,
        "MOTION_Matchbook_BACK_600dpi.png": back,
        "MOTION_Matchbook_INSIDE_600dpi.png": inside,
    }
    for name, im in plates.items():
        im.convert("RGB").save(OUT / name, "PNG", dpi=(DPI, DPI))
    striker_proof.convert("RGB").save(OUT / "MOTION_Matchbook_BACK_striker_PROOF.png", "PNG", dpi=(DPI, DPI))

    sheet = assembly(
        [
            ("01  FRONT", guides(front, False)),
            ("02  INSIDE", guides(inside, False)),
            ("03  BACK", guides(back, False)),
            ("04  STRIKER", striker_proof),
        ],
        fonts,
    )
    sheet.convert("RGB").save(OUT / "MOTION_Matchbook_ASSEMBLY.png", "PNG", dpi=(DPI, DPI))

    spec = {
        "dpi": DPI,
        "trim_in": [TRIM_W_IN, TRIM_H_IN],
        "trim_label": "estimate",
        "bleed_in": BLEED_IN,
        "safe_in": SAFE_IN,
        "canvas_px": [W, H],
        "trim_px": list(TRIM),
        "safe_px": list(SAFE_BOX),
        "colors": {"void": "#0A0810", "bone": "#EDE6DA"},
        "quantity_requested": 100,
        "quantity_label": "requested — not ordered",
        "front": front_spec,
        "back": back_spec,
        "inside": inside_spec,
    }
    (OUT / "layout.json").write_text(json.dumps(spec, indent=2) + "\n")
    print(json.dumps(spec, indent=2))


if __name__ == "__main__":
    main()
