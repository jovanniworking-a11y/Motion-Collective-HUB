from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter as L

F = "Arial"
def font(**k): return Font(name=F, size=k.pop("size", 10), **k)
BLUE = font(color="0000FF"); BLK = font(); BOLD = font(bold=True); GRN = font(color="008000")
H1 = font(size=14, bold=True); H2 = font(size=11, bold=True); HDR = font(bold=True, color="FFFFFF")
HFILL = PatternFill("solid", fgColor="1F2937"); YEL = PatternFill("solid", fgColor="FFFF00"); BAND = PatternFill("solid", fgColor="F3F4F6")
thin = Side(style="thin", color="D1D5DB"); BOT = Border(bottom=thin)
USD = '$#,##0.00;($#,##0.00);"-"'; PCT = '0.0%;(0.0%);"-"'; NUM1 = '#,##0.0;(#,##0.0);"-"'; INT = '#,##0;(#,##0);"-"'
TW = "Twin Liquors (Round Rock)"; HEB = "H-E-B"; WM = "Walmart"

wb = Workbook()
plan = wb.active; plan.title = "Plan"
shop = wb.create_sheet("Shopping List"); punch = wb.create_sheet("Punch"); pc = wb.create_sheet("Price Compare"); notes = wb.create_sheet("Notes & Sources")

