"""Room Studio Playwright boot helper (shared by _chk*, _night2, _all2).

T-015 rebuild: consumers exec() the prelude (everything before the
`mode = sys.argv[1]` line). Prelude must define ARGS and boot(pg).

ARGS copied from _err.py (SwiftShader Chromium flags).
Paths are repo-relative (script dir / cwd when exec'd). three.js from CDN
unless MOTION_THREE_ROOT points at a local three.js package.

Smoke: python3 _t2.py smoke
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# When sibling scripts exec() this prelude, __file__ is undefined — use cwd.
try:
    STUDIO_DIR = Path(__file__).resolve().parent
except NameError:
    STUDIO_DIR = Path.cwd()
SRC = STUDIO_DIR / "index.html"
TEST = STUDIO_DIR / "_test.html"
SHOTS = STUDIO_DIR / "shots"

# Optional local three.js (no hard-coded /home/claude path). CDN is default.
_THREE_ENV = os.environ.get("MOTION_THREE_ROOT", "").strip()
LOCAL_THREE = Path(_THREE_ENV) if _THREE_ENV else None

# Exact set from orch/context/studio/_err.py
ARGS = [
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--allow-file-access-from-files",
]


def resolve_chrome() -> str | None:
    """Prefer env override, then Playwright cache chromium."""
    env = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH", "").strip()
    if env and Path(env).is_file():
        return env
    home = Path.home() / ".cache" / "ms-playwright"
    if home.is_dir():
        candidates = sorted(home.glob("chromium-*/chrome-linux/chrome"), reverse=True)
        for c in candidates:
            if c.is_file():
                return str(c)
    return None


def _patch_chromium_launch() -> None:
    """Make sibling scripts' `p.chromium.launch(args=ARGS)` find cached Chrome."""
    try:
        from playwright.sync_api import BrowserType
    except ImportError:
        return
    if getattr(BrowserType.launch, "_motion_patched", False):
        return
    _orig = BrowserType.launch

    def launch(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        exe = resolve_chrome()
        if exe and not kwargs.get("executable_path"):
            kwargs["executable_path"] = exe
        kwargs.setdefault("headless", True)
        return _orig(self, *args, **kwargs)

    launch._motion_patched = True  # type: ignore[attr-defined]
    BrowserType.launch = launch  # type: ignore[method-assign]


_patch_chromium_launch()


def prepare_test_html() -> Path:
    """Build `_test.html` from index: CDN three.js (or MOTION_THREE_ROOT), strip fonts."""
    if not SRC.exists():
        raise FileNotFoundError(f"studio index missing: {SRC}")
    html = SRC.read_text(encoding="utf-8")
    if LOCAL_THREE is not None:
        three_js = LOCAL_THREE / "build" / "three.min.js"
        orbit = LOCAL_THREE / "examples" / "js" / "controls" / "OrbitControls.js"
        if three_js.is_file() and orbit.is_file():
            html = html.replace(
                "https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js",
                three_js.as_uri(),
            )
            html = html.replace(
                "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js",
                orbit.as_uri(),
            )
    # Google Fonts unreachable in sandbox; drop so boot does not stall
    html = "\n".join(l for l in html.splitlines() if "fonts.g" not in l)
    wrapped = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'></head><body>"
        + html
        + "</body></html>"
    )
    TEST.write_text(wrapped, encoding="utf-8")
    return TEST


def boot(pg, timeout_s: float = 90.0) -> None:
    """Load Studio page, clear localStorage, wait for window.__studio."""
    prepare_test_html()
    url = TEST.resolve().as_uri()
    pg.goto(url, wait_until="commit")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        pg.wait_for_timeout(500)
        try:
            if pg.evaluate("!!window.__studio"):
                break
        except Exception:
            pass
    else:
        raise TimeoutError("window.__studio not ready after first load")
    pg.evaluate("localStorage.clear()")
    pg.reload(wait_until="commit")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        pg.wait_for_timeout(400)
        try:
            if pg.evaluate("!!window.__studio"):
                return
        except Exception:
            pass
    raise TimeoutError("window.__studio not ready after localStorage clear")


def smoke_info(pg) -> dict:
    return pg.evaluate(
        """() => {
          const s = window.__studio;
          if (!s) return {ok: false};
          const e = s.ENV || {};
          return {
            ok: true,
            items: (s.items || []).length,
            hasDbg: !!s.dbg,
            stations: e.stations ? e.stations.length : null,
            baths_default: (s.dbg && s.dbg.SCEN && s.dbg.SCEN.baths) || null,
          };
        }"""
    )


# ---- standalone CLI (sibling scripts exec() everything above this line) ----
mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"

if __name__ == "__main__" or mode in {"smoke", "basic", "boot"}:
    from playwright.sync_api import sync_playwright

    SHOTS.mkdir(parents=True, exist_ok=True)
    errs: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=ARGS)
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        page.on("pageerror", lambda e: errs.append(str(e)))
        boot(page, timeout_s=90)
        info = smoke_info(page)
        page.wait_for_timeout(800)
        shot = SHOTS / f"t2_{mode}.png"
        page.screenshot(path=str(shot))
        browser.close()
    out = {
        "helper": "_t2.py",
        "mode": mode,
        "studio": info,
        "errors": errs[:5],
        "screenshot": str(shot) if info.get("ok") else None,
        "chrome": resolve_chrome(),
        "label": "confirmed" if info.get("ok") and not errs else "estimate",
    }
    print(json.dumps(out, indent=2))
    sys.exit(0 if info.get("ok") and not errs else 1)
