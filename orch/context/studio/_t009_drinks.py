"""T-009: drink-spot + stock sims for 150-cocktail menu (lemonade + paloma).

Geometry already baked — no venue visit. Maps Studio MIX.jj dispenser share
to the 16 Oct menu (90 entry lemonades + 60 Palomas) per orch/context/DRIVE_INDEX.md.
Does not edit SoT. Numbers labeled estimate unless noted.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

exec(open("_t2.py").read().split("mode = sys.argv[1]")[0])

OUT = Path(__file__).resolve().parent
OUTBOX = Path(__file__).resolve().parents[2] / "tasks" / "outbox"
OUTBOX.mkdir(parents=True, exist_ok=True)

# Menu (confirmed 16 Oct per DRIVE_INDEX / SoT pointer) — cocktail split inside dispenser share
LEMONADE = 90  # confirmed (menu count)
PALOMA = 60  # confirmed (menu count)
COCKTAILS = LEMONADE + PALOMA  # 150 confirmed


def main() -> int:
    t0 = time.time()
    errs: list[str] = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)  # noqa: F821
        pg = b.new_page(viewport={"width": 1200, "height": 800})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        boot(pg)  # noqa: F821

        # Kick drink-spot optimizer (exposed on __studio; core stays internal)
        pg.evaluate("window.__studio.optimizeDrinks()")
        deadline = time.time() + 2400  # hard cap ~40 min
        prog = ""
        while time.time() < deadline:
            pg.wait_for_timeout(5000)
            st = pg.evaluate(
                """() => ({
                  ranking: !!window.__studio.ranking,
                  prog: (document.querySelector('#rankProgTxt')||{}).textContent || '',
                  n: window.__studio.rankResults && window.__studio.rankResults.list
                    ? window.__studio.rankResults.list.length : 0,
                })"""
            )
            prog = st.get("prog") or prog
            print(f"[{round(time.time()-t0)}s] ranking={st['ranking']} n={st['n']} {prog[:100]}", flush=True)
            if not st["ranking"]:
                break
            if errs:
                break
        else:
            errs.append("optimizeDrinks timed out")

        result = pg.evaluate(
            """() => {
              const rr = window.__studio.rankResults;
              const list = (rr && rr.list) ? rr.list : [];
              const top = list.slice(0, 6).map(r => ({
                title: r.title,
                score: +(r.score||0).toFixed(2),
                ciPct: +((r.ciPct||0)*100).toFixed(1),
                n: r.n,
                ok: r.ok,
                jam: r.jamMin != null ? +r.jamMin.toFixed(2) : null,
                avgTrip: r.avgTrip != null ? +r.avgTrip.toFixed(3) : null,
                qPeak: r.qPeak != null ? +r.qPeak.toFixed(2) : null,
                tie: !!r.tieWithBest,
              }));
              return {
                win: top[0] || null,
                tested: list.length,
                top,
                N: 70,
                prog: (document.querySelector('#rankProgTxt')||{}).textContent || '',
              };
            }"""
        )

        # Apply best drink layout so nightStats use winning spots
        pg.evaluate(
            """() => {
              const rr = window.__studio.rankResults;
              if (rr && rr.list && rr.list[0] && typeof rr.apply === 'function') {
                rr.apply(rr.list[0]);
              }
            }"""
        )
        pg.wait_for_timeout(500)

        # Night stock: pours from our stations vs BYOB across baths 1|2, medium/spread
        stock = {}
        for baths in (1, 2):
            stock[baths] = pg.evaluate(
                """(b) => {
                  const D = window.__studio.dbg;
                  Object.assign(D.SCEN, {baths: b, arr: 'spread', drinks: 'medium', smoke: 0.5});
                  const r = D.nightStats(20);
                  const t = r.totals || {};
                  const m = k => t[k] ? t[k].m : null;
                  const hw = k => t[k] ? t[k].hw : null;
                  return {
                    trips: {m: m('trips'), hw: hw('trips'), label: 'estimate'},
                    byob: {m: m('byob'), hw: hw('byob'), label: 'estimate'},
                    litter: {m: m('litter'), hw: hw('litter'), label: 'estimate'},
                    tossed: {m: m('tossed'), hw: hw('tossed'), label: 'estimate'},
                    avgTrip: {m: m('avgTrip'), hw: hw('avgTrip'), label: 'estimate'},
                    peakDl: {m: m('peakDl'), hw: hw('peakDl'), label: 'estimate'},
                    restWait: {m: m('restWait'), hw: hw('restWait'), label: 'estimate'},
                  };
                }""",
                baths,
            )

        # Studio MIX constants (not on dbg) — read from page source contract in AGENTS.md / index comment
        mix = {"jj": 0.60, "beer": 0.22, "seltzer": 0.18, "source": "orch/context/studio/index.html MIX"}

        b.close()

    jj_share = float(mix["jj"])
    beer_share = float(mix["beer"])
    selt_share = float(mix["seltzer"])

    stock_plan = {}
    for baths, s in stock.items():
        trips = (s.get("trips") or {}).get("m") or 0
        byob = (s.get("byob") or {}).get("m") or 0
        from_us = trips
        cocktails_from_sim = from_us * jj_share
        beer_from_sim = from_us * beer_share
        selt_from_sim = from_us * selt_share
        stock_plan[str(baths)] = {
            "our_pours_estimate": round(from_us, 1),
            "byob_rounds_estimate": round(byob, 1),
            "cocktail_pours_estimate": round(cocktails_from_sim, 1),
            "lemonade_pours_estimate": round(cocktails_from_sim * (LEMONADE / COCKTAILS), 1),
            "paloma_pours_estimate": round(cocktails_from_sim * (PALOMA / COCKTAILS), 1),
            "beer_pours_estimate": round(beer_from_sim, 1),
            "seltzer_pours_estimate": round(selt_from_sim, 1),
            "menu_cocktails_confirmed": COCKTAILS,
            "menu_vs_sim": {
                "menu": COCKTAILS,
                "sim_cocktail_pours": round(cocktails_from_sim, 1),
                "delta": round(cocktails_from_sim - COCKTAILS, 1),
                "note": "sim uses MIX ratios + nightStats; menu is planned stock (confirmed 16 Oct)",
            },
            "label": "estimate",
        }

    out = {
        "task": "T-009",
        "seat": "cursor",
        "seconds": round(time.time() - t0, 1),
        "menu": {
            "cocktails": COCKTAILS,
            "lemonade": LEMONADE,
            "paloma": PALOMA,
            "label": "confirmed",
            "source": "orch/context/DRIVE_INDEX.md (16 Oct Logistics Control)",
        },
        "mix": mix,
        "drink_spots": result,
        "night_stock": {str(k): v for k, v in stock.items()},
        "stock_plan": stock_plan,
        "errors": errs[:8],
        "label": "estimate",
    }
    path = OUT / "_t009_drinks.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    log = OUTBOX / "_t009_drinks.log"
    log.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": not errs and bool(result.get("win")),
                "path": str(path),
                "win": result.get("win"),
                "stock_plan": stock_plan,
                "errors": errs[:3],
                "seconds": out["seconds"],
            },
            indent=2,
        )
    )
    return 0 if not errs and result.get("win") else 1


if __name__ == "__main__":
    raise SystemExit(main())
