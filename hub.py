#!/usr/bin/env python3
"""MOTION Hub — one place to find, open and run everything MOTION builds,
and to learn from every event.

    python hub.py                 interactive menu
    python hub.py list [--kind builder] [--area money] [--status ready]
    python hub.py search flyer
    python hub.py open room-studio      (an id from the list, or any path)
    python hub.py run drinks-build      (builders write into hub_out/<id>/)
    python hub.py board                 task board as a table
    python hub.py files [--ext .xlsx]   every file in the repo
    python hub.py check                 missing files / unregistered files
    python hub.py events | compare [E001] | lessons [--area flow]
    python hub.py add-metric E001 guests_total 52 --category attendance --unit people
    python hub.py add-lesson E001 flow "Line at the island at 23:30" "Second dispenser"
    python hub.py export                hub_catalog.xlsx with every table
"""
import argparse
import datetime as dt
import os
import platform
import subprocess
import sys
import webbrowser
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas is missing. Run:  pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "hub" / "registry.csv"
DATA = ROOT / "data"
EVENTS, METRICS, LESSONS = DATA / "events.csv", DATA / "metrics.csv", DATA / "lessons.csv"
BOARD = ROOT / "orch" / "tasks" / "BOARD.md"
OUT = ROOT / "hub_out"
SKIP_DIRS = {".git", "node_modules", "__pycache__", "hub_out", ".venv", "venv"}
KIND_BY_EXT = {
    ".html": "app", ".py": "script", ".js": "script", ".md": "doc", ".txt": "doc",
    ".xlsx": "workbook", ".csv": "data", ".json": "data", ".pdf": "pdf",
    ".pptx": "deck", ".png": "image", ".jpg": "image", ".jpeg": "image",
    ".mp4": "video", ".mov": "video",
}

pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 60)
pd.set_option("display.max_rows", 500)


# ---------- loading ----------

def load_registry():
    df = pd.read_csv(REGISTRY, dtype=str).fillna("")
    df["exists"] = df["path"].map(lambda p: (ROOT / p).exists())
    return df


def load_board():
    rows = [l for l in BOARD.read_text(encoding="utf-8").splitlines() if l.startswith("| T-")]
    cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
    return pd.DataFrame(cells, columns=["id", "task", "owner", "status"])


