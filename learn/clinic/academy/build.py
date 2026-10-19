"""Build the Academy page: python learn/clinic/academy/build.py  ->  learn/clinic/academy/index.html
Packs every level's README, starter (quest.py), check.py and data files, plus lessons.json, into one page."""
import json, os, re, glob
HERE = os.path.dirname(os.path.abspath(__file__)); LEVELS = os.path.join(HERE, "..", "levels")
lessons = json.load(open(os.path.join(HERE, "lessons.json")))
levels = {}
for n, ls in lessons.items():
    n = int(n)
    if n == 0:
        levels[0] = {"title": ls["title"], "xp": ls["xp"], "track": "shell", "dir": "", "readme": "", "starter": "", "check": "", "files": {}, "lesson": ls}
        continue
    d = glob.glob(os.path.join(LEVELS, f"L{n:02d}_*"))[0]
    readme = open(os.path.join(d, "README.md")).read()
    head = readme.splitlines()[0].lstrip("# ").strip()
    title, xp = head.rsplit("·", 1)
    title = re.sub(r"[^\w\s:,.'()&/-]", "", title).strip()               # no emoji in the UI
    files = {f: open(os.path.join(d, f)).read() for f in os.listdir(d) if f.endswith(".csv")}
    levels[n] = {"title": title, "xp": int(xp.split()[0]), "track": ls["track"], "dir": os.path.basename(d), "readme": readme,
                 "starter": open(os.path.join(d, "quest.py")).read(), "check": open(os.path.join(d, "check.py")).read(), "files": files, "lesson": ls}
data = json.dumps({"levels": levels}).replace("</", "<\\/")
html = open(os.path.join(HERE, "template.html")).read().replace("__DATA__", data)
open(os.path.join(HERE, "index.html"), "w").write(html)
print("built", len(levels), "levels,", len(html) // 1024, "KB")
