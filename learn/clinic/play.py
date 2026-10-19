"""Clinic Quest: python learn/clinic/play.py [level]"""
import importlib.util, os, sys, glob, io, contextlib, traceback
ROOT = os.path.dirname(os.path.abspath(__file__))
RANKS = [(0, "🩺 Intern"), (300, "💉 Resident"), (700, "🥼 Attending"), (1200, "🏥 Chief of Staff"), (1800, "👑 Founder")]

def levels():
    out = []
    for d in sorted(glob.glob(os.path.join(ROOT, "levels", "L*"))):
        meta = open(os.path.join(d, "README.md")).readline().strip("# \n")
        xp = int(meta.rsplit("·", 1)[-1].strip().split()[0])
        out.append((int(os.path.basename(d)[1:3]), d, meta.rsplit("·", 1)[0].strip(), xp))
    return out

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(ROOT, "levels")); spec.loader.exec_module(m); return m

def check(n, d, quiet=True):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            q = load(os.path.join(d, "quest.py"), f"quest{n}"); load(os.path.join(d, "check.py"), f"check{n}").run(q)
        return True, buf.getvalue()
    except AssertionError as e: return False, str(e)
    except TypeError as e:
        if "NoneType" in str(e) or "ellipsis" in str(e): return False, "not started yet: a function still has `...` instead of code"
        return False, f"{type(e).__name__}: {e}" + ("" if quiet else "\n" + traceback.format_exc(limit=2))
    except Exception as e: return False, f"{type(e).__name__}: {e}" + ("" if quiet else "\n" + traceback.format_exc(limit=2))

def rank(xp):
    r = [name for need, name in RANKS if xp >= need][-1]
    nxt = next(((need, name) for need, name in RANKS if need > xp), None)
    return r, nxt

if __name__ == "__main__":
    L = levels()
    if len(sys.argv) > 1:
        n = int(sys.argv[1]); hit = [x for x in L if x[0] == n]
        if not hit: sys.exit(f"no level {n}")
        _, d, title, xp = hit[0]; ok, msg = check(n, d, quiet=False)
        print(f"Level {n}: {title}")
        print(("✅ CLEARED  +%d XP" % xp) if ok else "❌ not yet: " + msg)
        if ok and msg.strip(): print(msg.rstrip())
        sys.exit(0 if ok else 1)
    xp = 0; nxt = None
    print("\n   DR. KIM'S CLINIC · build log\n")
    for n, d, title, pts in L:
        ok, msg = check(n, d)
        xp += pts if ok else 0
        if not ok and nxt is None: nxt = (n, title, msg)
        print(f"   {'✅' if ok else ('🔓' if nxt and nxt[0] == n else '🔒')}  L{n:02d}  {title:<42} {pts:>4} XP")
    r, up = rank(xp)
    bar = "█" * min(20, int(20 * xp / 1800)) + "░" * (20 - min(20, int(20 * xp / 1800)))
    print(f"\n   {bar}  {xp} XP · {r}")
    if up: print(f"   {up[0] - xp} XP to {up[1]}")
    if nxt: print(f"\n   Next quest: level {nxt[0]}, {nxt[1]}  →  learn/clinic/levels/L{nxt[0]:02d}_*/README.md\n   Status: {nxt[2]}")
    else: print("\n   Every level cleared. Dr. Kim's pain clinic runs on your code. 👑")
