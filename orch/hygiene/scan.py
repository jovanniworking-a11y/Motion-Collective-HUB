#!/usr/bin/env python3
"""Flag lineup/money rot and dead scratch. Does not delete files.

Exit 1 when an active path contradicts orch/context/CURRENT_LOCK.md
or when known-dead scratch is still in the tree.
Protected code (apps logic, services, desktop, hub.py, studio index) is
never listed as a delete candidate.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ACTIVE = (
    "apps",
    "services",
    "desktop",
    "site",
    "web",
    "ops",
    "AGENTS.md",
    "README.md",
    "CLAUDE.md",
    "hub/registry.csv",
    "orch/AGENTS.md",
    "orch/GEMINI.md",
    "orch/CLAUDE.md",
    "orch/workers",
    "orch/tasks/BOARD.md",
    "orch/context/CURRENT_LOCK.md",
)

SKIP_PARTS = (
    "/orch/archive/",
    "/orch/tasks/outbox/",
    "/orch/tasks/inbox/",
    "/orch/context/project_docs/",
    "/orch/context/drive/",
    "/orch/context/assets/LESSONS.md",
    "/orch/hygiene/",
    "/legacy/",
    "/node_modules/",
    "/.next/",
)

ALLOW = ("cancel", "archiv", "do not", "no copy", "removed", "not on the lineup", "her name")
RETIRED = ("$391.42", "$171.88", "$58.58")
DEAD = (
    "orch/context/studio/_chk.py",
    "orch/context/studio/_chk2.py",
    "orch/context/studio/_chk3.py",
    "orch/context/studio/_chk4.py",
    "orch/context/studio/_chk5.py",
    "orch/context/studio/_chk6.py",
    "orch/context/studio/_err.py",
    "orch/context/studio/_night2.py",
    "orch/context/studio/_all2.py",
    "orch/context/studio/_report_b1.json",
    "orch/context/studio/_report_b2.json",
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def active_files():
    for item in ACTIVE:
        p = ROOT / item
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix not in {".png", ".jpg", ".webp", ".xlsx", ".pptx", ".pdf", ".lock"}:
                    yield f


def skipped(path: str) -> bool:
    s = "/" + path
    return any(part in s for part in SKIP_PARTS)


def main() -> int:
    problems = []
    for path in active_files():
        r = rel(path)
        if skipped(r):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if "glamz" in low and not any(tok in low for tok in ALLOW):
                if "not.tomatch" in low.replace(" ", ""):
                    continue
                problems.append(f"GLAMZ {r}:{i}")
            for money in RETIRED:
                if money in line and not any(tok in low for tok in ("retir", "do not", "history")):
                    problems.append(f"RETIRED {money} {r}:{i}")
    sot = ROOT / "orch/context/SOURCE_OF_TRUTH_latest.md"
    if sot.exists():
        head = "\n".join(sot.read_text(encoding="utf-8", errors="replace").splitlines()[:12])
        if "CURRENT LOCK" not in head:
            problems.append("SOT missing CURRENT LOCK in the first 12 lines")
    for dead in DEAD:
        if (ROOT / dead).exists():
            problems.append(f"DEAD {dead}")
    flyer = ROOT / "orch/context/assets/flyer_v4_glamz"
    if flyer.is_dir():
        for f in flyer.glob("*.py"):
            problems.append(f"DEAD {rel(f)}")
    if problems:
        print(f"hygiene FAIL {len(problems)}")
        print("\n".join(problems[:80]))
        return 1
    print("hygiene ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
