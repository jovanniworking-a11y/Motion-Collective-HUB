# services/api — BFF constraints

Canonical product standard: **[`/ARCHITECTURE.md`](../../ARCHITECTURE.md)** (**T-013A-arch**).

## This package
Python **FastAPI** backend-for-frontend for MOTION Ops. **One backend** — Muse `/api/data/*` lives here (not a second service under `services/data/`).

**MVP endpoints (contract for UI agents — keep semantics; paths may be `/api/*`-prefixed as implemented):**
- `GET /health`
- Ops / night seed read (no PII, no address) — implemented today via studio/layout + panel seed, not a separate `/ops/snapshot` yet (**open**)
- Usage metering — implemented as `GET /api/usage` (SQLite); append-style `/usage/events` shape still **open** to align naming
- Agent runs — implemented as `/api/agents`, `/api/agents/{id}/chat`, sim jobs under `/api/sims/*`
- Router: `GET /api/routing`, `POST /api/routing/resolve` — **one** primary model per action
- Data MVP: `/api/data/*` (health, sims persist, observations, drinks, flow, compare). Panel route `/data` is the only UI for this contract.

**Storage:** SQLite under `data/` / `MOTION_DATA_DIR` (git-ignore DB files). Job queue for Studio sims — never block request handlers on long sims (`smoke-stub` default).

**Forbidden:** provider API keys in responses; guest names; venue address; calling every model on every request; turning `hub.py` into this server (import/share libs later if needed).
