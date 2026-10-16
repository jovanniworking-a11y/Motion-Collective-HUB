const pptxgen = require("pptxgenjs");

const VOID = "0A0810";
const BONE = "EDE6DA";
const DIM = "9A92A8";
const RED = "FF3B30";
const OXBLOOD = "A13B42";
const ICE = "58C4F0";
const WHITE = "FFFFFF";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "MOTION";
pres.company = "MOTION Collective";

const FONT_HEAD = "Bookman Old Style";
const FONT_BODY = "Calibri";

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: VOID };
  return s;
}
function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: BONE };
  return s;
}
function footer(s, label) {
  s.addText(label, {
    x: 0.5, y: 7.08, w: 8, h: 0.3, fontFace: FONT_BODY, fontSize: 9,
    color: DIM, isTextBox: true, margin: 0,
  });
  s.addText("AFTERIMAGE 001 · 10.30.26", {
    x: 9.5, y: 7.08, w: 3.33, h: 0.3, fontFace: FONT_BODY, fontSize: 9,
    color: DIM, align: "right", isTextBox: true, margin: 0,
  });
}

// ---------------- Slide 1: Title ----------------
{
  const s = darkSlide();
  s.addText("MOTION", {
    x: 0.8, y: 2.0, w: 11.7, h: 1.0, fontFace: FONT_HEAD, fontSize: 24,
    color: DIM, charSpacing: 10, isTextBox: true, margin: 0,
  });
  s.addText("Budget & Drinks Plan", {
    x: 0.8, y: 2.6, w: 11.7, h: 1.3, fontFace: FONT_HEAD, bold: true, fontSize: 48,
    color: BONE, isTextBox: true, margin: 0,
  });
  s.addText("Devil’s Night · AFTERIMAGE 001 · Friday 10.30.2026", {
    x: 0.8, y: 3.75, w: 11.7, h: 0.5, fontFace: FONT_BODY, fontSize: 16,
    color: RED, isTextBox: true, margin: 0,
  });
  s.addText("Finalized drinks recipe, real shopping carts, and the $450 pool budget — 13 Oct 2026", {
    x: 0.8, y: 4.3, w: 10, h: 0.4, fontFace: FONT_BODY, italic: true, fontSize: 12,
    color: DIM, isTextBox: true, margin: 0,
  });
}

// ---------------- Slide 2: Budget overview (stat callouts) ----------------
{
  const s = lightSlide();
  s.addText("Where the money goes", {
    x: 0.6, y: 0.4, w: 11, h: 0.6, fontFace: FONT_HEAD, bold: true, fontSize: 28, color: VOID, isTextBox: true, margin: 0,
  });
  s.addText("Pool-funded (shared, $450 cap)  vs.  Jovanni-funded separately", {
    x: 0.6, y: 1.0, w: 11, h: 0.4, fontFace: FONT_BODY, italic: true, fontSize: 13, color: "555555", isTextBox: true, margin: 0,
  });

  const stats = [
    { label: "Drinks, ice & cups", value: "$241", sub: "pool" },
    { label: "Decor + DIY + smoking", value: "$150", sub: "pool" },
    { label: "Buffer remaining", value: "$59", sub: "pool", accent: true },
    { label: "DJ fees (unpaid)", value: "$575", sub: "Jovanni" },
    { label: "CDJ + mixer rental", value: "$345", sub: "Jovanni" },
    { label: "Cap 01 merch (est.)", value: "$429", sub: "Jovanni" },
  ];
  const cardW = 3.6, cardH = 1.9, gapX = 0.25, gapY = 0.3, startX = 0.6, startY = 1.7;
  stats.forEach((st, i) => {
    const col = i % 3, rowI = Math.floor(i / 3);
    const x = startX + col * (cardW + gapX);
    const y = startY + rowI * (cardH + gapY);
    s.addShape("roundRect", {
      x, y, w: cardW, h: cardH, rectRadius: 0.08,
      fill: { color: st.accent ? OXBLOOD : WHITE },
      line: { color: st.accent ? OXBLOOD : "DDDDDD", width: 1 },
      shadow: { type: "outer", color: "000000", opacity: 0.15, blur: 6, offset: 2, angle: 90 },
    });
    s.addText(st.value, {
      x: x + 0.2, y: y + 0.25, w: cardW - 0.4, h: 0.8, fontFace: FONT_HEAD, bold: true, fontSize: 36,
      color: st.accent ? WHITE : VOID, isTextBox: true, margin: 0,
    });
    s.addText(st.label, {
      x: x + 0.2, y: y + 1.05, w: cardW - 0.4, h: 0.4, fontFace: FONT_BODY, fontSize: 13,
      color: st.accent ? BONE : "333333", isTextBox: true, margin: 0,
    });
    s.addText(st.sub.toUpperCase(), {
      x: x + 0.2, y: y + 1.45, w: cardW - 0.4, h: 0.3, fontFace: FONT_BODY, bold: true, fontSize: 9,
      color: st.accent ? ICE : RED, charSpacing: 2, isTextBox: true, margin: 0,
    });
  });
  footer(s, "Budget Overview");
}

