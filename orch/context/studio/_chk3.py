import json
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
JS=r"""()=>{ const S=window.__studio, D=S.dbg, G=D.G();
  const rig=D.rigLayout(4.5,4.6,4.25); const others=S.items.filter(i=>i.type!=='dj_rig'&&i.type!=='speaker'); const its=others.concat(rig);
  const env=D.buildEnv(its); const sq=D.soundReport(its,env);
  // toe-in: aim each speaker at a point 12 ft out from the table centre
  const r=rig[0]; const T=[r.x+Math.sin(r.rot)*12, r.z+Math.cos(r.rot)*12];
  const toed=its.map(i=>i.type==='speaker'?Object.assign({},i,{rot:Math.atan2(T[0]-i.x,T[1]-i.z)}):i);
  const te=D.soundReport(toed,env);
  const W=p=>[p[0],p[1]]; 
  return {sq,te,toe:toed.filter(i=>i.type==='speaker').map(i=>+(i.rot*57.3).toFixed(1)), rig}; }"""
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={"width":1200,"height":800}); boot(pg)
    print(json.dumps(pg.evaluate(JS),indent=0)); b.close()