# ---------------- Price Compare ----------------
# cat, product, store, size label, units/pack, oz/unit, abv, price, note, url, abv_source
PCROWS = [
 ("Punch base", "Everclear 190", TW, "1.75 L", 1, 59.2, 0.95, 37.99, "Cheapest per drink. 95% alcohol: jigger only, flammable, never as shots.", "https://twinliquors.com/shop/product/everclear-190/56caaf6e7562752ed5441600", "label"),
 ("Punch base", "Everclear 190 (750 ml)", TW, "750 ml", 1, 25.4, 0.95, 18.99, "Worse value than the 1.75 L.", "https://twinliquors.com/shop/product/everclear-190/56caaf777562752ed5461600", "label"),
 ("Punch base", "Svedka", TW, "1.75 L", 1, 59.2, 0.40, 18.99, "Best-value vodka. Clean in punch, much safer to pour than Everclear.", "https://twinliquors.com/shop/product/svedka-80-proof-vodka/564bd7e469702d5e6e6e0000", "standard"),
 ("Punch base", "Smirnoff 80", TW, "1.75 L", 1, 59.2, 0.40, 19.99, "Same tier as Svedka.", "https://twinliquors.com/shop/product/smirnoff-80-proof-vodka/5521cef66561310003380200", "label"),
 ("Punch base", "New Amsterdam", TW, "1.75 L", 1, 59.2, 0.40, 19.99, "Same tier as Svedka.", "https://twinliquors.com/shop/product/new-amsterdam-80-proof-vodka/5521cef46561310003d70100", "standard"),
 ("Punch base", "Wolfschmidt", TW, "1.75 L", 1, 59.2, 0.40, 15.49, "Cheapest vodka; harsher.", "https://twinliquors.com/shop/product/wolfschmidt-80-proof-vodka/587d3b70bfb24113b11b0173", "standard"),
 ("Punch base", "Western Son", TW, "1.75 L", 1, 59.2, 0.40, 21.99, "Texas-made. Out of stock at Round Rock on 5 Oct.", "https://twinliquors.com/shop/product/western-son-vodka/5967142912f2fb071587e708", "standard"),
 ("Punch base", "Deep Eddy Original", TW, "1.75 L", 1, 59.2, 0.40, 28.99, "Austin-made.", "https://twinliquors.com/shop/product/deep-eddy-vodka-original/56caaaf37562752ed5ba1500", "standard"),
 ("Punch base", "Tito's Handmade", TW, "1.75 L", 1, 59.2, 0.40, 32.99, "Austin-made, best known.", "https://twinliquors.com/shop/product/titos-handmade-vodka/564bd96269702d5e977a0100", "standard"),
 ("Punch base", "Absolut", TW, "1.75 L", 1, 59.2, 0.40, 29.99, "", "https://twinliquors.com/shop/product/absolut-vodka/618e7c297f9199660f0132b8", "standard"),
 ("Punch base", "Bacardi Superior (rum)", TW, "1.75 L", 1, 59.2, 0.40, 22.99, "Rum punch option.", "https://twinliquors.com/shop/product/bacardi-superior-rum/587e15d239e21c07b160de8c", "standard"),
 ("Orange liqueur", "DeKuyper Triple Sec", TW, "1 L", 1, 33.8, 0.15, 7.99, "Price from 1 Oct check.", "https://twinliquors.com/", "standard"),
 ("Orange liqueur", "Bols Triple Sec", TW, "1 L", 1, 33.8, 0.21, 9.99, "", "https://twinliquors.com/shop/product/bols-liqueur-triple-sec-/56dd1c1a69702d1873930000", "standard"),
 ("Orange liqueur", "Patrón Citrónge", TW, "750 ml", 1, 25.4, 0.35, 21.99, "Upgrade.", "https://twinliquors.com/shop/product/patron-citronge-orange/56cacd1575627527c4200100", "standard"),
 ("Shots", "Exotico Blanco tequila", TW, "750 ml", 1, 25.4, 0.40, 22.99, "Price from 1 Oct check.", "https://twinliquors.com/", "standard"),
 ("Shots", "Familia Camarena Silver tequila", TW, "750 ml", 1, 25.4, 0.40, 22.99, "Same price, smoother reputation.", "https://twinliquors.com/shop/product/camarena-silver-tequila/56c270ca75627570b0f00100", "standard"),
 ("Shots", "Lunazul Blanco tequila", TW, "750 ml", 1, 25.4, 0.40, 23.99, "", "https://twinliquors.com/shop/product/lunazul-blanco-tequila/56c3373a69702d27edbd0400", "standard"),
 ("Shots", "Teremana Blanco tequila", TW, "750 ml", 1, 25.4, 0.40, 29.99, "Upgrade.", "https://twinliquors.com/shop/product/teremana-blanco-tequila/5e696e9ce220be04a4e17255", "standard"),
 ("Artist", "Jinro Chamisul Fresh soju", TW, "750 ml", 1, 25.4, 0.165, 11.99, "For he/they. Out of stock at Round Rock on 5 Oct.", "https://twinliquors.com/shop/product/jinro-chamisul-fresh-soju/5d39f1e6ec27b513fd255b65", "standard"),
 ("Ready to drink", "BeatBox Party Box variety", HEB, "6 × 500 ml", 6, 16.9, 0.111, 20.98, "Wine/malt based: sold at H-E-B.", "https://www.heb.com/product-detail/beatbox-party-box-variety-pack/5508020", "listing"),
 ("Ready to drink", "BeatBox single", WM, "500 ml", 1, 16.9, 0.111, 4.22, "", "https://www.walmart.com/ip/BeatBox-Fruit-Punch-Party-Punch-Cocktail-11-1-ABV-500ml-Tetra/705837624", "listing"),
 ("Ready to drink", "Cutwater Lime Margarita", TW, "4 × 12 oz", 4, 12, 0.125, 12.99, "Spirit based: liquor store only.", "https://twinliquors.com/shop/product/cutwater-lime-margarita-4pk-12oz-cans/5aee1ad65065c128fd3529da", "listing"),
 ("Ready to drink", "BuzzBallz Biggie Chiller", HEB, "1.5 L", 1, 50.7, 0.15, 17.76, "Wine based: H-E-B.", "https://www.heb.com/product-detail/buzzballz-biggies-berry-cherry-limeade-large-chiller/15320037", "listing"),
 ("Ready to drink", "BuzzBallz Chiller single", HEB, "187 ml", 1, 6.3, 0.15, 3.12, "ABV assumed 15%.", "https://www.heb.com/product-detail/buzzballz-sour-apple-chiller/2787503", "assumed"),
 ("Ready to drink", "BuzzBallz Strawberry Rita", TW, "200 ml", 1, 6.8, 0.15, 3.99, "Spirit based. ABV assumed 15%.", "https://twinliquors.com/shop/product/buzzballz-rtd-strawberry-rita/573f9d5969702d34f5453500", "assumed"),
 ("Ready to drink", "High Noon vodka seltzer", TW, "8 × 12 oz", 8, 12, 0.045, 19.99, "Spirit based. ABV assumed 4.5%.", "https://twinliquors.com/shop/product/high-noon-sun-sips-tropical-variety-pack-rtd-cocktail-cans/607de70b40603747fe45e498", "assumed"),
 ("Beer", "Miller Lite", WM, "30 × 12 oz", 30, 12, 0.042, 24.67, "Marked down from $32.49. H-E-B $25.27.", "https://www.walmart.com/ip/Miller-Lite-Beer-30-Pack-12-fl-oz-Aluminum-Cans-4-2-ABV-Domestic-Light-Lager/10984520", "listing"),
 ("Beer", "Lone Star", HEB, "30 × 12 oz", 30, 12, 0.0465, 27.47, "ABV assumed 4.65%.", "https://www.heb.com/product-detail/lone-star-texas-beer-30-pk-cans/11448020", "assumed"),
 ("Beer", "Michelob Ultra", HEB, "30 × 12 oz", 30, 12, 0.042, 29.87, "", "https://www.heb.com/product-detail/michelob-ultra-superior-light-lager-beer-cans-30-pack-12-oz/1484389", "listing"),
 ("Beer", "Modelo Especial", HEB, "24 × 12 oz", 24, 12, 0.044, 26.66, "ABV assumed 4.4%.", "https://www.heb.com/product-detail/modelo-especial-mexican-lager-import-beer-24-pk-cans/1610273", "assumed"),
 ("Seltzer", "White Claw variety", HEB, "24 × 12 oz", 24, 12, 0.05, 29.87, "", "https://www.heb.com/product-detail/white-claw-hard-seltzer-variety-24-pk-cans/3758568", "listing"),
 ("Seltzer", "White Claw variety (12)", HEB, "12 × 12 oz", 12, 12, 0.05, 18.67, "", "https://www.heb.com/product-detail/white-claw-hard-seltzer-hard-seltzer-variety-pack-12-pk-cans-flavor-collection-no-2/3758566", "listing"),
 ("Seltzer", "Truly Originals variety", HEB, "24 × 12 oz", 24, 12, 0.05, 29.48, "", "https://www.heb.com/product-detail/truly-hard-seltzer-originals-variety-24-pk-cans/3495514", "listing"),
 ("Seltzer", "Topo Chico Hard Seltzer variety", HEB, "24 × 12 oz", 24, 12, 0.047, 31.98, "", "https://www.heb.com/product-detail/topo-chico-hard-seltzer-variety-24-pk-cans/6327581", "listing"),
]
pc["A1"] = "Price Compare · alcohol, checked 5 Oct 2026"; pc["A1"].font = H1
pc["A2"] = "Blue = typed-in price or ABV (edit if the shelf differs). Black = calculated. Standard drink = 0.6 oz of pure alcohol (US)."; pc["A2"].font = font(italic=True, color="6B7280")
hdr = ["Category", "Product", "Store", "Size", "Units / pack", "oz / unit", "ABV", "Price", "Standard drinks / pack", "$ per standard drink", "Notes", "Source"]
for c, h in enumerate(hdr, 1):
    x = pc.cell(4, c, h); x.font = HDR; x.fill = HFILL; x.alignment = Alignment(wrap_text=True, vertical="center")