def scan_files():
    rows = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(ROOT).as_posix()
            st = p.stat()
            rows.append({
                "path": rel, "ext": p.suffix.lower(),
                "kind": KIND_BY_EXT.get(p.suffix.lower(), "other"),
                "kb": round(st.st_size / 1024, 1),
                "modified": dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
    return pd.DataFrame(rows).sort_values("path", ignore_index=True)


def load_metrics():
    m = pd.read_csv(METRICS, dtype={"event_id": str})
    for col in ("planned", "actual"):
        m[col] = pd.to_numeric(m[col], errors="coerce")
    return m


def show(df, cols=None):
    if df.empty:
        print("(nothing)")
        return
    print((df[cols] if cols else df).to_string(index=False))


# ---------- open / run ----------

def resolve(target):
    reg = load_registry()
    hit = reg[reg["id"] == target]
    if not hit.empty:
        return hit.iloc[0]
    path = ROOT / target
    if path.exists():
        return pd.Series({"id": target, "path": target, "action": "open", "command": "", "status": "ready"})
    sys.exit(f"Not found: {target}. Try:  python hub.py search {target}")


def open_path(path):
    path = Path(path)
    if path.suffix.lower() == ".html":
        webbrowser.open(path.as_uri())
    elif platform.system() == "Windows":
        os.startfile(path)  # noqa: only exists on Windows
    elif platform.system() == "Darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)
    print(f"Opened {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")


def cmd_open(target):
    item = resolve(target)
    path = ROOT / item["path"]
    if not path.exists():
        sys.exit(f"{item['path']} is missing ({item.get('status', '')}).")
    open_path(path)


def cmd_run(target, force=False):
    item = resolve(target)
    if item["action"] != "run":
        sys.exit(f"{item['id']} isn't runnable - use:  python hub.py open {item['id']}")
    if item["status"] != "ready" and not force:
        sys.exit(f"{item['id']} is '{item['status']}': {item.get('notes', '')}\n"
                 f"Fix that first, or run anyway with --force.")
    script = ROOT / item["path"]
    exe = sys.executable if item["command"] in ("", "python") else item["command"]
    out = OUT / item["id"]
    out.mkdir(parents=True, exist_ok=True)
    print(f"Running {item['path']}  ->  output in {out.relative_to(ROOT)}")
    # Builders write into the current folder, so run them in hub_out/<id>/
    # and never overwrite the committed copies in orch/context/.
    code = subprocess.run([exe, str(script)], cwd=out).returncode
    made = [p.name for p in out.iterdir()]
    print(f"Exit {code}. Files in {out.relative_to(ROOT)}: {', '.join(made) or '(none)'}")


# ---------- learning ----------

def cmd_compare(event_id=None):
    m = load_metrics()
    if event_id:
        m = m[m["event_id"] == event_id]
    m = m.assign(diff=m["actual"] - m["planned"])
    m["diff_%"] = (m["diff"] / m["planned"] * 100).round(1)
    show(m, ["event_id", "category", "metric", "unit", "planned", "actual", "diff", "diff_%", "status"])
    filled = m["actual"].notna().sum()
    print(f"\n{filled}/{len(m)} metrics have actuals. Fill the rest after the event "
          f"(data/DEBRIEF_TEMPLATE.md), or:  python hub.py add-metric <event> <metric> <value>")
    # Once there are several events, show each metric side by side.
    if m["event_id"].nunique() > 1:
        print("\nActuals by event:")
        print(m.pivot_table(index="metric", columns="event_id", values="actual").to_string())


def cmd_add_metric(event_id, metric, value, category, unit, planned):
    m = pd.read_csv(METRICS, dtype=str).fillna("")
    mask = (m["event_id"] == event_id) & (m["metric"] == metric)
    if mask.any():
        m.loc[mask, "actual"] = value
        if planned:
            m.loc[mask, "planned"] = planned
        m.loc[mask, "status"] = "confirmed"
    else:
        m.loc[len(m)] = {"event_id": event_id, "category": category, "metric": metric, "unit": unit,
                         "planned": planned, "actual": value, "status": "confirmed",
                         "source": "hub add-metric", "notes": ""}
    m.to_csv(METRICS, index=False)
    print(f"Saved {event_id}.{metric} = {value}")


def cmd_add_lesson(event_id, area, lesson, next_time):
    l = pd.read_csv(LESSONS, dtype=str).fillna("")
    l.loc[len(l)] = {"event_id": event_id, "date": dt.date.today().isoformat(), "area": area,
                     "lesson": lesson, "next_time": next_time, "source": "hub add-lesson"}
    l.to_csv(LESSONS, index=False)
    print(f"Saved lesson for {event_id} ({area}).")


# ---------- check / export ----------

def cmd_check():
    reg = load_registry()
    missing = reg[~reg["exists"]]
    print("Registered but missing on disk:" if not missing.empty else "Every registered path exists.")
    show(missing, ["id", "path", "status"]) if not missing.empty else None
    blocked = reg[reg["status"].isin(["needs-path-fix", "missing-file"])]
    print("\nNot runnable yet:")
    show(blocked, ["id", "status", "notes"])
    files = scan_files()
    covered = reg["path"].tolist()
    loose = files[~files["path"].map(lambda p: any(p == c or p.startswith(c.rstrip("/") + "/") for c in covered))]
    print(f"\n{len(loose)} files are not in hub/registry.csv (add the ones worth a shortcut):")
    show(loose, ["path", "kind", "kb"])


def cmd_export():
    target = ROOT / "hub_catalog.xlsx"
    with pd.ExcelWriter(target) as xw:
        load_registry().to_excel(xw, sheet_name="Software", index=False)
        load_board().to_excel(xw, sheet_name="Board", index=False)
        pd.read_csv(EVENTS).to_excel(xw, sheet_name="Events", index=False)
        load_metrics().to_excel(xw, sheet_name="Metrics", index=False)
        pd.read_csv(LESSONS).to_excel(xw, sheet_name="Lessons", index=False)
        scan_files().to_excel(xw, sheet_name="Files", index=False)
    print(f"Wrote {target.name}")


def filtered(df, **filters):
    for col, val in filters.items():
        if val:
            df = df[df[col].str.lower() == val.lower()]
    return df


LIST_COLS = ["id", "name", "kind", "area", "status", "owner"]


def cmd_search(term):
    reg = load_registry()
    hay = reg[["id", "name", "kind", "area", "path", "notes"]].agg(" ".join, axis=1).str.lower()
    show(reg[hay.str.contains(term.lower(), regex=False)], LIST_COLS)


# ---------- menu ----------

MENU = """
MOTION HUB
  l  list everything        s  search            o  open (id)       r  run builder (id)
  b  task board             e  events            c  compare plan vs actual
  n  lessons                k  check             x  export to Excel  q  quit
"""


def menu():
    days = (dt.date(2026, 10, 30) - dt.date.today()).days
    if days >= 0:
        print(f"\nDevil's Night · AFTERIMAGE 001 · {days} days to doors")
    while True:
        print(MENU)
        choice = input("> ").strip()
        key, _, arg = choice.partition(" ")
        try:
            if key == "q":
                return
            elif key == "l":
                show(load_registry(), LIST_COLS)
            elif key == "s":
                cmd_search(arg or input("search for: "))
            elif key == "o":
                cmd_open(arg or input("id or path: "))
            elif key == "r":
                cmd_run(arg or input("builder id: "))
            elif key == "b":
                show(load_board())
            elif key == "e":
                show(pd.read_csv(EVENTS))
            elif key == "c":
                cmd_compare(arg or None)
            elif key == "n":
                show(pd.read_csv(LESSONS), ["event_id", "area", "lesson", "next_time"])
            elif key == "k":
                cmd_check()
            elif key == "x":
                cmd_export()
        except SystemExit as e:  # keep the menu open on errors
            print(e)


def main():
    ap = argparse.ArgumentParser(description="MOTION Hub", formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("list"); p.add_argument("--kind"); p.add_argument("--area"); p.add_argument("--status")
    sub.add_parser("search").add_argument("term")
    sub.add_parser("open").add_argument("target")
    p = sub.add_parser("run"); p.add_argument("target"); p.add_argument("--force", action="store_true")
    sub.add_parser("board")
    sub.add_parser("files").add_argument("--ext")
    sub.add_parser("check")
    sub.add_parser("events")
    sub.add_parser("compare").add_argument("event_id", nargs="?")
    sub.add_parser("lessons").add_argument("--area")
    p = sub.add_parser("add-metric")
    for a in ("event_id", "metric", "value"):
        p.add_argument(a)
    p.add_argument("--category", default=""); p.add_argument("--unit", default=""); p.add_argument("--planned", default="")
    p = sub.add_parser("add-lesson")
    for a in ("event_id", "area", "lesson", "next_time"):
        p.add_argument(a)
    sub.add_parser("export")
    a = ap.parse_args()

    if a.cmd is None:
        menu()
    elif a.cmd == "list":
        show(filtered(load_registry(), kind=a.kind, area=a.area, status=a.status), LIST_COLS)
    elif a.cmd == "search":
        cmd_search(a.term)
    elif a.cmd == "open":
        cmd_open(a.target)
    elif a.cmd == "run":
        cmd_run(a.target, a.force)
    elif a.cmd == "board":
        show(load_board())
    elif a.cmd == "files":
        f = scan_files()
        show(f[f["ext"] == a.ext.lower()] if a.ext else f)
    elif a.cmd == "check":
        cmd_check()
    elif a.cmd == "events":
        show(pd.read_csv(EVENTS))
    elif a.cmd == "compare":
        cmd_compare(a.event_id)
    elif a.cmd == "lessons":
        show(filtered(pd.read_csv(LESSONS, dtype=str).fillna(""), area=a.area), ["event_id", "area", "lesson", "next_time"])
    elif a.cmd == "add-metric":
        cmd_add_metric(a.event_id, a.metric, a.value, a.category, a.unit, a.planned)
    elif a.cmd == "add-lesson":
        cmd_add_lesson(a.event_id, a.area, a.lesson, a.next_time)
    elif a.cmd == "export":
        cmd_export()


if __name__ == "__main__":
    main()