// ---------------- Slide 3: Drinks recipe ----------------
{
  const s = lightSlide();
  s.addText("Finalized drinks recipe", {
    x: 0.6, y: 0.4, w: 11, h: 0.6, fontFace: FONT_HEAD, bold: true, fontSize: 28, color: VOID, isTextBox: true, margin: 0,
  });
  s.addText("~170 standard drinks — covers ~55 drinkers at 3 each. BYOB tops up the rest.", {
    x: 0.6, y: 1.0, w: 11, h: 0.4, fontFace: FONT_BODY, italic: true, fontSize: 13, color: "555555", isTextBox: true, margin: 0,
  });

  const batches = [
    { title: "VODKA JJ", sub: "~2.5 gal batch", items: ["Svedka Vodka 1.75L", "Hawaiian Punch 1 gal", "Pineapple juice 46oz", "Sprite 2L"], cost: "$31.93" },
    { title: "TEQUILA JJ", sub: "~2.7 gal batch", items: ["Lunazul Tequila 1.75L", "DeKuyper Triple Sec 750mL", "H-E-B Limeade x2", "Cranberry juice ~96oz", "Sprite 2L"], cost: "$53.90" },
    { title: "CANS", sub: "ready to serve", items: ["White Claw Variety 24-pk", "Miller Lite 30-pk", "Soju x2 (he/they rider)"], cost: "$82.46" },
  ];
  const cardW = 3.75, cardH = 4.9, gapX = 0.25, startX = 0.6, startY = 1.65;
  batches.forEach((b, i) => {
    const x = startX + i * (cardW + gapX);
    s.addShape("roundRect", {
      x, y: startY, w: cardW, h: cardH, rectRadius: 0.08,
      fill: { color: WHITE }, line: { color: "DDDDDD", width: 1 },
      shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 6, offset: 2, angle: 90 },
    });
    s.addText(b.title, {
      x: x + 0.25, y: startY + 0.25, w: cardW - 0.5, h: 0.4, fontFace: FONT_HEAD, bold: true, fontSize: 18,
      color: RED, isTextBox: true, margin: 0,
    });
    s.addText(b.sub, {
      x: x + 0.25, y: startY + 0.68, w: cardW - 0.5, h: 0.3, fontFace: FONT_BODY, italic: true, fontSize: 11,
      color: "777777", isTextBox: true, margin: 0,
    });
    const bulletItems = b.items.map((it, idx) => ({
      text: it, options: { bullet: { code: "2022" }, breakLine: idx !== b.items.length - 1, color: "222222" },
    }));
    s.addText(bulletItems, {
      x: x + 0.25, y: startY + 1.1, w: cardW - 0.5, h: cardH - 2.0, fontFace: FONT_BODY, fontSize: 13,
      paraSpaceAfter: 8, isTextBox: true, margin: 0,
    });
    s.addText(b.cost, {
      x: x + 0.25, y: startY + cardH - 0.75, w: cardW - 0.5, h: 0.55, fontFace: FONT_HEAD, bold: true, fontSize: 26,
      color: VOID, isTextBox: true, margin: 0,
    });
  });
  footer(s, "Drinks Recipe");
}

// ---------------- Slide 4: Shopping carts ----------------
{
  const s = lightSlide();
  s.addText("Shopping carts — where to buy it", {
    x: 0.6, y: 0.4, w: 11, h: 0.6, fontFace: FONT_HEAD, bold: true, fontSize: 28, color: VOID, isTextBox: true, margin: 0,
  });
  s.addText("Texas law: hard liquor only from a package store. Beer, seltzer and mixers can be grocery.", {
    x: 0.6, y: 1.0, w: 11.5, h: 0.4, fontFace: FONT_BODY, italic: true, fontSize: 13, color: "555555", isTextBox: true, margin: 0,
  });

  const rows = [
    [{ text: "Stop", options: { bold: true, color: WHITE, fill: { color: VOID } } },
     { text: "Items", options: { bold: true, color: WHITE, fill: { color: VOID } } },
     { text: "Cart total", options: { bold: true, color: WHITE, fill: { color: VOID }, align: "right" } }],
    ["Liquor store", "Svedka, Lunazul, Triple Sec, Soju", "$86.23"],
    ["Grocery (H-E-B / Walmart)", "Mixers, juices, Sprite, White Claw, Miller Lite, water", "$92.06"],
    ["Sam's Club", "Member's Mark cups 16oz x2", "$22.56"],
    ["Ice (day-of)", "~160 lb, Twice the Ice / Texas Cold Front", "$24.00"],
  ];
  rows.slice(1).forEach(r => { r[2] = { text: r[2], options: { align: "right" } }; });
  s.addTable(rows, {
    x: 0.6, y: 1.7, w: 12.1, h: 2.6,
    colW: [3.0, 7.3, 1.8],
    fontFace: FONT_BODY, fontSize: 13, color: "222222",
    border: { type: "solid", color: "DDDDDD", pt: 0.75 },
    autoPage: false,
  });

  s.addShape("roundRect", {
    x: 0.6, y: 4.6, w: 12.1, h: 1.9, rectRadius: 0.08,
    fill: { color: OXBLOOD }, line: { type: "none" },
  });
  s.addText("EVERYTHING-TO-BUY TOTAL", {
    x: 1.0, y: 4.85, w: 6, h: 0.5, fontFace: FONT_BODY, bold: true, fontSize: 14,
    color: BONE, charSpacing: 1, isTextBox: true, margin: 0,
  });
  s.addText("$241.42", {
    x: 1.0, y: 5.25, w: 6, h: 1.0, fontFace: FONT_HEAD, bold: true, fontSize: 48,
    color: WHITE, isTextBox: true, margin: 0,
  });
  s.addText("$224.85 carts + $16.57 Austin sales tax (8.25%)", {
    x: 7.3, y: 5.55, w: 5.1, h: 0.5, fontFace: FONT_BODY, italic: true, fontSize: 12,
    color: ICE, align: "right", isTextBox: true, margin: 0,
  });
  footer(s, "Shopping Carts");
}

