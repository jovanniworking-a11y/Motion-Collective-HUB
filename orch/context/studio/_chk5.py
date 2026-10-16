import json
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={"width":1200,"height":800}); boot(pg)
    print(pg.evaluate(r"""()=>{ const S=window.__studio,D=S.dbg,G=D.G(); const rig=D.rigLayout(4.5,4.6,4.25);
      const others=S.items.filter(i=>i.type!=='dj_rig'&&i.type!=='speaker'&&!D.CAT[i.type].ball).concat(rig);
      const env=D.buildEnv(others); const sim=new D.Sim(env,1000,70); for(let s=0;s<5400;s++) sim.step(0.5); const H=sim.heatAll;
      const g=G.grid, CS=0.5; const cx=c=>g.minx+(c%g.nx+0.5)*CS, cz=c=>g.minz+(((c/g.nx)|0)+0.5)*CS;
      const near=(x,z,r)=>{ let s=0; for(let c=0;c<g.N;c++) if(Math.hypot(cx(c)-x,cz(c)-z)<=r) s+=H[c]; return s/60; };
      const pts=[[1.75,3.25],[2.25,3.25],[2.25,2.25],[2.25,4.25],[12.68,-4.74],[10.75,3.25]];
      return pts.map(p=>[p, +near(p[0],p[1],2).toFixed(1), D.ballCheck(p[0],p[1],'hook',others).ok]); }"""))
    b.close()
