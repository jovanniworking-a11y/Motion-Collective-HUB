# T-021 result · Hygiene scan clean on file-push

**Seat:** Cursor (repo + `services/api`). Atlas owns `apps/ops-panel` and Vercel.  
**Branch:** `cursor/file-push-2026-10-21`  
**Status:** hygiene was failing. Scan is clean. Merge to `main` authorized by Jovanni (21 Oct). Nothing spent, sent, or posted.

## What changed

- Live copy no longer treats Glamz as the middle set. Fan site, hub seed, and the board use the 21 Oct lock: iamariology b2b raymixes → Rohan Rali b2b Shubh Samtani (no fee) → HE//THEY · co.b b2b NiiON.
- Source of Truth header points at `orch/context/CURRENT_LOCK.md`. The older body stays as history.
- Removed the scratch studio scripts and the two flyer renderers the archive log already called dead. `test_studio.py` and Room Studio `index.html` stay.
- One e2e assertion in `apps/ops-panel/e2e/smoke.spec.ts` now expects Rohan Rali, matching the assist mock. Atlas owns further panel edits.
- Hygiene skips `.next` build output.

## Verify

`python3 orch/hygiene/scan.py` → `hygiene ok`.

## Open

Codex T-002 and T-009 are not in this tree yet. When they land they merge into `services/api`, not a second backend.