// ---------------- Slide 5: Pool budget chart ----------------
{
  const s = lightSlide();
  s.addText("Pool budget check", {
    x: 0.6, y: 0.4, w: 11, h: 0.6, fontFace: FONT_HEAD, bold: true, fontSize: 28, color: VOID, isTextBox: true, margin: 0,
  });
  s.addText("$450 pool (Jovanni + Haven + Alex, $150 each)", {
    x: 0.6, y: 1.0, w: 11, h: 0.4, fontFace: FONT_BODY, italic: true, fontSize: 13, color: "555555", isTextBox: true, margin: 0,
  });

  s.addChart(pres.ChartType.bar, [
    {
      name: "Pool spend",
      labels: ["Drinks/ice/cups", "Decor", "DIY signage", "Smoking", "Buffer left"],
      values: [241.42, 76, 30, 44, 58.58],
    },
  ], {
    x: 0.6, y: 1.6, w: 7.2, h: 5.0,
    barDir: "col",
    showTitle: true, title: "Pool spend by category ($450 total)",
    titleFontFace: FONT_BODY, titleFontSize: 14, titleColor: VOID,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: "222222",
    chartColors: [RED, OXBLOOD, DIM, "C9A0A6", "2F8F5B"],
    catAxisLabelColor: "333333", catAxisLabelFontSize: 11,
    valAxisLabelColor: "333333", valAxisLabelFontSize: 10,
    valGridLine: { color: "E5E5E5", size: 1 },
    catGridLine: { style: "none" },
    showLegend: false,
  });

  const items = [
    ["Drinks + ice + cups", "$241.42"],
    ["Decor", "$76.00"],
    ["DIY signage", "$30.00"],
    ["Smoking supplies", "$44.00"],
    ["Pool spend total", "$391.42"],
    ["Pool available", "$450.00"],
    ["Buffer remaining", "$58.58"],
  ];
  let y = 1.7;
  items.forEach(([label, val], i) => {
    const isTotal = label.includes("total") || label.includes("Buffer") || label.includes("available");
    s.addText(label, {
      x: 8.1, y, w: 2.8, h: 0.45, fontFace: FONT_BODY, fontSize: 13,
      bold: isTotal, color: label.includes("Buffer") ? "2F8F5B" : "222222", isTextBox: true, margin: 0,
    });
    s.addText(val, {
      x: 10.9, y, w: 1.8, h: 0.45, fontFace: FONT_BODY, fontSize: 13, align: "right",
      bold: isTotal, color: label.includes("Buffer") ? "2F8F5B" : "222222", isTextBox: true, margin: 0,
    });
    y += 0.5;
  });
  footer(s, "Pool Budget");
}

// ---------------- Slide 6: Next steps ----------------
{
  const s = darkSlide();
  s.addText("Next steps", {
    x: 0.8, y: 0.6, w: 11, h: 0.7, fontFace: FONT_HEAD, bold: true, fontSize: 32, color: BONE, isTextBox: true, margin: 0,
  });
  const steps = [
    "Buy liquor (vodka, tequila, triple sec, soju) by Thu 29 Oct — package stores closed Sundays.",
    "Grocery run for mixers, beer, White Claw, water — any day that week.",
    "Sam's Club run for cups.",
    "Pick up ice ~160 lb the day of (Twice the Ice / Texas Cold Front, Pflugerville).",
    "Confirm in-store: Miller Lite 30-pack price (showed out of stock online when checked).",
    "Pay DJ fees ($575) before the 30th — currently unpaid.",
  ];
  const bulletItems = steps.map((t, i) => ({
    text: t, options: { bullet: { code: "2022" }, breakLine: i !== steps.length - 1, color: BONE },
  }));
  s.addText(bulletItems, {
    x: 0.8, y: 1.6, w: 11.5, h: 4.5, fontFace: FONT_BODY, fontSize: 18, paraSpaceAfter: 14,
    isTextBox: true, margin: 0,
  });
  footer(s, "Next Steps");
}

pres.writeFile({ fileName: "/home/claude/motion/budget/exports/MOTION_Budget_Deck.pptx" }).then(() => {
  console.log("saved deck");
});