PC0 = 5; pcrow = {}
for i, (cat, prod, store, size, units, oz, abv, price, note, url, abvsrc) in enumerate(PCROWS):
    r = PC0 + i; pcrow[prod] = r
    vals = [cat, prod, store, size, units, oz, abv, price]
    for c, v in enumerate(vals, 1):
        x = pc.cell(r, c, v); x.font = BLUE if c >= 5 else BLK
    pc.cell(r, 7).number_format = PCT; pc.cell(r, 8).number_format = USD; pc.cell(r, 6).number_format = '0.0'
    pc.cell(r, 9, f"=E{r}*F{r}*G{r}/0.6").number_format = NUM1
    pc.cell(r, 10, f"=IFERROR(H{r}/I{r},0)").number_format = USD
    pc.cell(r, 11, note); pc.cell(r, 12, url).font = font(color="1D4ED8", underline="single"); pc.cell(r, 12).hyperlink = url
    if abvsrc == "assumed": pc.cell(r, 7).comment = Comment("ABV not listed on the product page; typical value for this product assumed.", "Claude")
    for c in range(1, 13):
        pc.cell(r, c).border = BOT
        if c <= 11 and c != 12: pc.cell(r, c).font = pc.cell(r, c).font.copy(name=F)
PCN = PC0 + len(PCROWS) - 1
for c, w in enumerate([15, 30, 24, 12, 8, 8, 8, 10, 12, 12, 52, 40], 1): pc.column_dimensions[L(c)].width = w
pc.freeze_panes = "C5"
PUNCH_LIST = f"'Price Compare'!$B${pcrow['Everclear 190']}:$B${pcrow['Bacardi Superior (rum)']}"
PB = f"'Price Compare'!$B${PC0}:$B${PCN}"
def look(col, key): return f"INDEX('Price Compare'!${col}${PC0}:${col}${PCN},MATCH({key},{PB},0))"

