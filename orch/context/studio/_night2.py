import json
from playwright.sync_api import sync_playwright
exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])
out={}
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e))); boot(pg)
    print(pg.evaluate("window.__studio.items.map(i=>i.type+'@'+i.x.toFixed(1)+','+i.z.toFixed(1)+(i.locked?'L':''))"))
    for B in [1,2]:
        r=pg.evaluate("b=>{const D=window.__studio.dbg; Object.assign(D.SCEN,{baths:b,arr:'spread',drinks:'medium',smoke:0.5}); return D.nightStats(20);}",B)
        out[B]=r
        for c in r['chapters']: print(B,c['time'],c['title'],{k:c[k]['m'] for k in ['in','dance','dl','rl','balc','litter']})
        print(B,{k:(v['m'],v['hw']) for k,v in r['totals'].items()})
    json.dump(out,open('_night2.json','w'),indent=1); print('errors',errs); b.close()
