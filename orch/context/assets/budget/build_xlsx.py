#!/usr/bin/env python3
"""MOTION · AFTERIMAGE 001 — Drinks Recipe + Full Event Budget workbook."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = "/home/claude/motion/budget/exports/MOTION_Budget_and_Carts.xlsx"

FONT = "Arial"
NAVY = "1E2761"
ICE = "CADCFC"
RED = "C0392B"
WHITE = "FFFFFF"
GREY = "F2F2F2"
GREEN_TEXT = "0F6B2E"
BLUE_INPUT = "0000FF"

wb = openpyxl.Workbook()

def style_header(ws, row, ncols, fill=NAVY, font_color=WHITE, size=11):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color=font_color, size=size)
        cell.fill = PatternFill("solid", fgColor=fill)
        cell.alignment = Alignment(vertical="center", wrap_text=True)

def thin_border():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def money(ws, cell):
    ws[cell].number_format = '$#,##0.00;($#,##0.00)'

def set_col_widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ============================================================= 1. RECIPE
ws = wb.active
ws.title = "Drinks Recipe"
set_col_widths(ws, [30, 14, 34, 16, 12, 14])
ws["A1"] = "MOTION · AFTERIMAGE 001 — Devil's Night"
ws["A1"].font = Font(name=FONT, bold=True, size=16, color=NAVY)
ws["A2"] = "Finalized drinks recipe — 2 batches (vodka + tequila jungle juice) + canned alcohol. BYOB recommended on top of this."
ws["A2"].font = Font(name=FONT, italic=True, size=10, color="555555")
ws.merge_cells("A1:F1")
ws.merge_cells("A2:F2")

row = 4
ws.cell(row=row, column=1, value="VODKA JUNGLE JUICE — about 2.5 gal batch")
ws.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=12, color=RED)
ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
row += 1
headers = ["Ingredient", "Qty", "Notes", "Unit Price", "Qty Needed", "Line Cost"]
for i, h in enumerate(headers, start=1):
    ws.cell(row=row, column=i, value=h)
style_header(ws, row, 6)
vodka_start = row + 1
vodka_items = [
    ("Svedka Vodka", "1.75 L", "80 proof", 17.98, 1),
    ("Hawaiian Punch Fruit Juicy Red", "1 gal", "", 7.48, 1),
    ("Dole 100% Pineapple Juice", "46 oz can", "stands in for 64oz called for", 3.50, 1),
    ("Sprite", "2 L", "", 2.97, 1),
]
r = vodka_start
for name, qty, notes, price, n in vodka_items:
    ws.cell(row=r, column=1, value=name)
    ws.cell(row=r, column=2, value=qty)
    ws.cell(row=r, column=3, value=notes)
    ws.cell(row=r, column=4, value=price); money(ws, f"D{r}")
    ws.cell(row=r, column=5, value=n)
    ws.cell(row=r, column=6, value=f"=D{r}*E{r}"); money(ws, f"F{r}")
    for c in range(1, 7):
        ws.cell(row=r, column=c).border = thin_border()
        ws.cell(row=r, column=c).font = Font(name=FONT, size=10)
    r += 1
vodka_end = r - 1
ws.cell(row=r, column=5, value="Batch total")
ws.cell(row=r, column=5).font = Font(name=FONT, bold=True)
ws.cell(row=r, column=6, value=f"=SUM(F{vodka_start}:F{vodka_end})")
money(ws, f"F{r}")
ws.cell(row=r, column=6).font = Font(name=FONT, bold=True)
vodka_total_row = r
row = r + 2

ws.cell(row=row, column=1, value="TEQUILA JUNGLE JUICE — about 2.7 gal batch")
ws.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=12, color=RED)
ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
row += 1
for i, h in enumerate(headers, start=1):
    ws.cell(row=row, column=i, value=h)
style_header(ws, row, 6)
teq_start = row + 1
teq_items = [
    ("Lunazul Tequila Blanco", "1.75 L", "80 proof", 34.77, 1),
    ("DeKuyper Triple Sec", "750 mL", "15% ABV", 7.48, 1),
    ("H-E-B Limeade (frozen concentrate)", "12 oz", "estimate", 1.50, 2),
    ("Ocean Spray Cranberry Juice Cocktail", "~96 oz", "estimate, exact size unconfirmed online", 5.68, 1),
    ("Sprite", "2 L", "", 2.97, 1),
]
r = teq_start
for name, qty, notes, price, n in teq_items:
    ws.cell(row=r, column=1, value=name)
    ws.cell(row=r, column=2, value=qty)
    ws.cell(row=r, column=3, value=notes)
    ws.cell(row=r, column=4, value=price); money(ws, f"D{r}")
    ws.cell(row=r, column=5, value=n)
    ws.cell(row=r, column=6, value=f"=D{r}*E{r}"); money(ws, f"F{r}")
    for c in range(1, 7):
        ws.cell(row=r, column=c).border = thin_border()
        ws.cell(row=r, column=c).font = Font(name=FONT, size=10)
    r += 1
teq_end = r - 1
ws.cell(row=r, column=5, value="Batch total")
ws.cell(row=r, column=5).font = Font(name=FONT, bold=True)
ws.cell(row=r, column=6, value=f"=SUM(F{teq_start}:F{teq_end})")
money(ws, f"F{r}")
ws.cell(row=r, column=6).font = Font(name=FONT, bold=True)
teq_total_row = r
row = r + 2

ws.cell(row=row, column=1, value="CANS & SPECIALTY")
ws.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=12, color=RED)
ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
row += 1
for i, h in enumerate(headers, start=1):
    ws.cell(row=row, column=i, value=h)
style_header(ws, row, 6)
cans_start = row + 1
cans_items = [
    ("White Claw Variety 24-pack", "12 oz cans", "", 33.46, 1),
    ("Miller Lite 30-pack", "12 oz cans", "showed out-of-stock online when checked — confirm in-store", 23.00, 1),
    ("Soju", "bottle", "for HE//THEY's rider — estimate", 13.00, 2),
]
r = cans_start
for name, qty, notes, price, n in cans_items:
    ws.cell(row=r, column=1, value=name)
    ws.cell(row=r, column=2, value=qty)
    ws.cell(row=r, column=3, value=notes)
    ws.cell(row=r, column=4, value=price); money(ws, f"D{r}")
    ws.cell(row=r, column=5, value=n)
    ws.cell(row=r, column=6, value=f"=D{r}*E{r}"); money(ws, f"F{r}")
    for c in range(1, 7):
        ws.cell(row=r, column=c).border = thin_border()
        ws.cell(row=r, column=c).font = Font(name=FONT, size=10)
    r += 1
cans_end = r - 1
ws.cell(row=r, column=5, value="Section total")
ws.cell(row=r, column=5).font = Font(name=FONT, bold=True)
ws.cell(row=r, column=6, value=f"=SUM(F{cans_start}:F{cans_end})")
money(ws, f"F{r}")
ws.cell(row=r, column=6).font = Font(name=FONT, bold=True)
cans_total_row = r
row = r + 2

ws.cell(row=row, column=1, value="DRINKS GRAND TOTAL (pre-tax)")
ws.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=12)
ws.cell(row=row, column=6, value=f"=F{vodka_total_row}+F{teq_total_row}+F{cans_total_row}")
money(ws, f"F{row}"); ws.cell(row=row, column=6).font = Font(name=FONT, bold=True, size=12)
drinks_pretax_row = row
row += 1
ws.cell(row=row, column=1, value="Austin sales tax (8.25%)")
ws.cell(row=row, column=1).font = Font(name=FONT, italic=True)
ws.cell(row=row, column=6, value=f"=F{drinks_pretax_row}*0.0825")
money(ws, f"F{row}")
tax_row = row
row += 1
ws.cell(row=row, column=1, value="DRINKS TOTAL (with tax)")
ws.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=13, color=NAVY)
ws.cell(row=row, column=6, value=f"=F{drinks_pretax_row}+F{tax_row}")
money(ws, f"F{row}"); ws.cell(row=row, column=6).font = Font(name=FONT, bold=True, size=13, color=NAVY)
drinks_total_cell = f"F{row}"
row += 2
ws.cell(row=row, column=1, value="~170 standard drinks covers about 55 drinkers at 3 each. BYOB tops up beyond that. Figures in blue below are estimates (price not confirmed online this pass) — everything else was checked live against Walmart/H-E-B listings on 13 Oct 2026.")
ws.cell(row=row, column=1).font = Font(name=FONT, italic=True, size=9, color="777777")
ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
ws.freeze_panes = "A4"

# mark estimate rows blue
for r_ in [vodka_start + 2, teq_start + 2, teq_start + 3, cans_start + 1, cans_start + 2]:
    ws.cell(row=r_, column=4).font = Font(name=FONT, size=10, color=BLUE_INPUT)

RECIPE_SHEET = ws.title
DRINKS_TOTAL_REF = f"'{RECIPE_SHEET}'!{drinks_total_cell}"

# ============================================================= 2. SHOPPING CARTS
ws2 = wb.create_sheet("Shopping Carts")
set_col_widths(ws2, [34, 14, 12, 12, 10, 12])
ws2["A1"] = "Shopping carts by stop — exactly what to buy where"
ws2["A1"].font = Font(name=FONT, bold=True, size=14, color=NAVY)
ws2.merge_cells("A1:F1")
ws2["A2"] = "TX law: hard liquor only from a package store. Beer/seltzer and mixers can be grocery. Buy liquor by Thu 29 Oct (stores closed Sun)."
ws2["A2"].font = Font(name=FONT, italic=True, size=10, color="555555")
ws2.merge_cells("A2:F2")

def cart_section(ws, start_row, title, items):
    r = start_row
    ws.cell(row=r, column=1, value=title)
    ws.cell(row=r, column=1).font = Font(name=FONT, bold=True, size=12, color=WHITE)
    ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=NAVY)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    r += 1
    hdrs = ["Item", "Size", "Qty", "Unit Price", "Line Cost", "Confirmed?"]
    for i, h in enumerate(hdrs, start=1):
        ws.cell(row=r, column=i, value=h)
    style_header(ws, r, 6, fill=ICE, font_color="111111", size=10)
    r += 1
    data_start = r
    for name, size, qty, price, confirmed in items:
        ws.cell(row=r, column=1, value=name)
        ws.cell(row=r, column=2, value=size)
        ws.cell(row=r, column=3, value=qty)
        ws.cell(row=r, column=4, value=price); money(ws, f"D{r}")
        ws.cell(row=r, column=5, value=f"=C{r}*D{r}"); money(ws, f"E{r}")
        ws.cell(row=r, column=6, value=confirmed)
        for c in range(1, 7):
            ws.cell(row=r, column=c).border = thin_border()
            ws.cell(row=r, column=c).font = Font(name=FONT, size=10,
                color=(BLUE_INPUT if confirmed == "Estimate" else "111111") if c == 4 else "111111")
        r += 1
    data_end = r - 1
    ws.cell(row=r, column=4, value="Cart total")
    ws.cell(row=r, column=4).font = Font(name=FONT, bold=True)
    ws.cell(row=r, column=5, value=f"=SUM(E{data_start}:E{data_end})")
    money(ws, f"E{r}")
    ws.cell(row=r, column=5).font = Font(name=FONT, bold=True)
    return r, r  # cart total row

row = 4
r1, liquor_total_row = cart_section(ws2, row, "CART 1 · LIQUOR STORE (Twin Liquors / WB Liquors)", [
    ("Svedka Vodka", "1.75 L", 1, 17.98, "Confirmed"),
    ("Lunazul Tequila Blanco", "1.75 L", 1, 34.77, "Confirmed"),
    ("DeKuyper Triple Sec", "750 mL", 1, 7.48, "Confirmed"),
    ("Soju (he/they rider)", "bottle", 2, 13.00, "Estimate"),
])
row = liquor_total_row + 2
r2, grocery_total_row = cart_section(ws2, row, "CART 2 · GROCERY (H-E-B or Walmart)", [
    ("Hawaiian Punch Fruit Juicy Red", "1 gal", 1, 7.48, "Confirmed"),
    ("Dole 100% Pineapple Juice", "46 oz", 1, 3.50, "Estimate"),
    ("Sprite", "2 L", 2, 2.97, "Confirmed"),
    ("H-E-B Limeade concentrate", "12 oz", 2, 1.50, "Estimate"),
    ("Ocean Spray Cranberry Juice Cocktail", "~96 oz", 1, 5.68, "Estimate"),
    ("White Claw Variety 24-pack", "12 oz cans", 1, 33.46, "Confirmed"),
    ("Miller Lite 30-pack", "12 oz cans", 1, 23.00, "Confirm in-store"),
    ("Water (case) + napkins", "—", 1, 10.00, "Estimate"),
])
row = grocery_total_row + 2
r3, samsclub_total_row = cart_section(ws2, row, "CART 3 · SAM'S CLUB", [
    ("Member's Mark Clear Plastic Cups", "16 oz, 132 ct", 2, 11.28, "Confirmed"),
])
row = samsclub_total_row + 2
r4, ice_total_row = cart_section(ws2, row, "CART 4 · ICE (day-of, Twice the Ice / Texas Cold Front, Pflugerville)", [
    ("Bagged ice (~20 lb bags, ~160 lb total)", "20 lb bag", 8, 3.00, "Estimate"),
])
row = ice_total_row + 2
ws2.cell(row=row, column=1, value="COMBINED CARTS TOTAL (pre-tax)")
ws2.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=12)
ws2.cell(row=row, column=5, value=f"=E{liquor_total_row}+E{grocery_total_row}+E{samsclub_total_row}+E{ice_total_row}")
money(ws2, f"E{row}"); ws2.cell(row=row, column=5).font = Font(name=FONT, bold=True, size=12)
carts_pretax_row = row
row += 1
ws2.cell(row=row, column=1, value="Sales tax (8.25%) on liquor + grocery + cups (ice excluded)")
ws2.cell(row=row, column=1).font = Font(name=FONT, italic=True)
ws2.cell(row=row, column=5, value=f"=(E{liquor_total_row}+E{grocery_total_row}+E{samsclub_total_row})*0.0825")
money(ws2, f"E{row}")
carts_tax_row = row
row += 1
ws2.cell(row=row, column=1, value="EVERYTHING-TO-BUY TOTAL")
ws2.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=13, color=NAVY)
ws2.cell(row=row, column=5, value=f"=E{carts_pretax_row}+E{carts_tax_row}")
money(ws2, f"E{row}"); ws2.cell(row=row, column=5).font = Font(name=FONT, bold=True, size=13, color=NAVY)
carts_total_cell = f"'Shopping Carts'!E{row}"
ws2.freeze_panes = "A4"

# ============================================================= 3. FULL EVENT BUDGET
ws3 = wb.create_sheet("Full Event Budget")
set_col_widths(ws3, [36, 16, 30])
ws3["A1"] = "MOTION · AFTERIMAGE 001 — Full Event Budget"
ws3["A1"].font = Font(name=FONT, bold=True, size=16, color=NAVY)
ws3.merge_cells("A1:C1")
ws3["A2"] = "Pool: $450 (Jovanni $150 + Haven $150 + Alex $150). DJs ($575) and CDJ rental ($345) are funded separately by Jovanni, not from the pool."
ws3["A2"].font = Font(name=FONT, italic=True, size=10, color="555555")
ws3.merge_cells("A2:C2")

row = 4
ws3.cell(row=row, column=1, value="Item"); ws3.cell(row=row, column=2, value="Cost"); ws3.cell(row=row, column=3, value="Notes")
style_header(ws3, row, 3)
row += 1
pool_start = row
pool_items = [
    ("Drinks + ice + cups (Shopping Carts tab)", f"={carts_total_cell}", "Carts 1-4 combined, with tax"),
    ("Decor (mirror ball rental, red bulbs, black cloth)", 76, "Unchanged estimate from prior plan"),
    ("DIY signage (eye posters, Cricut labels)", 30, "Unchanged estimate"),
    ("Smoking supplies (cigarettes, lighters, decals)", 44, "Unchanged estimate"),
]
for name, cost, note in pool_items:
    ws3.cell(row=row, column=1, value=name)
    if isinstance(cost, str):
        ws3.cell(row=row, column=2, value=cost)
    else:
        ws3.cell(row=row, column=2, value=cost)
    money(ws3, f"B{row}")
    ws3.cell(row=row, column=3, value=note)
    for c in range(1, 4):
        ws3.cell(row=row, column=c).border = thin_border()
        ws3.cell(row=row, column=c).font = Font(name=FONT, size=10)
    row += 1
pool_end = row - 1
ws3.cell(row=row, column=1, value="POOL SPEND TOTAL")
ws3.cell(row=row, column=1).font = Font(name=FONT, bold=True)
ws3.cell(row=row, column=2, value=f"=SUM(B{pool_start}:B{pool_end})")
money(ws3, f"B{row}"); ws3.cell(row=row, column=2).font = Font(name=FONT, bold=True)
pool_total_row = row
row += 1
ws3.cell(row=row, column=1, value="Pool available ($150 x 3)")
ws3.cell(row=row, column=2, value=450); money(ws3, f"B{row}")
pool_available_row = row
row += 1
ws3.cell(row=row, column=1, value="BUFFER REMAINING")
ws3.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=12, color=GREEN_TEXT)
ws3.cell(row=row, column=2, value=f"=B{pool_available_row}-B{pool_total_row}")
money(ws3, f"B{row}"); ws3.cell(row=row, column=2).font = Font(name=FONT, bold=True, size=12, color=GREEN_TEXT)
row += 3

ws3.cell(row=row, column=1, value="Outside the pool (Jovanni funds personally)")
ws3.cell(row=row, column=1).font = Font(name=FONT, bold=True, size=12, color=NAVY)
ws3.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
row += 1
outside_start = row
outside_items = [
    ("DJ fees (HE//THEY $300 + Rohan $275)", 575, "Still unpaid as of 13 Oct — pay before the 30th"),
    ("Glamz fee", 0, "TBD — not yet confirmed, add once known"),
    ("CDJ + mixer rental (Rock n Roll Rentals, self pickup)", 345, "2x CDJ-2000NXS2 + DJM-900NXS2, weekend rate"),
    ("Cap 01 merch", 429, "Estimate, colourway/quote still open"),
]
for name, cost, note in outside_items:
    ws3.cell(row=row, column=1, value=name)
    ws3.cell(row=row, column=2, value=cost); money(ws3, f"B{row}")
    ws3.cell(row=row, column=3, value=note)
    for c in range(1, 4):
        ws3.cell(row=row, column=c).border = thin_border()
        ws3.cell(row=row, column=c).font = Font(name=FONT, size=10)
    row += 1
outside_end = row - 1
ws3.cell(row=row, column=1, value="OUTSIDE-POOL TOTAL (Jovanni)")
ws3.cell(row=row, column=1).font = Font(name=FONT, bold=True)
ws3.cell(row=row, column=2, value=f"=SUM(B{outside_start}:B{outside_end})")
money(ws3, f"B{row}"); ws3.cell(row=row, column=2).font = Font(name=FONT, bold=True)
ws3.freeze_panes = "A4"

wb.save(OUT)
print("saved", OUT)
