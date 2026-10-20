"""Headless test of the room studio: CDN three.js, console errors, screenshots, ranking run."""
import os
import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

STUDIO_DIR = Path(__file__).resolve().parent
SRC = STUDIO_DIR / "index.html"
TEST = STUDIO_DIR / "_test.html"
OUT = STUDIO_DIR / "shots"
OUT.mkdir(parents=True, exist_ok=True)

# Optional local three.js via MOTION_THREE_ROOT; otherwise keep CDN URLs in index.html
_THREE_ENV = os.environ.get("MOTION_THREE_ROOT", "").strip()
LOCAL_THREE = Path(_THREE_ENV) if _THREE_ENV else None

html = SRC.read_text(encoding="utf-8")
if LOCAL_THREE is not None:
    three_js = LOCAL_THREE / "build" / "three.min.js"
    orbit = LOCAL_THREE / "examples" / "js" / "controls" / "OrbitControls.js"
    if three_js.is_file() and orbit.is_file():
        html = html.replace(
            "https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js",
            three_js.as_uri(),
        )
        html = html.replace(
            "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js",
            orbit.as_uri(),
        )
# google fonts are unreachable from the sandbox; drop them so the page doesn't stall
html = "\n".join(l for l in html.splitlines() if "fonts.g" not in l)
TEST.write_text(
    "<!doctype html><html><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'></head><body>"
    + html
    + "</body></html>",
    encoding="utf-8",
)

mode = sys.argv[1] if len(sys.argv) > 1 else "basic"
W, H = (1600, 1000) if mode != "mobile" else (400, 860)

ARGS = [
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--allow-file-access-from-files",
]

# Prefer Playwright cache chromium (same as _t2.py)
_chrome = None
_env = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH", "").strip()
if _env and Path(_env).is_file():
    _chrome = _env
else:
    _home = Path.home() / ".cache" / "ms-playwright"
    if _home.is_dir():
        for c in sorted(_home.glob("chromium-*/chrome-linux/chrome"), reverse=True):
            if c.is_file():
                _chrome = str(c)
                break

with sync_playwright() as p:
    launch_kw = {"args": ARGS, "headless": True}
    if _chrome:
        launch_kw["executable_path"] = _chrome
    b = p.chromium.launch(**launch_kw)
    pg = b.new_page(viewport={"width": W, "height": H})
    logs = []
    pg.on("console", lambda m: logs.append(f"[{m.type}] {m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"[pageerror] {e}"))
    pg.goto(TEST.resolve().as_uri(), wait_until="commit")
    for _ in range(90):
        pg.wait_for_timeout(1000)
        if pg.evaluate("!!window.__studio"):
            break
    pg.evaluate("localStorage.clear()")
    pg.reload(wait_until="commit")
    for _ in range(60):
        pg.wait_for_timeout(500)
        if pg.evaluate("!!window.__studio"):
            break
    print("boot logs:", logs[:20])
    pg.wait_for_timeout(2500)
    info = pg.evaluate(
        """() => { const s = window.__studio; if(!s) return 'no studio';
        const e = s.ENV; return {items: s.items.map(i => i.type + '@' + i.x.toFixed(1) + ',' + i.z.toFixed(1)),
          danceArea: e.danceArea, egressIn: Math.round(e.egressFt*12), restIn: Math.round(e.restPathFt*12),
          stations: e.stations.length, entry: e.entryCell, rest: e.restCell, wallLen: s.G.wallLen.toFixed(2)}; }"""
    )
    print("INFO", json.dumps(info, indent=1))
    pg.screenshot(path=str(OUT / f"{mode}_3d.png"))
    if mode == "mobile":
        print("\n".join(logs[:30]))
        b.close()
        sys.exit()
    pg.evaluate("window.__studio.setView('top')")
    pg.wait_for_timeout(600)
    pg.screenshot(path=str(OUT / f"{mode}_top.png"))
    if mode in ("rank", "full"):
        t0 = time.time()
        pg.click("#tabs button[data-tab=sim]")
        pg.evaluate("window.__studio.runRanking()")
        pg.wait_for_function("window.__studio.rankResults !== null", timeout=240000)
        print("ranking took", round(time.time() - t0, 1), "s")
        res = pg.evaluate(
            """() => window.__studio.rankResults.map(r => ({t: r.title, score: +r.score.toFixed(2), jam: +r.jamMin.toFixed(2),
            cut: +r.cutMin.toFixed(2), trip: +r.avgTrip.toFixed(2), trips: r.trips, q: r.qPeak, rq: r.rqPeak, eg: Math.round(r.egIn), dp: r.dancePeak}))"""
        )
        for r in res:
            print(r)
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / f"{mode}_rank_panel.png"))
        pg.click("#rank li .use")
        pg.wait_for_timeout(800)
        pg.screenshot(path=str(OUT / f"{mode}_best_top.png"))
        pg.evaluate("window.__studio.setView('3d')")
        pg.click("#btnPlay")
        pg.wait_for_timeout(6000)
        pg.screenshot(path=str(OUT / f"{mode}_live_3d.png"))
        pg.evaluate("window.__studio.setOverlay('crowd'); window.__studio.setView('top')")
        pg.wait_for_timeout(1500)
        pg.screenshot(path=str(OUT / f"{mode}_live_heat.png"))
    print("\n".join(logs[:40]))
    b.close()