# ---------------- Punch ----------------
p = punch
p["A1"] = "Devil's Night punch"; p["A1"].font = H1
p["A2"] = "Change the yellow cells. The base spirit list comes from Price Compare; the recipe keeps the same alcohol per gallon whichever spirit you pick."; p["A2"].font = font(italic=True, color="6B7280")
inputs = [
 ("Punch gallons", 6, INT, "How many gallons of punch over the night (2 at doors, then refills)."),
 ("0.0 (no alcohol) gallons", 1, INT, ""),
 ("Base spirit", "Everclear 190", None, "Pick from the list. Svedka/Smirnoff cost almost the same per drink and are far safer to pour."),
 ("Pure alcohol per gallon (oz)", 9.3, '0.0', "9.3 oz = about 23 oz of 80-proof vodka or 9.8 oz of Everclear per gallon."),
 ("Triple sec per gallon (oz)", 5, '0.0', "DeKuyper, 15% ABV."),
 ("Cranberry per gallon (oz)", 64, '0', "H-E-B cranberry cocktail."),
 ("Lime juice per gallon (oz)", 12, '0', "About 12 limes."),
]
for i, (lab, v, fmt, note) in enumerate(inputs):
    r = 4 + i; p.cell(r, 1, lab).font = BOLD; x = p.cell(r, 2, v); x.font = BLUE; x.fill = YEL
    if fmt: x.number_format = fmt
    p.cell(r, 3, note).font = font(color="6B7280")
dv = DataValidation(type="list", formula1=PUNCH_LIST, allow_blank=False); p.add_data_validation(dv); dv.add("B6")
calc = [
 ("Base spirit ABV", f"={look('G','B6')}", PCT),
 ("Base spirit bottle size (oz)", f"={look('F','B6')}", '0.0'),
 ("Base spirit bottle price", f"={look('H','B6')}", USD),
 ("Base spirit per gallon (oz)", "=B7/B12", '0.0'),
 ("Club soda per gallon (oz)", "=128-B15-B8-B9-B10", '0.0'),
 ("Punch ABV", "=(B15*B12+B8*0.15)/128", PCT),
 ("Standard drinks per gallon", "=(B15*B12+B8*0.15)/0.6", NUM1),
 ("9 oz cup = standard drinks", "=9*B17/0.6", '0.00'),
]
p["A11"] = "Calculated"; p["A11"].font = H2
for i, (lab, f, fmt) in enumerate(calc):
    r = 12 + i; p.cell(r, 1, lab); x = p.cell(r, 2, f); x.number_format = fmt
p["A21"] = "Recipe per gallon (128 oz)"; p["A21"].font = H2
rec = [("Base spirit", "=B15"), ("Triple sec", "=B8"), ("Cranberry juice cocktail", "=B9"), ("Fresh lime juice", "=B10"), ("Club soda (add when serving)", "=B16"), ("Total", "=SUM(B22:B26)")]
for i, (lab, f) in enumerate(rec):
    r = 22 + i; p.cell(r, 1, lab).font = BOLD if lab == "Total" else BLK; p.cell(r, 2, f).number_format = '0.0'; p.cell(r, 3, "oz")
p["A29"] = "0.0 per gallon: cranberry 80 oz, lime 16 oz, club soda 32 oz."; p["A29"].font = font(color="6B7280")
p["A31"] = "Batch totals (feed the Shopping List)"; p["A31"].font = H2
tot = [
 ("Base spirit bottles", "=ROUNDUP(B4*B15/B13,0)", INT),
 ("Triple sec 1 L bottles", "=ROUNDUP(B4*B8/33.8,0)", INT),
 ("Cranberry 96 oz jugs (incl. 1 spare)", "=ROUNDUP((B4*B9+B5*80)/96,0)+1", INT),
 ("Limes (about 1 oz each)", "=ROUNDUP(B4*B10+B5*16,0)", INT),
 ("Club soda 2 L bottles", "=ROUNDUP((B4*B16+B5*32)/67.6,0)", INT),
 ("Punch standard drinks", "=B4*B18", NUM1),
]
for i, (lab, f, fmt) in enumerate(tot):
    r = 32 + i; p.cell(r, 1, lab); x = p.cell(r, 2, f); x.number_format = fmt
