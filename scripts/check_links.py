#!/usr/bin/env python3
"""Autonomous link + architecture check for the MOTION hub.

Fails when a crew-facing route, FastAPI path the panel calls, registry
"ready" file, or local HTML/markdown target is missing. Font packs under
media/ that are not in git are reported as open and do not fail the run
(teaser HTML falls back to system faces). Draft only — no network publish.

    python scripts/check_links.py
    python hub.py links
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "apps" / "ops-panel"
APP = PANEL / "src" / "app"
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".next",
    "hub_out",
    ".venv",
    "venv",
}
FONT_EXT = {".woff", ".woff2", ".ttf", ".otf", ".eot"}
MD_ROOTS = [
    ROOT / "README.md",
    ROOT / "ARCHITECTURE.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "apps",
    ROOT / "services",
    ROOT / "desktop",
    ROOT / "docs",
    ROOT / "ops",
    ROOT / "media",
]

failures: list[str] = []
open_items: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def walk_files(base: Path, suffixes: set[str]) -> list[Path]:
    if base.is_file():
        return [base] if base.suffix.lower() in suffixes else []
    out: list[Path] = []
    if not base.exists():
        return out
    for path in base.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in suffixes:
            out.append(path)
    return out


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def panel_page(route: str) -> Path | None:
    route = route.split("?")[0].split("#")[0]
    if not route.startswith("/"):
        return None
    rel = "page.tsx" if route == "/" else f"{route.strip('/')}/page.tsx"
    page = APP / rel
    if page.exists():
        return page
    public = PANEL / "public" / route.lstrip("/")
    if public.exists():
        return public
    return None


def require_route(route: str, source: str) -> None:
    if panel_page(route) is None:
        fail(f"{source}: route {route} has no page.tsx or public file")


def check_nav_and_shell() -> None:
    shell = read(PANEL / "src" / "components" / "AppShell.tsx")
    nav = re.findall(r'href:\s*"(/[^"]*)"', shell)
    if not nav or nav[0] != "/":
        fail("AppShell NAV is missing or does not start at /")
    for href in nav:
        require_route(href, "AppShell NAV")

    css = read(PANEL / "src" / "app" / "globals.css")
    nav_block = css.split(".bottom-nav {", 1)[-1].split("}", 1)[0]
    repeat = re.search(r"repeat\(\s*(\d+)", nav_block)
    if repeat and int(repeat.group(1)) != len(nav):
        fail(
            f"bottom-nav grid is repeat({repeat.group(1)}) but NAV has {len(nav)} links"
        )

    sw = read(PANEL / "public" / "sw.js")
    shell_routes = re.findall(r'"(/[^"]*)"', sw.split("SHELL", 1)[-1].split("];", 1)[0])
    for href in nav:
        if href not in shell_routes:
            fail(f"service worker SHELL does not precache NAV route {href}")
    for href in shell_routes:
        if href.startswith("/api"):
            continue
        require_route(href, "sw.js SHELL")

    readme = read(PANEL / "README.md")
    table = readme.split("## Routes", 1)[-1].split("## ", 1)[0]
    for token in re.findall(r"`(/[^`]+)`", table):
        require_route(token.strip(), "apps/ops-panel/README.md")


def check_library_urls() -> None:
    text = read(PANEL / "src" / "lib" / "ops-data.ts")
    for url in re.findall(r'url:\s*"([^"]+)"', text):
        if url.startswith("/") and "${" not in url:
            require_route(url, "LIBRARY_SEED")
        if "github.com/jovanniworking-a11y/Motion-Collective-HUB/blob/" in url:
            if "/blob/main/" not in url:
                fail(f"GitHub library link is not on main: {url}")


def normalize_api_path(raw: str) -> str:
    path = raw.split("?")[0].split("${")[0]
    path = re.sub(r"\$\{[^}]+\}", "{}", path)
    path = re.sub(r"\{[^}]+\}", "{}", path)
    if not path.startswith("/"):
        path = "/" + path
    return path.rstrip("/") or "/"


def fastapi_routes() -> dict[str, set[str]]:
    text = read(ROOT / "services" / "api" / "app" / "main.py")
    routes: dict[str, set[str]] = {}
    for method, path in re.findall(
        r'@app\.(get|post|put|patch|delete)\(\s*"([^"]+)"',
        text,
        flags=re.I,
    ):
        routes.setdefault(normalize_api_path(path), set()).add(method.lower())
    return routes


def check_api_client() -> None:
    text = read(PANEL / "src" / "lib" / "api.ts")
    routes = fastapi_routes()
    found: list[tuple[str, str]] = []
    for match in re.finditer(r'["`](/(?:health|api/|studio/)[^"`]*)["`]', text):
        raw = match.group(1)
        window = text[match.end() : match.end() + 500]
        window = re.split(r"\n  [A-Za-z][A-Za-z0-9]*:", window, maxsplit=1)[0]
        method_m = re.search(r'method:\s*"(GET|POST|PUT|PATCH|DELETE)"', window)
        method = method_m.group(1).lower() if method_m else "get"
        found.append((method, raw))
    if "/studio/embed" in text:
        found.append(("get", "/studio/embed"))
    if not any(path.startswith("/api/data/") for _, path in found):
        fail("api.ts does not call /api/data/* (Data page has no backend)")
    if not found:
        fail("api.ts: no client paths parsed")
        return
    for method, raw in found:
        path = normalize_api_path(re.sub(r"\$\{[^}]+\}", "{}", raw.split("?")[0]))
        methods = routes.get(path)
        if not methods:
            fail(f"api.ts calls {method.upper()} {raw} but FastAPI has no {path}")
            continue
        if method not in methods:
            fail(f"api.ts {method.upper()} {path} but FastAPI only has {sorted(methods)}")


def local_target(src: Path, link: str) -> Path | None:
    link = link.strip().strip("<>")
    if not link or link.startswith(("#", "mailto:", "javascript:", "data:", "http://", "https://", "//")):
        return None
    if "${" in link or link.startswith("{"):
        return None
    path = link.split("#", 1)[0].split("?", 1)[0].strip()
    if not path:
        return None
    # title leftover: foo.md "title"
    path = path.split()[0]
    # CSS filter ids and JS calls are not files. A real target has a slash or an extension.
    name = Path(path).name
    if "/" not in path and "." not in name:
        return None
    if path.startswith(("%", "#")):
        return None
    suffix = Path(path).suffix.lower()
    if suffix in FONT_EXT:
        target = (src.parent / path).resolve()
        if not target.exists():
            open_items.append(f"{src.relative_to(ROOT)} -> {path}")
        return None
    if path.startswith("/"):
        return (ROOT / path.lstrip("/")).resolve()
    return (src.parent / path).resolve()


def check_documents() -> None:
    md_link = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    attr = re.compile(r"(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", re.I)
    css_url = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)")
    files: list[Path] = []
    for base in MD_ROOTS:
        files.extend(walk_files(base, {".md"}))
    for html in walk_files(ROOT, {".html"}):
        # Product pages and creative sources. Skip nothing except vendor dumps.
        if "node_modules" in html.parts:
            continue
        files.append(html)
    seen: set[tuple[str, str]] = set()
    for path in files:
        text = read(path)
        links = md_link.findall(text) if path.suffix.lower() == ".md" else []
        if path.suffix.lower() == ".html":
            links.extend(attr.findall(text))
            links.extend(css_url.findall(text))
        for raw in links:
            target = local_target(path, raw)
            if target is None:
                continue
            key = (str(path.relative_to(ROOT)), raw.split()[0])
            if key in seen:
                continue
            seen.add(key)
            if not target.exists():
                fail(f"{key[0]} -> {raw.split()[0]}")


def check_registry() -> None:
    reg = ROOT / "hub" / "registry.csv"
    with reg.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if (row.get("status") or "").strip() != "ready":
                continue
            rel = (row.get("path") or "").strip()
            if not rel:
                fail(f"registry {row.get('id')} is ready with an empty path")
                continue
            if not (ROOT / rel).exists():
                fail(f"registry {row.get('id')} ready path missing: {rel}")


def main() -> int:
    check_nav_and_shell()
    check_library_urls()
    check_api_client()
    check_documents()
    check_registry()
    if open_items:
        print(f"open: {len(open_items)} local font file(s) not in git (system fallback)")
    if failures:
        print(f"FAIL {len(failures)} link/architecture check(s):")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("OK link + architecture check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
