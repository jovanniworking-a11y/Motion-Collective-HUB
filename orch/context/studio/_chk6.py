import json
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={"width":1200,"height":800}); boot(pg)
    r=pg.evaluate(r"""async()=>{ const S=window.__studio,D=S.dbg; const rep={}; await D.optimizeBallCore({N:70,done:0,total:0},rep);
      const C=window.__ballCands; return {n:C.length, hooksNearWall:C.filter(c=>c.kind==='hook'&&c.bx<4).map(c=>[c.bx,c.bz,+c.score.toFixed(1),+c.hands.toFixed(1),+c.dv.toFixed(1)]), best:C.slice().sort((a,b)=>a.score-b.score).slice(0,5).map(c=>[c.kind,c.bx,c.bz,+c.score.toFixed(1),+c.ciPct.toFixed(3),c.n]), win:[rep.ball.win.bx,rep.ball.win.bz]}; }""")
    print(json.dumps(r)); b.close()
