"""Kitchen / hall clear-floor sim from orch/context/assets/geom.py.

Run from this folder (or any cwd): pip install shapely; python kitchen_hall_sim.py
"""
import sys
from pathlib import Path

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# geom lives in orch/context/assets, not next to this script.
_here = Path(__file__).resolve()
for _parent in _here.parents:
    _assets = _parent / "orch" / "context" / "assets"
    if (_assets / "geom.py").is_file():
        sys.path.insert(0, str(_assets))
        break
else:
    raise SystemExit("could not find orch/context/assets/geom.py from " + str(_here))

import geom as g
f = (g.IN_PX / 12) ** 2  # plan px^2 -> sq ft
ext = Polygon(g.EXT)
closed = unary_union([Polygon(p) for p in g.ROOMS.values()] + [Polygon(g.BALC)])
openp = ext.difference(closed)
fixed = unary_union([Polygon(p) for p in g.FIXED.values()])
clear = openp.difference(fixed)
for name, b in {"best": (600, 340, 815, 545), "low": (620, 355, 815, 545), "high": (580, 330, 815, 545)}.items():
    k = box(*b).intersection(openp)
    c = k.difference(fixed).area * f
    print(f"kitchen {name}: gross {k.area*f:.0f} sq ft, clear {c:.0f} sq ft, {c/7:.0f} people @7")
print(f"open plan: gross {openp.area*f:.0f}, clear {clear.area*f:.0f}")
print(f"living + hall clear: {clear.difference(box(600,340,815,545)).area*f:.0f}")
