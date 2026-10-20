"""Quick page-error probe for Studio _test.html (repo-relative)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

STUDIO_DIR = Path(__file__).resolve().parent
TEST = STUDIO_DIR / "_test.html"

# Ensure _test.html exists via _t2 prepare path when possible
try:
    exec(open(STUDIO_DIR / "_t2.py").read().split("mode = sys.argv[1]")[0])
    prepare_test_html()  # noqa: F821 — from exec'd prelude
except Exception:
    # Fallback: thin wrap of index with CDN three.js (no local /home paths)
    src = (STUDIO_DIR / "index.html").read_text(encoding="utf-8")
    src = "\n".join(l for l in src.splitlines() if "fonts.g" not in l)
    TEST.write_text(
        "<!doctype html><html><head><meta charset='utf-8'></head><body>"
        + src
        + "</body></html>",
        encoding="utf-8",
    )

ARGS = [
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--allow-file-access-from-files",
]

with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    pg = b.new_page()
    L = []
    pg.on("pageerror", lambda e: L.append(str(e)))
    pg.on("console", lambda m: L.append(m.type + " " + m.text) if m.type == "error" else None)
    pg.goto(TEST.resolve().as_uri())
    pg.wait_for_timeout(8000)
    print(L[:5])
    b.close()
