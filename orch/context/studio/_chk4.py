import json
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={"width":1200,"height":800}); boot(pg)
    pg.evaluate("window.__studio.items.length")
    print(pg.evaluate(r"""()=>{ const S=window.__studio,D=S.dbg,ballCheck=D.ballCheck,describeBall=D.describeBall,cellOf=D.cellOf,CAT=D.CAT,G=D.G(),buildEnv=D.buildEnv; const rig=D.rigLayout(4.5,4.6,4.25); const others=S.items.filter(i=>i.type!=='dj_rig'&&i.type!=='speaker'&&!CAT[i.type].ball).concat(rig);
      const out=[]; for(let x=0.75;x<=3.0;x+=0.25) for(const z of [2.25,3.25,4.25]){ const c=ballCheck(x,z,'hook',others); out.push([x,z,c.ok,c.why.join('/'), +G.tallClear[cellOf(x,z)].toFixed(2), describeBall(x,z,others)]); }
      const env=buildEnv(others); const DC=[env.danceFront[0]+env.danceDir[0]*5,env.danceFront[1]+env.danceDir[1]*5];
      return {DC, wallA:G.wallA, out:out.filter(o=>o[2]||o[0]<2.6)}; }"""))
    b.close()