p.column_dimensions["A"].width = 36; p.column_dimensions["B"].width = 18; p.column_dimensions["C"].width = 80

# ---------------- Shopping List ----------------
s = shop
s["A1"] = "Shopping list"; s["A1"].font = H1
s["A2"] = "Yellow Qty cells are yours to change. Punch rows follow the Punch tab. Prices and ABV come from Price Compare (green) or are typed here (blue)."; s["A2"].font = font(italic=True, color="6B7280")
sh = ["Item", "Store", "Group", "Units / pack", "oz / unit", "ABV", "Qty", "Unit price", "Cost", "Standard drinks", "For guests?", "Guest drinks", "$ per drink"]
for c, h in enumerate(sh, 1):
    x = s.cell(4, c, h); x.font = HDR; x.fill = HFILL; x.alignment = Alignment(wrap_text=True)
rows = []
def pcref(prod, col): return f"='Price Compare'!{col}{pcrow[prod]}"
def add_pc(prod, group, qty, guest="Y", qty_formula=False):
    rows.append(dict(item=pcref(prod, "B"), store=pcref(prod, "C"), group=group, units=pcref(prod, "E"), oz=pcref(prod, "F"), abv=pcref(prod, "G"), qty=qty, price=pcref(prod, "H"), guest=guest, qf=qty_formula, link=True))
# punch base by lookup
rows.append(dict(item="=Punch!B6&\" (1.75 L or as listed)\"", store=f"={look('C','Punch!B6')}", group="Punch", units=1, oz="=Punch!B13", abv="=Punch!B12", qty="=Punch!B32", price="=Punch!B14", guest="Y", qf=True, link=True))
add_pc("DeKuyper Triple Sec", "Punch", "=Punch!B33", guest="N", qty_formula=True)
add_pc("Exotico Blanco tequila", "Shots", 1)
add_pc("Jinro Chamisul Fresh soju", "he/they rider", 1, guest="N")
add_pc("Miller Lite", "Beer", 1)
add_pc("White Claw variety", "Seltzer", 1)
add_pc("BeatBox Party Box variety", "Ready to drink", 1)
add_pc("Cutwater Lime Margarita", "Ready to drink", 2)
add_pc("BuzzBallz Biggie Chiller", "Ready to drink", 1)
mixers = [
 ("H-E-B cranberry cocktail 96 oz", HEB, "Punch mixer", "=Punch!B34", 4.28, "https://www.heb.com/product-detail/h-e-b-cranberry-cocktail-juice/5785031"),
 ("Limes", HEB, "Punch mixer", "=Punch!B35", 0.20, "https://www.heb.com/"),
 ("Club soda 2 L", HEB, "Punch mixer", "=Punch!B36", 1.78, "https://www.heb.com/product-detail/h-e-b-club-soda/125681"),
 ("Ice 10 lb bag (buy Friday)", WM, "Supplies", 20, 1.88, "https://www.walmart.com/ip/170115537"),
 ("Bottled water 24-pack", HEB, "Supplies", 2, 3.27, "https://www.heb.com/product-detail/1042431"),
 ("Clear 16 oz cups, 132 ct", "Sam's Club", "Supplies", 2, 11.28, "https://www.samsclub.com/ip/7874220648"),
 ("Napkins 500 ct", HEB, "Supplies", 1, 3.48, "https://www.heb.com/product-detail/645601"),
]
for (it, st, gr, q, pr, url) in mixers:
    rows.append(dict(item=it, store=st, group=gr, units=None, oz=None, abv=0, qty=q, price=pr, guest="-", qf=isinstance(q, str), link=False, url=url))
