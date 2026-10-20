# T-018 · Backend reconcile — FastAPI control plane survives

**Seat:** Cursor (Claude Code seat out of usage; Cursor holding orchestrator backend package)  
**Timestamp (UTC):** 2026-10-20T18:38:57Z  
**Branch:** `cursor/backend-reconcile-c926` (from `cursor/claude-pro-bridge`)  
**Status:** draft / local only — nothing spent, sent, posted, or published  
**Scope kept:** no merge to main · no `orch/context/` SoT edits · no `data-platform/` · no Codex T-009 touch

---

## Receipt

| Field | Value | Label |
|---|---|---|
| Input tip `cursor/claude-pro-bridge` | `a905bcdcd7b861fafecbfaaeb2dc65f64c7731ea` | **confirmed** (git) |
| Input tip `cursor/muse-cloud-platform-c430` | `220f6b6b13eb5b859974e76df223548055f777c2` | **confirmed** (git) |
| Input tip `cursor/architecture-review-07eb` | `e7b4fe85dab8027b9bc0cd507dbe767d73d23d23` | **confirmed** (git) |
| Pip verified SHAs (a905bcd / e7b4fe8 / 220f6b6) | match tips above | **confirmed** |
| Merge-ready output commit | *`fc419bb71039333920a547bcd74d7026897a53a0`* | **confirmed** when pushed |
| Tests | `cd services/api && python3 -m pytest -q` → **8 passed** | **confirmed** |
| Cloud run | `bc-963c4235-a94d-5f34-8c0d-dabe6848c926` | **confirmed** |

---

## 1. Stack recommendation (not a ruling — Claude ratifies)

**Pick: keep Python FastAPI as the single BFF/control-plane backend; keep TypeScript on the UI side only (Next `apps/ops-panel` + static `ops/` / Electron shell).** Reason: Room Studio / hub / sim jobs are already Python; keys, metering, and long jobs belong server-side; architecture review @ `e7b4fe8` already steers this split; the Muse data MVP @ `220f6b6` implemented `/api/data/*` in FastAPI, not a second Node API. `SOFTWARE_SPEC.md` is **missing** from the repo (**confirmed** — T-017_plan.md / T-015_result.md); briefs that assumed a TypeScript backend (or Vite-only Night-Of as the only stack) should be reworded so **backend = FastAPI `services/api`**, **UI = TypeScript React** (Next panel + optional Vite/static Night-Of), and any “TS BFF” language is struck. This is a recommendation for Claude/Jovanni — not an SoT edit.

---

## 2. What folded / killed

| Action | Detail | Source |
|---|---|---|
| **Folded** | `/api/data/*` + `platform.py` / `platform_db.py` + SQLAlchemy dep + data tests + `.env.example` into `services/api` | muse @ `220f6b6` |
| **Folded** | `docs/MUSE_DATA_PLATFORM.md` (local-accurate; cloud file claims softened) | muse @ `220f6b6` |
| **Folded** | Root + `services/api` `ARCHITECTURE.md` BFF constraints | arch @ `e7b4fe8` |
| **Killed / superseded** | Parallel data HTTP surface — `services/data/README.md` now points only at `services/api` | this branch |
| **Not folded** | Muse cloud Docker/Fly/Vercel, panel `/data` UI, `orch/context/studio/_t2.py`, `t2-smoke` allowlist | avoid SoT/T-015/T-009 / unrelated mix-in |
| **Not touched** | `data-platform/` (Codex DP-01 lane) · board task IDs · main | per brief |

**One backend survives:** `services/api` on the claude-pro-bridge line.

---

## 3. Merge-ready prep

- Tip before this work: `a905bcd` (**confirmed**)
- README run instructions rewritten for local uvicorn + pytest (no false Docker claims on this branch)
- `python3 -m pytest -q` from `services/api`: **8 passed** (**confirmed**, 2026-10-20)
- BFF constraints retained (keys server-only; no guest PII; no venue address; router one-primary; no hub.py-as-HTTP)

**Merge-ready commit SHA:** `fc419bb71039333920a547bcd74d7026897a53a0` (**confirmed**).

---

## 4. T-013 collision

| Item | Action |
|---|---|
| Architecture review outbox | Renamed → `orch/tasks/outbox/T-013A-arch_architecture_review.md` |
| Board `T-013` (Abraham) | **Untouched** |
| Pre-existing `T-013_result.md` on bridge | Left as control-plane slice receipt (ops-software era); not Abraham; not arch review |

---

## 5. What’s left for DP-01..04 (Codex `data-platform/` lane — **open**)

No `data-platform/` tree on these branches (**confirmed**). Remaining work (**estimate / open**, for Codex — not this seat):

1. **DP-01** — Own `data-platform/` package boundary vs folded `/api/data/*` (avoid a second live HTTP API).  
2. **DP-02** — Postgres/`DATABASE_URL` + durable volume when cloud is OK’d.  
3. **DP-03** — Object storage for images (path hash already; blobs later); still no faces.  
4. **DP-04** — Real compare/metrics vs stub; night-of ground truth; camera hardware still **not ordered** ($67.96 **estimate** from muse doc).

Also **open** on BFF contract naming: `/ops/snapshot`, `/usage/events`, `/agents/runs` vs current `/api/*` paths.

---

## 6. Questions for Jovanni

1. Ratify FastAPI-as-only-backend wording for when `SOFTWARE_SPEC.md` is authored?  
2. OK to leave muse branch cloud/UI extras unmerged until a dedicated fold (panel `/data`, Fly/Docker)?  
3. Prefer aligning route names to architecture contract (`/usage/events`) or keep current `/api/usage`?  
4. Camera remains not ordered until explicit buy OK?

---

## Proposed SoT changes

None (orchestrator / Claude chat only). Optional later pointer to `ARCHITECTURE.md` + T-013A-arch once ratified.

## Files produced

- `services/api/app/platform.py`, `platform_db.py`, updated `main.py` / `config.py` / `requirements.txt` / `tests/test_api.py` / `.env.example` / `README.md` / `ARCHITECTURE.md`
- `services/data/README.md` (supersede pointer)
- `docs/MUSE_DATA_PLATFORM.md`
- `ARCHITECTURE.md`, `AGENTS.md` (T-013A-arch constraints)
- `orch/tasks/outbox/T-013A-arch_architecture_review.md`
- `orch/tasks/outbox/T-018_backend_reconcile.md` (this file)
