import json, base64, html, sys
CL, CUT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
import glob
m = {e["key"]: dict(e, tag="on") for e in json.load(open(f"{CL}/effects.json"))}
for fn in sorted(glob.glob(f"{CL}/effects2_*.json")) + [f"{CL}/effects3.json"]:
    for e in json.load(open(fn)): m[e["key"]] = e
for k in ("warp", "mirror", "vhs"): m[k]["tag"] = "careful"     # warping is on brand since 17 Oct
m["warp"]["note"] = "Rippling distortion. On brand since 17 Oct as a hit or a transition, not a whole shot."
CAT = json.load(open(sys.argv[5]))
GROUPS = [("Pop-culture cut", "New 17 Oct: the Lucki / Carti / Yeat / Kettama language used in teaser v5.", ["fisheye", "bulge", "liquid", "type_stack", "hud", "stabilize", "twirl"]),
          ("Finish", "One grade on every shot. This is what makes phone footage read as film.", ["raw_vs_look", "promist", "deep_glow", "grain"]),
          ("Motion", "Moves that feel shot, not slid.", ["motion_blur", "shake", "speed_ramp"]),
          ("Transitions", "Hard cuts for 95% of edits. One of these per section, on a bar line.", ["whip", "zoom_through", "luma_fade", "defocus", "flash", "slices"]),
          ("Style", "The AFTERIMAGE signatures.", ["echo", "letterbox", "triptych", "astig", "cutout"]),
          ("The mark", "Opens and closes every video.", ["logo", "sweep"]),
          ("Light", "Flares, rays, outlines and reflections. Neutral white only.", ["saber", "lens_flare", "rays", "light_leak", "reflect"]),
          ("Glitch and texture", "The popular GFX looks. Most are a single beat at most for us.", ["twitch", "block_glitch", "pixel_sort", "halftone", "vhs", "rgb_split"]),
          ("Distortion and time", "Warps, freezes and frame-rate tricks.", ["heat_haze", "film_burn", "freeze_outline", "invert_hit", "posterize_time", "warp", "mirror"]),
          ("Colour", "The only tint we use.", ["duotone"])]
TAGS = {"on": "On brand", "careful": "Use once", "off": "Off brand"}
def poster(k): return "data:image/jpeg;base64," + base64.b64encode(open(f"{CL}/{k}.jpg", "rb").read()).decode()
def vid(k): return "data:video/mp4;base64," + base64.b64encode(open(f"{CL}/{k}.mp4", "rb").read()).decode()
cards = []
n = 0
for g, sub, keys in GROUPS:
    items = []
    for k in keys:
        n += 1; e = m[k]
        items.append(f'''<figure class="fx" id="{k}"><div class="frame"><video src="{vid(k)}" poster="{poster(k)}" autoplay muted loop playsinline preload="auto" aria-label="{html.escape(e['name'])} demo"></video></div>
<figcaption><span class="no">FX {n:02d} <i class="tag t-{e.get('tag','on')}">{TAGS[e.get('tag','on')]}</i></span><h3>{html.escape(e['name'])}</h3><p class="plug">{html.escape(e['plugin'])}</p><p>{html.escape(e['note'])}</p><code>mfx.{html.escape(k if k not in ('raw_vs_look','cutout','logo','sweep') else {'raw_vs_look':'finish','cutout':'track matte','logo':'sting4.py','sweep':'sting4.py'}[k])}</code></figcaption></figure>''')
    cards.append(f'<section class="group" id="{g.lower().replace(" ", "-")}"><header class="gh"><h2>{g}</h2><p>{sub}</p></header><div class="grid">{"".join(items)}</div></section>')
rows = [l.strip().strip("|").split("|") for l in open(CUT) if l.startswith("|") and not l.startswith("|---") and "Beat" not in l]
trs = "".join(f"<tr><td class='mono'>{html.escape(r[0].strip())}</td><td class='mono'>{html.escape(r[1].strip())}</td><td>{html.escape(r[2].strip())}</td><td>{html.escape(r[3].strip())}</td></tr>" for r in rows)
cat_rows = "".join(f"<tr><td><b>{html.escape(a)}</b><br><span class='maker'>{html.escape(b)}</span></td><td><span class='lic {('free' if ('free' in c or 'built' in c) else 'paid')}'>{html.escape(c)}</span></td><td>{html.escape(d)}</td><td class='ours'>{html.escape(e_)}</td><td>{html.escape(f_)}</td></tr>" for a, b, c, d, e_, f_ in CAT)
tpl = open(sys.argv[4]).read().replace("{{CATROWS}}", cat_rows).replace("{{CATCOUNT}}", str(len(CAT)))
open(OUT, "w").write(tpl.replace("{{GROUPS}}", "".join(cards)).replace("{{CUTROWS}}", trs).replace("{{COUNT}}", str(n)))
print("ok", n, "effects")