R0 = 5
for i, d in enumerate(rows):
    r = R0 + i
    def put(c, v, fmt=None, fnt=None):
        x = s.cell(r, c, v); x.number_format = fmt or "General"; x.font = fnt or BLK; x.border = BOT; return x
    gfont = GRN if d["link"] else BLK
    put(1, d["item"], fnt=gfont if str(d["item"]).startswith("=") else BLK)
    put(2, d["store"], fnt=gfont if str(d["store"]).startswith("=") else BLK)
    put(3, d["group"])
    if d["units"] is not None:
        put(4, d["units"], INT, gfont); put(5, d["oz"], '0.0', gfont); put(6, d["abv"], PCT, gfont)
    else:
        put(4, None); put(5, None); put(6, 0, PCT, BLUE)
    q = put(7, d["qty"], INT, BLK if d["qf"] else BLUE)
    if not d["qf"]: q.fill = YEL
    put(8, d["price"], USD, gfont if d["link"] else BLUE)
    put(9, f"=G{r}*H{r}", USD)
    put(10, f"=IF(D{r}=\"\",0,G{r}*D{r}*E{r}*F{r}/0.6)", NUM1)
    put(11, d["guest"])
    put(12, "=Punch!B37" if i == 0 else f"=IF(K{r}=\"Y\",J{r},0)", NUM1)
    put(13, f"=IFERROR(I{r}/J{r},0)", USD)
    if not d["link"]:
        s.cell(r, 8).comment = Comment(f"Source: {d['url']} (checked 5 Oct 2026)", "Claude")
RN = R0 + len(rows) - 1
TR = RN + 1
s.cell(TR, 1, "Total").font = BOLD
for c, f, fmt in [(9, f"=SUM(I{R0}:I{RN})", USD), (10, f"=SUM(J{R0}:J{RN})", NUM1), (12, f"=SUM(L{R0}:L{RN})", NUM1), (13, f"=IFERROR(I{TR}/L{TR},0)", USD)]:
    x = s.cell(TR, c, f); x.font = BOLD; x.number_format = fmt
s.cell(TR + 2, 1, "Punch row: guest drinks = what the punch batch holds (spirit + triple sec), so leftover spirit isn't counted.").font = font(italic=True, color="6B7280")
s.cell(TR + 1, 1, "Prices before tax. Twin Liquors prices are the Round Rock store; H-E-B prices may come from a non-Austin default store. Soju is for he/they and isn't counted in guest drinks.").font = font(italic=True, color="6B7280")
for c, w in enumerate([40, 26, 16, 9, 9, 8, 7, 11, 11, 11, 9, 11, 10], 1): s.column_dimensions[L(c)].width = w
s.freeze_panes = "B5"

# group subtotals
GR = TR + 4
s.cell(GR, 1, "By group").font = H2
groups = ["Punch", "Punch mixer", "Shots", "Beer", "Seltzer", "Ready to drink", "he/they rider", "Supplies"]
s.cell(GR + 1, 1, "Group").font = BOLD; s.cell(GR + 1, 9, "Cost").font = BOLD; s.cell(GR + 1, 12, "Guest drinks").font = BOLD
for i, g in enumerate(groups):
    r = GR + 2 + i; s.cell(r, 1, g)
    s.cell(r, 9, f'=SUMIFS($I${R0}:$I${RN},$C${R0}:$C${RN},A{r})').number_format = USD
    s.cell(r, 12, f'=SUMIFS($L${R0}:$L${RN},$C${R0}:$C${RN},A{r})').number_format = NUM1

# ---------------- Plan ----------------
pl = plan
pl["A1"] = "Devil's Night · drinks plan"; pl["A1"].font = H1
pl["A2"] = "Fri 30 Oct 2026, 9 PM–2 AM. Change the yellow cells; everything else updates."; pl["A2"].font = font(italic=True, color="6B7280")
pl["A4"] = "Headcount"; pl["A4"].font = H2
inp = [("Guests (incl. crew)", 70, INT), ("Drinkers (21+, drinking)", 60, INT), ("Drinks each (target)", 3, '0.0'), ("Buffer so we don't run out", 0.15, PCT)]
for i, (lab, v, fmt) in enumerate(inp):
    r = 5 + i; pl.cell(r, 1, lab); x = pl.cell(r, 2, v); x.font = BLUE; x.fill = YEL; x.number_format = fmt
pl["A10"] = "Do we have enough?"; pl["A10"].font = H2
out = [
 ("Standard drinks needed", "=B6*B7*(1+B8)", NUM1),
 ("Standard drinks planned (guests)", f"='Shopping List'!L{TR}", NUM1),
 ("Drinks per drinker", "=IFERROR(B12/B6,0)", '0.0'),
 ("Status", '=IF(B12>=B11,"Enough",IF(B12>=B6*B7,"Enough, no buffer","Short by "&TEXT(B11-B12,"0")&" drinks"))', None),
]
for i, (lab, f, fmt) in enumerate(out):
    r = 11 + i; pl.cell(r, 1, lab); x = pl.cell(r, 2, f); x.font = BOLD if lab == "Status" else BLK
    if fmt: x.number_format = fmt
