# T-017 plan pointer — Night-Of Ops (plan only; no Sprint 1 code)

**Seat:** cursor · **Timestamp:** 2026-10-20T16:23:51Z · **After:** T-015 success on `cursor/t015-t2-rebuild`.

## Brief asks
- Night-Of Ops per `SOFTWARE_SPEC.md` §4 if present: TypeScript + React Vite PWA, branch `cursor/ops-panel`, state via `app/state.json`, Cap **70 confirmed** (20 Oct).
- Do **not** start Sprint 1 until T-015 done — T-015 met; this file is the planning pointer (no scaffold started).

## Repo fact check
- `SOFTWARE_SPEC.md`: **not found** in workspace root, `orch/`, or listed ops remote branches (`cursor/ops-software-*`, `cursor/night-of-ops-6609`, `cursor/ops-cloud`, `cursor/ops-desktop-e7a0`). Label: **UNKNOWN / missing**.
- Earlier cursor work: untracked/local `apps/ops-panel` appears to be **Next.js** (`.next/` present), not Vite — **conflict** with brief’s Vite requirement if SOFTWARE_SPEC mandates Vite.
- Cap 70: brief **confirmed** 20 Oct; `orch/AGENTS.md` still says living-room working cap ~50 / under review — Claude/SoT reconcile.

## Proposed next (when Jovanni/Claude OK)
1. Locate or author `SOFTWARE_SPEC.md` §4 (Claude chat / Pip).
2. If Vite required: new branch `cursor/ops-panel` scaffold (not Next.js reuse) + `app/state.json`.
3. If Next.js already intentional: DECISION from Jovanni before more coding.
4. Defaults: pass NUMBERS only; no venue address; draft-only; Cap 70 as confirmed default until SoT says otherwise.

## Blockers
- Missing `SOFTWARE_SPEC.md` — cannot implement §4 faithfully without it.
