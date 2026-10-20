# T-015 — Studio helper `_t2.py` rebuild (Cursor) + prior cloud hosting note

## What I did
1. **Prior (ops-cloud):** cloud hosting infra/docs (Vercel + Fly) — see tip `63884e8` / parent outbox history.
2. **This run (muse-cloud-platform):** rebuilt missing `orch/context/studio/_t2.py` so `_chk*` / `_night2` / `_all2` can `exec()` the prelude again. Portable paths, SwiftShader ARGS, cached-Chromium launch patch, `python3 _t2.py smoke`.

## Files produced
- `orch/context/studio/_t2.py` — ARGS, `boot(pg)`, `prepare_test_html`, smoke CLI
- `services/api/app/sims.py` — allowlist kind `t2-smoke`
- `hub/registry.csv` — `studio-sims` status → ready
- `orch/tasks/outbox/T-015_result.md` (this file)

## How verified
- `cd orch/context/studio && python3 _t2.py smoke` → `studio.ok=true`, items=10, hasDbg=true, errors=[], label=confirmed
- Prelude exec (same pattern as `_night2.py`) + `boot(pg)` → ok
- Chromium: `/home/ubuntu/.cache/ms-playwright/chromium-1169/chrome-linux/chrome` via executable_path patch (Playwright package wanted newer browser; no paid download)
- Screenshot generated under `shots/t2_smoke.png` (gitignored)

## Proposed SoT changes
None.

## Questions for Jovanni
1. OK to run heavier `_night2` / `_all2` on a PC with more time (T-009 drinks)?
2. Camera remains **not ordered** until explicit buy OK.

## Branch
`cursor/muse-cloud-platform-c430` (from `cursor/ops-cloud`)
