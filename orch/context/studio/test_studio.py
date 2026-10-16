"""Headless test of the room studio: local three.js swap, console errors, screenshots, ranking run."""
import sys, time, json
from playwright.sync_api import sync_playwright

SRC = "/home/claude/motion/studio/index.html"
TEST = "/home/claude/motion/studio/_test.html"
OUT = "/home/claude/motion/studio/shots"
import os; os.makedirs(OUT, exist_ok=True)

html = open(SRC).read()
html = html.replace("https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js",
                    "file:///home/claude/motion/apt/package/build/three.min.js")
html = html.replace("https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js",
                    "file:///home/claude/motion/apt/package/examples/js/controls/OrbitControls.js")
# google fonts are unreachable from the sandbox; drop them so the page doesn't stall
html = "\n".join(l for l in html.splitlines() if "fonts.g" not in l)
open(TEST, "w").write("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'></head><body>" + html + "</body></html>")

mode = sys.argv[1] if len(sys.argv) > 1 else "basic"
W, H = (1600, 1000) if mode != "mobile" else (400, 860)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": W, "height": H})
    logs = []
    pg.on("console", lambda m: logs.append(f"[{m.type}] {m.text}"))
    pg.on("pageerror", lambda e: logs.append(f"[pageerror] {e}"))
    pg.goto("file://" + TEST, wait_until="commit")
    for _ in range(90):
        pg.wait_for_timeout(1000)
        if pg.evaluate("!!window.__studio"): break
    pg.evaluate("localStorage.clear()"); pg.reload(wait_until="commit")
    for _ in range(60):
        pg.wait_for_timeout(500)
        if pg.evaluate("!!window.__studio"): break
    print("boot logs:", logs[:20])
    pg.wait_for_timeout(2500)
    info = pg.evaluate("""() => { const s = window.__studio; if(!s) return 'no studio';
        const e = s.ENV; return {items: s.items.map(i => i.type + '@' + i.x.toFixed(1) + ',' + i.z.toFixed(1)),
          danceArea: e.danceArea, egressIn: Math.round(e.egressFt*12), restIn: Math.round(e.restPathFt*12),
          stations: e.stations.length, entry: e.entryCell, rest: e.restCell, wallLen: s.G.wallLen.toFixed(2)}; }""")
    print("INFO", json.dumps(info, indent=1))
    pg.screenshot(path=f"{OUT}/{mode}_3d.png")
    if mode == "mobile":
        print("\n".join(logs[:30])); b.close(); sys.exit()
    pg.evaluate("window.__studio.setView('top')"); pg.wait_for_timeout(600)
    pg.screenshot(path=f"{OUT}/{mode}_top.png")
    if mode in ("rank", "full"):
        t0 = time.time()
        pg.click("#tabs button[data-tab=sim]")
        pg.evaluate("window.__studio.runRanking()")
        pg.wait_for_function("window.__studio.rankResults !== null", timeout=240000)
        print("ranking took", round(time.time() - t0, 1), "s")
        res = pg.evaluate("""() => window.__studio.rankResults.map(r => ({t: r.title, score: +r.score.toFixed(2), jam: +r.jamMin.toFixed(2),
            cut: +r.cutMin.toFixed(2), trip: +r.avgTrip.toFixed(2), trips: r.trips, q: r.qPeak, rq: r.rqPeak, eg: Math.round(r.egIn), dp: r.dancePeak}))""")
        for r in res: print(r)
        pg.wait_for_timeout(300)
        pg.screenshot(path=f"{OUT}/{mode}_rank_panel.png")
        # apply best + play
        pg.click("#rank li .use"); pg.wait_for_timeout(800)
        pg.screenshot(path=f"{OUT}/{mode}_best_top.png")
        pg.evaluate("window.__studio.setView('3d')")
        pg.click("#btnPlay"); pg.wait_for_timeout(6000)
        pg.screenshot(path=f"{OUT}/{mode}_live_3d.png")
        pg.evaluate("window.__studio.setOverlay('crowd'); window.__studio.setView('top')"); pg.wait_for_timeout(1500)
        pg.screenshot(path=f"{OUT}/{mode}_live_heat.png")
    print("\n".join(logs[:40]))
    b.close()
