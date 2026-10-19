import os, sys, importlib.util
def run(q):
    p = os.path.join(os.path.dirname(__file__), "notes.md")
    assert os.path.exists(p), "write notes.md in this folder (see the README)"
    t = open(p).read()
    for sec in ["## Brief", "## What I checked", "## What I'd brief differently"]:
        assert sec in t, f"notes.md needs a section {sec!r}"
        body = t.split(sec, 1)[1].split("\n## ", 1)[0]
        assert len([l for l in body.splitlines() if l.strip()]) >= 2, f"section {sec!r} needs at least 2 lines"
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from _lib import level
    for n in (6, 10):
        d = [x for x in os.listdir(os.path.dirname(os.path.dirname(__file__))) if x.startswith(f"L{n:02d}_")][0]
        spec = importlib.util.spec_from_file_location(f"c{n}", os.path.join(os.path.dirname(os.path.dirname(__file__)), d, "check.py"))
        c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c); c.run(level(n))
