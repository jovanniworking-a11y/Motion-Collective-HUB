# T-018 result · FastAPI control plane reconciled and merged to main

**Seat:** Cursor (Claude Code seat out of usage; Cursor holding the orchestrator backend package)  
**Timestamp (UTC):** 2026-10-20T19:42:33Z  
**Branch:** `cursor/backend-merge-34bf` (from `cursor/backend-reconcile-c926`, itself from `cursor/claude-pro-bridge`)  
**Status:** merge to `main` **authorized** by Jovanni (20 Oct, “let Cursor merge”). Nothing spent, sent, posted, or published.  
**Not touched:** `orch/context/` Source of Truth · board numbering · Codex `data-platform/` · T-009 sims

---

## 1. Stack recommendation (not a ruling — Claude ratifies, Jovanni can overrule)

**Pick: Python FastAPI in `services/api` is the only control-plane backend; TypeScript stays on the UI (Next.js `apps/ops-panel`, Electron shell, static Night-Of `ops/`).** Room Studio, `hub.py`, and sim jobs are already Python, and both the architecture review (`e7b4fe8`) and the Muse data MVP (`220f6b6`) already put keys, metering, jobs, and `/api/data/*` behind FastAPI rather than a second Node server. `SOFTWARE_SPEC.md` is **missing** from the repo (**confirmed** — `orch/tasks/outbox/T-017_plan.md` on `cursor/t015-t2-rebuild`). The brief that spec would have carried assumes a **TypeScript + React Vite PWA** for Night-Of (§4, cap **70 confirmed** in that plan note) and T-012 assumes **TypeScript + Next.js** for the panel UI. If this pick is adopted, spec wording should say **backend = FastAPI `services/api`** (including Muse `/api/data/*`), **panel UI = TypeScript React (Next.js)**, **Night-Of phones = the existing static PWA unless a later decision switches it to Vite**, and any line that calls the BFF itself TypeScript should be struck. This file does not edit the Source of Truth.

---

## 2. What was folded / killed

| Action | Detail | Label |
|---|---|---|
| Folded | `/api/data/*` plus `platform.py`, `platform_db.py`, SQLAlchemy, data tests, `.env.example` into `services/api` | **confirmed** (from muse @ `220f6b6`) |
| Folded | `docs/MUSE_DATA_PLATFORM.md` | **confirmed** |
| Folded | Root `ARCHITECTURE.md`, `services/api/ARCHITECTURE.md`, BFF block in `AGENTS.md` | **confirmed** (from arch @ `e7b4fe8`, renamed T-013A-arch) |
| Superseded | Parallel data HTTP service. `services/data/README.md` is a pointer only: one backend, `services/api` | **confirmed** |
| Left on muse, not mixed in | Docker/Fly/Vercel hosting, panel `/data` page, studio `_t2.py`, cloud worker extras | **confirmed** (not on this branch) |
| Left for Codex | `data-platform/` does not exist on this branch | **confirmed** absent |

**One backend survives:** `services/api`.

BFF constraints kept: responses carry pass numbers only (guest **name** meta stripped), no venue address, no provider keys in responses. Live check on uvicorn `:8787`: observation meta `{"name","address","pass":7}` stored as `{"pass":7}` plus an image path hash; `/api/data/health` reports scheme `sqlite` only (**confirmed**, this run).

---

## 3. Merge

| Field | Value | Label |
|---|---|---|
| Input `cursor/claude-pro-bridge` | `a905bcdcd7b861fafecbfaaeb2dc65f64c7731ea` | **confirmed** |
| Input `cursor/architecture-review-07eb` | `e7b4fe85dab8027b9bc0cd507dbe767d73d23d23` | **confirmed** |
| Input `cursor/muse-cloud-platform-c430` | `220f6b6b13eb5b859974e76df223548055f777c2` | **confirmed** |
| Services/api fold commit | `fc419bb71039333920a547bcd74d7026897a53a0` | **confirmed** |
| Branch tip before this gist | `9799bb60956831396046158a6050cf7012bc1223` | **confirmed** |
| Source commit merged to `main` | stamped in the follow-up line below after `git merge` | **open** until that commit lands |
| Merge commit on `main` | stamped in the follow-up line below | **open** until that commit lands |
| Tests | `cd services/api && python3 -m pytest -q` → **8 passed**, 1 warning | **confirmed** (2026-10-20) |
| `main` before this merge | did not exist on `origin` | **confirmed** (`git ls-remote`) |
| Default branch before this merge | `claude/motion-files-consolidated-dx17w2` @ `a397cbc` | **confirmed** |

`main` is created from that default branch and this package is merged with `--no-ff`, so the merge commit is a real merge, not a fast-forward.

README run path (local): `cd services/api && pip install -r requirements.txt && uvicorn app.main:app --host 127.0.0.1 --port 8787`. Health smoke returned `motion-control-plane` `0.1.0` `draft_only: true` (**confirmed**).

---

## 4. T-013 collision

| Item | Action |
|---|---|
| Architecture review file | Renamed to `orch/tasks/outbox/T-013A-arch_architecture_review.md` |
| `T-013_architecture_review.md` | Removed from this line (rename, not a second copy) |
| Board `T-013` (Abraham’s brief) | **Untouched** |
| Older `T-013_result.md` on the bridge | Left in place; it is the control-plane slice receipt, not the architecture review and not Abraham’s brief |

---

## 5. What’s left for DP-01..04

Ticket text for DP-02, DP-03, and DP-04 is **not in this repo** (**open**). Do not treat the rows below as confirmed scopes.

| Item | Left | Label |
|---|---|---|
| DP-01 | Codex’s new `data-platform/` folder. Absent here (**confirmed**). This seat did not create it. It should not become a second live HTTP API next to `/api/data/*`. | **open** (Codex lane) |
| DP-02..04 | Definitions unknown here. Muse doc still lists later work that is **not** numbered as those tickets: Postgres via `DATABASE_URL` when cloud is OK’d; object storage for images (hashes only today); compare metrics are a stub (`label: estimate`). | **open** |
| Camera | Muse doc: not ordered. Price **$67.96** | **estimate** (doc), buy **not authorized** |

Also **open** on the BFF contract: architecture names `/ops/snapshot` and `/usage/events`; the running API uses `/api/studio`, `/api/usage`, `/api/agents`, `/api/sims`, `/api/data/*`.

---

## 6. Questions for Jovanni

1. Ratify FastAPI as the only backend when `SOFTWARE_SPEC.md` is written, with TypeScript limited to the UI?
2. Night-Of stays the static `ops/` PWA, or must it become the Vite app the missing spec’s §4 described?
3. Keep current `/api/*` paths, or rename toward the architecture contract (`/usage/events`, `/ops/snapshot`)?
4. Leave muse-only extras (panel `/data`, Fly/Docker) unmerged until a separate OK?

---

## Proposed SoT changes

None.

## Files produced (this seat’s merge record)

- This gist: `orch/tasks/outbox/T-018_result.md`
- Package already on the branch from the fold: `services/api/**`, `services/data/README.md`, `docs/MUSE_DATA_PLATFORM.md`, `ARCHITECTURE.md`, `AGENTS.md`, `orch/tasks/outbox/T-013A-arch_architecture_review.md`, `orch/tasks/outbox/T-018_backend_reconcile.md`

## How verified

- `python3 -m pytest -q` in `services/api`: **8 passed** (**confirmed**)
- uvicorn `127.0.0.1:8787` `/health` and `/api/data/health`, plus one observation write that kept pass `7` and stripped name/address (**confirmed**)
