"""AFTERIMAGE 001 · Devil's Night · FINAL (client pick: bignames variant b).
Print + four story treatments of the bottom IG zone. he/they is one step up the modular scale (step 7)
from Glamz / Rohan Rali (step 6), so it reads as the headliner. Rows are content-sized + equal share of leftover
(flex:1 1 auto), so the bottom stays filled with no dead band.
Modes: print · bleed · signoff · fill · sticker  (python3 final.py [modes...])"""
import base64, io, sys
import numpy as np
from PIL import Image, ImageFilter
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/home/claude/motion/flyer_af/i_big_names")
from bignames import photo, step, MEASURE, red_frac, SRC, BG, TINT, ACC, RED, hx, MARK, FONTS

HERE = "/home/claude/motion/flyer_af/i_big_names/final"

def echo(width, height, alpha_top=0.0, alpha_bot=.32):
    """The third (fully dilated) eye band again, as a dim afterimage that fades in towards the bottom edge."""
    im = Image.open(SRC).convert("L").filter(ImageFilter.GaussianBlur(1.6))
    half = int(height * 736 / width / 2); c = 812
    b = im.crop((0, c - half, 736, c + half)).resize((width, height), Image.LANCZOS)
    g = np.asarray(b, float) / 255
    g = np.clip((g - .02) / .66, 0, 1) ** .9 * .88
    g = np.clip(g + np.random.default_rng(7).normal(0, .045, g.shape), 0, 1)
    ramp = np.linspace(alpha_top, alpha_bot, height)[:, None] ** 1.4 / alpha_bot ** .4
    g = g * ramp
    rgb = hx(BG) * (1 - g[..., None]) + hx(TINT) * g[..., None]
    buf = io.BytesIO(); Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(buf, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def html(W, H, mode):
    story = mode != "print"
    s = W / 1500
    t = s * ({"fill": 1.3}.get(mode, 1.2) if story else 1)
    gap = max(2, int(5 * s)); M = int(96 * s)
    ph = int(H * ({"fill": .42}.get(mode, .39) if story else .5))
    img, divs = photo(W, ph, gap)
    base = 24 * t; z = lambda n: round(step(n, base), 1)
    u = 12 * t; sp = lambda n: round(n * u)
    nglow = f"0 0 {int(3*s)}px {ACC},0 0 {int(12*s)}px rgba(88,196,240,.7),0 0 {int(30*s)}px rgba(88,196,240,.4)"; hglow = nglow
    hd_top = 150 if story else int(56 * s)
    divh = "".join(f'<div class="dv" style="top:{y}px"></div>' for y in divs)
    mark = "".join(f'<span style="color:{c}">M</span>' for c in MARK)
    hs = s * (1.15 if story else 1); E = int(36 * hs); MK = 2 * E
    sig = f'<div class="sig"><div class="mark">{mark}</div><div class="ev"><span class="rec"></span>AFTERIMAGE&nbsp;001</div></div>'
    tb = {"print": int(72 * s), "fill": 250}.get(mode, 300)
    dot = " &nbsp;·&nbsp; "
    foot = f'<b class="perk">COSTUMES ENCOURAGED{dot}BEST LOOK WINS CASH</b><br>DRINKS PROVIDED{dot}BYOB RECOMMENDED{"<br>" if story else dot}ADDRESS ON INVITE'
    row = lambda name, note, cls="": f'<div class="row {cls}"><div class="a">{name}</div><div class="n">{note}</div></div>'
    # ---- bottom-zone treatments (story only) ----
    extra = ""
    if mode == "bleed":
        eh = 420
        extra = f'<img class="echo" src="{echo(W, eh)}" style="position:absolute;left:0;bottom:0;width:{W}px;height:{eh}px">' \
                f'<div style="position:absolute;left:0;right:0;bottom:0;height:{max(2,int(3*s))}px;background:{ACC};opacity:.35"></div>'
    elif mode == "signoff":
        e2 = int(E * .78); m2 = 2 * e2
        extra = f'''<div class="so" style="position:absolute;left:0;right:0;top:{H-tb+sp(4)}px;display:flex;flex-direction:column;align-items:center;gap:{sp(2)}px">
          <div style="width:{int(120*s)}px;height:1px;background:rgba(191,221,240,.4)"></div>
          <div class="sig" style="gap:{int(48*s)}px"><div class="mark" style="font-size:{m2}px">{mark}</div><div class="ev" style="font-size:{e2}px;gap:{int(10*s)}px"><span class="rec" style="width:{int(8*s)}px;height:{int(8*s)}px"></span>AFTERIMAGE&nbsp;001</div></div></div>'''
    elif mode == "sticker":
        bw, bh, btop = int(W * .6), 116, H - tb + sp(4)
        extra = f'''<div class="slot" style="position:absolute;left:{(W-bw)//2}px;top:{btop}px;width:{bw}px;height:{bh}px;border:1px solid rgba(191,221,240,.42);
            display:flex;align-items:center;justify-content:center;box-shadow:inset 0 0 {int(30*s)}px rgba(88,196,240,.08)">
          <div style="position:absolute;top:-.6em;left:50%;transform:translateX(-50%);background:{BG};padding:0 .9em;font-size:{z(-1)}px;letter-spacing:.5em;margin-right:-.5em;color:#8F9DAC;font-weight:500;line-height:1.2;white-space:nowrap">INVITE&nbsp;ONLY</div>
          <div style="font-size:{z(1)}px;letter-spacing:.32em;margin-right:-.32em;color:#E9EEF2;font-weight:500;white-space:nowrap">DM FOR AN INVITE</div></div>'''
    elif mode == "fill":
        pass
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;background:linear-gradient(#060B13 0%,#060B13 {80 if not story else 76}%,#10070A 90%,#26090D 100%);overflow:hidden;font-family:JO,sans-serif;color:#E9EEF2;position:relative}}
.ph{{position:absolute;left:0;top:0;width:{W}px;height:{ph}px}} .ph img{{display:block;width:{W}px}}
.ph::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:{max(2,int(3*s))}px;background:{ACC};opacity:.55;box-shadow:0 0 {int(10*s)}px {ACC}}}
.dv{{position:absolute;left:0;width:{W}px;height:{gap}px;background:#08111B;border-bottom:1px solid rgba(88,196,240,.3)}}
.scrim{{position:absolute;left:0;top:0;width:{W}px;height:{hd_top+int((210 if story else 150)*s)}px;background:linear-gradient(rgba(6,11,19,{.9 if story else .8}),rgba(6,11,19,{.72 if story else .5}) 55%,rgba(6,11,19,0))}}
.hd{{position:absolute;left:{M}px;right:{M}px;top:{hd_top}px}}
.hd .sig{{justify-content:space-between;padding-bottom:{int(14*hs)}px;border-bottom:1px solid rgba(191,221,240,.45)}}
.sig{{display:flex;align-items:baseline;line-height:1}}
.mark{{font-family:BM;font-variation-settings:'opsz' 36,'wght' 500;font-size:{MK}px;display:flex;line-height:1;text-shadow:0 0 {int(2*s)}px rgba(0,0,0,.85),0 0 {int(14*s)}px rgba(255,59,48,.28)}}
.mark span{{margin-right:-.18em}} .mark span:last-child{{margin-right:0}}
.ev{{font-family:BM;font-variation-settings:'opsz' 18,'wght' 500;font-size:{E}px;letter-spacing:.24em;margin-right:-.24em;display:flex;gap:{int(14*hs)}px;align-items:baseline;color:#fff;text-shadow:0 0 {int(6*s)}px rgba(0,0,0,.9)}}
.rec{{width:{int(11*hs)}px;height:{int(11*hs)}px;border-radius:50%;background:{RED};box-shadow:0 0 {int(8*s)}px {RED};align-self:center;position:relative;top:{int(-.08*E)}px}}
.txt{{position:absolute;left:{M}px;right:{M}px;top:{ph+sp(4)}px;bottom:{tb}px;display:flex;flex-direction:column;z-index:2}}
.head{{text-align:center}}
.pre2{{font-size:{z(0)}px;line-height:1;letter-spacing:.5em;margin-right:-.5em;color:#C9D8E4;font-weight:500;margin-bottom:{sp(1)}px}}
.dnb{{font-family:BM;font-style:italic;font-variation-settings:'opsz' 96,'wght' 400;font-size:{z(9)}px;line-height:1;color:#FFF3F1;letter-spacing:-.005em;text-shadow:0 0 {int(4*s)}px rgba(255,59,48,.95),0 0 {int(18*s)}px rgba(255,59,48,.6),0 0 {int(44*s)}px rgba(255,59,48,.35)}}
.rule{{width:{int(190*s)}px;height:{max(1,int(2*s))}px;background:#E9EEF2;opacity:.7;margin:{sp(2)}px auto {sp(2)}px}}
.hw{{font-size:{z(0)}px;line-height:1;letter-spacing:.42em;margin-right:-.42em;color:{RED};font-weight:500;margin-top:{sp(2)}px;margin-bottom:{sp(3)}px;text-shadow:0 0 {int(8*s)}px rgba(255,59,48,.6)}}
.blood{{position:absolute;left:0;right:0;top:0;bottom:0;background:linear-gradient(#FFFFFF 0%,#FFFFFF 42%,#DCCFD1 55%,#C98A8E 66%,#FF2A1F 80%,#FF2A1F 100%);mix-blend-mode:multiply;pointer-events:none}}
.date{{font-size:{z(2)}px;line-height:1;font-weight:500;letter-spacing:.14em;margin-right:-.14em}}
.venue{{font-size:{z(2)}px;line-height:1;letter-spacing:.32em;margin-right:-.32em;color:#C9D8E4;font-weight:500;margin-top:{sp(1)}px}}
.foot b{{color:#D5DEE6;font-weight:500}}
.perk{{letter-spacing:.32em}}
.sb{{font-size:{z(0 if story else -1)}px;line-height:1;letter-spacing:.5em;margin-right:-.5em;color:#8F9DAC;font-weight:500;margin-top:{sp(3)}px;margin-bottom:{sp(1)}px;text-align:center}}
.rows{{border-top:1px solid rgba(233,238,242,.18);flex:1;display:flex;flex-direction:column}}
.row{{display:grid;grid-template-columns:1fr auto;align-items:baseline;align-content:center;column-gap:{int(24*s)}px;border-bottom:1px solid rgba(233,238,242,.10);flex:1 1 auto}}
.hey .a,.hey .sl{{text-shadow:{hglow}}}
.a{{font-family:BM;font-variation-settings:'opsz' 48,'wght' 400;font-size:{z(6)}px;line-height:1;letter-spacing:.015em;color:#fff;text-shadow:{nglow}}}
.hey .a{{font-style:italic;font-size:{z(7)}px}}
.sl{{font-style:normal;font-family:JO;font-weight:300;color:#fff;margin:0 .1em;text-shadow:{nglow}}}
.who{{font-size:{z(1)}px;line-height:1;letter-spacing:.06em;color:#C9D2DB;margin-top:{sp(1)}px}}
.who b{{font-weight:400;color:{ACC};margin:0 .3em;letter-spacing:.1em}}
.n{{font-size:{z(1)}px;color:#BFDDF0;text-align:right;letter-spacing:.24em;margin-right:-.24em;font-weight:500;line-height:{round(1+sp(1)/z(0),3)}}}
.foot{{margin-top:{sp(2)}px;font-size:{z(0)}px;line-height:{round(1+sp(1)/z(0),3)};letter-spacing:.28em;margin-right:-.28em;color:#7F8C9A;text-align:center}}
.foot{{color:#A9B4BF!important;letter-spacing:{'.2em' if story else '.28em'}!important;margin-right:{'-.2em' if story else '-.28em'}!important}} .hey .a{{font-size:{z(6) if story else z(7)}px!important}} .perk{{color:#E9EEF2}} .who b{{color:#FF6A5E!important}}
body::before{{content:'';position:absolute;left:0;right:0;bottom:0;height:22%;background:radial-gradient(ellipse 80% 70% at 50% 100%,rgba(255,40,30,.20),transparent 75%);pointer-events:none}} .who b{{font-weight:500!important}}
</style></head><body>
<div class="ph"><img src="{img}">{divh}</div><div class="scrim"></div><div class="hd">{sig}</div>{extra}
<div class="txt">
<div class="head"><div class="pre2">MOTION COLLECTIVE &nbsp;PRESENTS</div><div class="dnb">Devil’s Night</div><div class="rule"></div>
<div class="date">FRIDAY &nbsp;10.30.2026 &nbsp;·&nbsp; 9 PM–2 AM</div>
<div class="venue">AUSTIN</div><div class="hw">THE NIGHT BEFORE HALLOWEEN</div></div>
<div class="sb" style="visibility:hidden;height:0;margin:0"></div>
<div class="rows">
 <div class="row hey"><div><div class="a">HE<span class="sl">//</span>THEY</div><div class="who">co.b <b>b2b</b> NiiON</div></div><div class="n">UKG · HARD HOUSE<br>ELECTRO · BASS HOUSE</div></div>
 {row("Glamz", "23:00")}
 {row("Rohan Rali", "OPEN FORMAT")}
</div>
<div class="foot">{foot}</div>
</div></body></html>'''

EXTRA_MEASURE = """() => { const r = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom)] };
  return {so: r('.so'), slot: r('.slot'), heyW: Math.round(document.querySelector('.hey .a').getBoundingClientRect().right), heyNote: Math.round(document.querySelector('.hey .n').getBoundingClientRect().left)} }"""

if __name__ == "__main__":
    modes = sys.argv[1:] or ["print", "bleed", "signoff", "fill", "sticker"]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for m in modes:
            W, H = (1500, 2100) if m == "print" else (1080, 1920)
            pg = b.new_page(viewport={"width": W, "height": H}); pg.set_content(html(W, H, m)); pg.wait_for_timeout(1000)
            info = pg.evaluate(MEASURE); info.update(pg.evaluate(EXTRA_MEASURE))
            name = "final_print" if m == "print" else f"story_{m}"
            out = f"{HERE}/../final_v4_glamz/{name}.png"; pg.screenshot(path=out); pg.close()
            info["red%"] = round(100 * red_frac(out), 2)
            keep = ["fonts", "rows", "dn", "rowsBox", "foot", "so", "slot", "heyW", "heyNote", "red%"]
            print(name, {k: info.get(k) for k in keep})
            Image.open(out).resize((300, int(300 * H / W)), Image.LANCZOS).save(f"{HERE}/../final_v4_glamz/_thumb_{name}.png")
        b.close()
