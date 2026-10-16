#!/usr/bin/env python3
"""One-page MOTION drinks budget + shopping cart PDF."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

NAVY = colors.HexColor("#1E2761")
ICE = colors.HexColor("#CADCFC")
RED = colors.HexColor("#C0392B")
GREY = colors.HexColor("#F2F2F2")
GREEN = colors.HexColor("#0F6B2E")

OUT = "/home/claude/motion/budget/exports/MOTION_Drinks_Budget_Summary.pdf"
doc = SimpleDocTemplate(OUT, pagesize=letter,
                         topMargin=0.4*inch, bottomMargin=0.4*inch,
                         leftMargin=0.6*inch, rightMargin=0.6*inch)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold",
                             fontSize=20, textColor=NAVY, spaceAfter=2)
sub_style = ParagraphStyle("sub", parent=styles["Normal"], fontName="Helvetica-Oblique",
                            fontSize=9, textColor=colors.HexColor("#555555"), spaceAfter=10)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                     fontSize=11, textColor=RED, spaceBefore=5, spaceAfter=3)
note_style = ParagraphStyle("note", parent=styles["Normal"], fontName="Helvetica-Oblique",
                             fontSize=7.5, textColor=colors.HexColor("#777777"), spaceBefore=4)

story = []
story.append(Paragraph("MOTION &middot; Devil&rsquo;s Night Drinks Budget", title_style))
story.append(Paragraph("AFTERIMAGE 001 &middot; Fri 10.30.26 &middot; finalized 13 Oct 2026 &middot; prices checked live where marked ✓", sub_style))
story.append(HRFlowable(width="100%", color=NAVY, thickness=1))

def make_table(rows, col_widths, header=True, align_right_cols=()):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    style = [
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    for c in align_right_cols:
        style.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    return t

# ---- Recipe section ----
story.append(Paragraph("Finalized Recipe", h2))
rows = [["Batch", "Key ingredients", "Cost"]]
rows.append(["Vodka JJ (~2.5 gal)", "Svedka 1.75L + Hawaiian Punch + pineapple juice + Sprite", "$31.93"])
rows.append(["Tequila JJ (~2.7 gal)", "Lunazul 1.75L + triple sec + limeade + cranberry + Sprite", "$53.90"])
rows.append(["Cans", "White Claw 24-pk + Miller Lite 30-pk + soju (he/they rider)", "$82.46"])
story.append(make_table(rows, [1.5*inch, 4.1*inch, 0.8*inch], align_right_cols=(2,)))
story.append(Paragraph("~170 standard drinks, covers ~55 drinkers at 3 each &mdash; BYOB tops up the rest.", note_style))

# ---- Shopping carts ----
story.append(Paragraph("Shopping Carts", h2))
rows = [["Stop", "Item", "Qty", "Price"]]
cart_data = [
    ("Liquor store", "Svedka Vodka 1.75L ✓", "1", "$17.98"),
    ("", "Lunazul Tequila Blanco 1.75L ✓", "1", "$34.77"),
    ("", "DeKuyper Triple Sec 750mL ✓", "1", "$7.48"),
    ("", "Soju (est.)", "2", "$26.00"),
    ("Grocery", "Hawaiian Punch 1 gal ✓", "1", "$7.48"),
    ("", "Dole Pineapple Juice 46oz (est.)", "1", "$3.50"),
    ("", "Sprite 2L ✓", "2", "$5.94"),
    ("", "H-E-B Limeade concentrate (est.)", "2", "$3.00"),
    ("", "Ocean Spray Cranberry Juice (est.)", "1", "$5.68"),
    ("", "White Claw Variety 24-pk ✓", "1", "$33.46"),
    ("", "Miller Lite 30-pk (confirm in-store)", "1", "$23.00"),
    ("", "Water + napkins (est.)", "1", "$10.00"),
    ("Sam's Club", "Member's Mark cups 16oz 132ct ✓", "2", "$22.56"),
    ("Ice (day-of)", "Bagged ice ~20lb bags (est.)", "8", "$24.00"),
]
for stop, item, qty, price in cart_data:
    rows.append([stop, item, qty, price])
t = make_table(rows, [0.9*inch, 3.9*inch, 0.5*inch, 1.1*inch], align_right_cols=(2, 3))
# merge stop column visually via span where blank follows
story.append(t)

# ---- Totals ----
story.append(Paragraph("Totals", h2))
rows = [["", "Amount"]]
rows.append(["Combined carts (pre-tax)", "$224.85"])
rows.append(["Austin sales tax (8.25%)", "$16.57"])
rows.append(["EVERYTHING-TO-BUY TOTAL", "$241.42"])
t2 = make_table(rows, [4.4*inch, 1.0*inch], header=False, align_right_cols=(1,))
t2.setStyle(TableStyle([
    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, -1), (-1, -1), 10),
    ("BACKGROUND", (0, -1), (-1, -1), ICE),
    ("TEXTCOLOR", (0, -1), (-1, -1), NAVY),
]))
story.append(t2)

story.append(Paragraph("Pool Budget Check", h2))
rows = [["", "Amount"]]
rows.append(["Drinks + ice + cups", "$241.42"])
rows.append(["Decor", "$76.00"])
rows.append(["DIY signage", "$30.00"])
rows.append(["Smoking supplies", "$44.00"])
rows.append(["POOL SPEND TOTAL", "$391.42"])
rows.append(["Pool available ($150 × 3)", "$450.00"])
rows.append(["BUFFER REMAINING", "$58.58"])
t3 = make_table(rows, [4.4*inch, 1.0*inch], header=False, align_right_cols=(1,))
t3.setStyle(TableStyle([
    ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
    ("LINEABOVE", (0, 5), (-1, 5), 0.75, NAVY),
    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, -1), (-1, -1), 10),
    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E7F3EA")),
    ("TEXTCOLOR", (0, -1), (-1, -1), GREEN),
]))
story.append(t3)

story.append(Paragraph(
    "✓ = live price checked against Walmart/H-E-B/Sam's Club listings on 13 Oct 2026. Everything else is a clearly-labeled estimate "
    "&mdash; confirm in person, prices shift. DJ fees ($575), CDJ rental ($345) and Cap 01 merch are funded by Jovanni separately, not from the $450 pool.",
    note_style))

doc.build(story)
print("saved", OUT)
