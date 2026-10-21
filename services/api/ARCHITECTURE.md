# services/api — BFF constraints

Canonical product standard: **[`/ARCHITECTURE.md`](../../ARCHITECTURE.md)** (**T-013A-arch**).

## This package
Python **FastAPI** backend-for-frontend for MOTION Ops. **One backend** — Muse `/api/data/*` lives here (not a second service under `services/data/`).

**Seat (21 Oct, until Claude returns):** Cursor owns `services/api`, including the data-platform routes. Codex still runs T-002 (budget workbook) and T-009 (drink sims). When those land, they merge into this package. Atlas owns `apps/ops-panel` and Vercel.

**MVP endpoints (contract for UI agents — keep semantics; paths may be `/api/*`-prefixed as implemented):**
- `GET /health`
- Ops / night seed read (no PII, no address) — implemented today via studio/layout + panel seed, not a separate `/ops/snapshot` yet (**open**)
- Usage metering — implemented as `GET /api/usage` (SQLite); append-style `/usage/events` shape still **open** to align naming
- Agent runs — implemented as `/api/agents`, `/api/agents/{id}/chat`, sim jobs under `/api/sims/*`
- Router: `GET /api/routing`, `POST /api/routing/resolve` — **one** primary model per action
- Data MVP: `/api/data/*` (health, sims persist, observations, drinks, flow, compare). Panel route `/data` is the only UI for this contract.
- Occupancy: `/api/data/occupancy` stores one zone sample, or Jerry's counter frame (`ts`, `zones`, `total`) into `flow_counts` (201). `GET /api/data/counter-health` is live / stale / offline from the newest counter frame. `MOTION_DB_LOCAL=1` points the API at localhost Postgres and ignores Neon.
- Agent writes: `POST /api/data/sim_runs` (insert-only, 409 when `sim_id` exists), `POST /api/data/zones`, `POST /api/data/events`, `POST /api/data/occupancy_samples`, `POST /api/data/drink_events`. Postgres sessions use `SET LOCAL ROLE motion_api`. Bad input returns 400. Each success body is `{"id": ...}`.

**Storage:** SQLite under `data/` / `MOTION_DATA_DIR` (git-ignore DB files). Job queue for Studio sims — never block request handlers on long sims (`smoke-stub` default).

**Forbidden:** provider API keys in responses; guest names; venue address; calling every model on every request; turning `hub.py` into this server (import/share libs later if needed).
