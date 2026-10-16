import json
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
JS=r"""()=>{ const S=window.__studio, D=S.dbg; const its=S.items.map(i=>Object.assign({},i));
  const env0=D.buildEnv(its); const sp=D.wallSpots('trash',env0,its,{awayFromSound:true,spacing:3,max:12,entryGap:3.5});
  const run=(its,seed)=>{ const env=D.buildEnv(its); const sim=new D.Sim(env,seed,70); for(let k=0;k<5400;k++) sim.step(0.5); return Object.assign(sim.score(env),{m:Object.assign({},sim.m),nb:env.bins.length}); };
  const out=[]; for(const c of sp.slice(0,6)){ const it2=its.concat([{id:900,type:'trash',x:c.x,z:c.z,rot:c.rot}]); const r=[0,1,2].map(k=>run(it2,1000+k*7919));
    out.push({x:c.x,z:c.z,rot:+(c.rot*57.3).toFixed(0),nb:r[0].nb,score:+(r.reduce((a,b)=>a+b.score,0)/3).toFixed(1),litter:r.map(x=>+x.litter.toFixed(0)),tossed:r.map(x=>x.tossed),resc:r.map(x=>x.m.rescues),jam:+(r.reduce((a,b)=>a+b.jamMin,0)/3).toFixed(1)}); }
  const G=D.G(); return {u:G.u,n:G.n,wallLen:G.wallLen,spots:sp.length,out}; }"""
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={"width":1200,"height":800}); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e))); boot(pg)
    print(json.dumps(pg.evaluate(JS),indent=0)); print("errors",errs); b.close()
