import json
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
JS=r"""()=>{ const S=window.__studio, D=S.dbg; const its=S.items.map(i=>Object.assign({},i));
  const run=(its,seed,mode,steps)=>{ const env=D.buildEnv(its); const sim=new D.Sim(env,seed,70,mode); for(let k=0;k<(steps||5400);k++) sim.step(0.5);
     return Object.assign(sim.score(env),{m:Object.assign({},sim.m),inside:sim.inside?sim.inside():null,bins:env.bins?env.bins.length:-1}); };
  const a=run(its,1234), b=run(its,1234);
  const det=JSON.stringify(a)===JSON.stringify(b);
  const reps=[]; for(let s=0;s<10;s++) reps.push(run(its,1000+s*7919));
  const sc=reps.map(r=>r.score), m=sc.reduce((x,y)=>x+y,0)/10, sd=Math.sqrt(sc.reduce((x,y)=>x+(y-m)**2,0)/9);
  const rot=S.items.map(i=>i.type+':'+(i.rot*180/Math.PI).toFixed(1));
  // with a trash bin near the island
  const bin={id:999,type:'trash',x:0,z:0,rot:0}; const st=D.buildEnv(its).stations[0];
  const tr=[]; for(let s=0;s<4;s++) tr.push(run(its,1000+s*7919));
  const night=run(its,77,'night',Math.round(5.5*3600/0.5));
  return {det, mean:+m.toFixed(2), ciPct:+(2.262*sd/Math.sqrt(10)/m*100).toFixed(1), litter:reps.map(r=>+r.litter.toFixed(0)), tossed:reps.map(r=>r.tossed),
    rescues:reps.map(r=>r.m.rescues), nan:reps.map(r=>r.m.nan), giveups:reps.map(r=>r.m.giveups), rot,
    night:{score:+night.score.toFixed(1),inside:night.inside,rescues:night.m.rescues,nan:night.m.nan,litter:night.litter,trips:night.trips}}; }"""
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={"width":1200,"height":800}); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e))); boot(pg)
    print(json.dumps(pg.evaluate(JS))); print("errors",errs); b.close()