pl["A16"] = "Cost"; pl["A16"].font = H2
cost = [("Drinks total (before tax)", f"='Shopping List'!I{TR}", USD), ("Cost per guest drink", f"='Shopping List'!M{TR}", USD), ("Cost per guest", "=IFERROR(B17/B5,0)", USD)]
for i, (lab, f, fmt) in enumerate(cost):
    r = 17 + i; pl.cell(r, 1, lab); x = pl.cell(r, 2, f); x.number_format = fmt; x.font = GRN if "Shopping" in f else BLK
pl["A21"] = "Event budget"; pl["A21"].font = H2
bud = [("Crew members", 6, INT, True), ("Each pays", 176, USD, True), ("Budget", "=B22*B23", USD, False),
       ("he/they (co.b_nguyen b2b Nioon)", 300, USD, True), ("Drinks", "=B17", USD, False), ("Decor (lean cart)", 153, USD, True),
       ("Mirror ball rental", 45, USD, True), ("Rohan Rali", 0, USD, True), ("Food", 0, USD, True), ("Left", "=B24-SUM(B25:B30)", USD, False)]
for i, (lab, v, fmt, isin) in enumerate(bud):
    r = 22 + i; pl.cell(r, 1, lab).font = BOLD if lab in ("Budget", "Left") else BLK
    x = pl.cell(r, 2, v); x.number_format = fmt
    if isin: x.font = BLUE; x.fill = YEL
    elif lab in ("Budget", "Left"): x.font = BOLD
pl["C28"] = "Fill in once he quotes"; pl["C29"] = "Pizza or snacks, recommended"
pl["A33"] = "Where to buy"; pl["A33"].font = H2
for i, t in enumerate([
 "Twin Liquors (or WB Liquors at Costco, Kelly Ln): the punch spirit, triple sec, tequila, soju, Cutwater. Liquor stores: Mon–Sat 10am–9pm, closed Sunday.",
 "H-E-B: cranberry, limes, club soda, water, napkins, BeatBox, BuzzBallz, White Claw (beer, wine and malt drinks are sold in grocery stores).",
 "Walmart: Miller Lite 30-pack and ice. Sam's Club: cups.",
 "Buy ice on Friday afternoon. Everything else any weekday before.",
]):
    pl.cell(34 + i, 1, t)
pl.column_dimensions["A"].width = 38; pl.column_dimensions["B"].width = 16; pl.column_dimensions["C"].width = 30

# ---------------- Notes ----------------
n = notes
n["A1"] = "Notes & sources"; n["A1"].font = H1
lines = [
 "Standard drink: 0.6 oz (14 g) of pure alcohol, the US definition. Standard drinks = volume (oz) × ABV ÷ 0.6.",
 "Prices checked online 5 Oct 2026, before tax. Twin Liquors = Round Rock (Palm Valley) store; some H-E-B pages showed a non-Austin default store. Spec's, Total Wine and Costco didn't show Austin prices online.",
 "ABV marked with a cell comment was not on the product page; a typical value was assumed.",
 "Texas: only package stores sell spirits and spirit-based canned cocktails (Cutwater, High Noon, BuzzBallz Cocktails). Grocery stores sell beer, wine and wine/malt drinks (BeatBox, BuzzBallz Chillers, White Claw).",
 "Everclear is 95% alcohol: measure with a jigger, never serve as shots, keep away from candles and the smokers. Only the bar person handles it.",
 "No selling, no collection, IDs checked for anyone drinking. Water and food out all night; rides home only.",
 "TABC package store hours: https://www.tabc.texas.gov/static/sites/default/files/2021-08/package-store-p-and-local-distributor-lp-off-premise-retailers-lc_0.pdf",
 "Product links for every price are in the Source column of Price Compare and in cell comments on the Shopping List.",
]
for i, t in enumerate(lines): n.cell(3 + i, 1, t).alignment = Alignment(wrap_text=True, vertical="top")
n.column_dimensions["A"].width = 120

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.font and c.font.name != F: c.font = c.font.copy(name=F)
wb.save("Devils_Night_Drinks.xlsx")
print("rows", len(rows), "TR", TR)
