import json,time
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={"width":1600,"height":1000}); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e))); boot(pg)
    import sys; B=int(sys.argv[1]); pg.evaluate("b=>Object.assign(window.__studio.dbg.SCEN,{baths:b,arr:'spread',drinks:'medium',smoke:0.5})",B); t0=time.time(); pg.evaluate("window.__studio.optimizeEverything()")
    while True:
        pg.wait_for_timeout(20000)
        st=pg.evaluate("({r:window.__studio.ranking,t:document.querySelector('#rankProgTxt').textContent})")
        print(round(time.time()-t0),st['t'][:120],flush=True)
        if not st['r'] or errs: break
        if time.time()-t0>3000: break
    R=pg.evaluate(r"""()=>{ const R=window.__studio.lastReport; if(!R) return null; const f=r=>r&&({t:r.title,score:+(r.score||0).toFixed(2),ciPct:+((r.ciPct||0)*100).toFixed(1),n:r.n,ok:r.ok,tie:r.tieWithBest,jam:r.jamMin&&+r.jamMin.toFixed(1),litter:r.litter&&+r.litter.toFixed(1),resc:r.rescues});
      return {ms:R.ms, sound:{cands:R.sound.candidates, top:R.sound.top.map(c=>Object.assign(f(c),{s:c.s,spread:c.spread,depth:c.depth,snd:{sd:+c.snd.sd.toFixed(2),w3:+c.snd.within3.toFixed(2),hot:+c.snd.hot.toFixed(1),dj:+c.snd.djSpill.toFixed(1)},eg:Math.round(c.egIn),rest:Math.round(c.restIn)})), win:{s:R.sound.win.s,spread:R.sound.win.spread,depth:R.sound.win.depth}},
        drinks:{tested:R.drinks.tested, top:R.drinks.top.map(f)}, bins:{top:R.bins.top.map(f), none:f(R.bins.none)}, ball:{top:R.ball.top.map(r=>Object.assign(f(r),{m:r.mline}))}, final:f(R.final),
        items:window.__studio.items.map(i=>({t:i.type,x:i.x,z:i.z,rot:Math.round(i.rot*57.2958),s:i.surface,l:i.locked,serves:i.serves}))}; }""")
    json.dump(R,open(f"_report_b{B}.json","w"),indent=1); 
    pg.screenshot(path="shots/all_panel_b{B}.png"); pg.evaluate("window.__studio.setView('top')"); pg.wait_for_timeout(800); pg.screenshot(path=f"shots/all_top_b{B}.png")
    print("errors",errs); b.close()
