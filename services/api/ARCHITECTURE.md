# services/api — BFF constraints

Canonical product standard: **[`/ARCHITECTURE.md`](../../ARCHITECTURE.md)** (T-013).

## This package
Python **FastAPI** backend-for-frontend for MOTION Ops.

**MVP endpoints (contract for UI agents):**
- `GET /health`
- `GET /ops/snapshot` — night/capacity/ROS/budget seed (no PII, no address)
- `POST /usage/events` — append metering row
- `GET /usage/events` — list recent (for live view)
- `GET|POST /agents/runs` — stub run status (queued / running / done)
- Router config: area → model (file or table); **one** primary model per action

**Storage:** SQLite under `data/` (git-ignore DB files). Job queue for Studio sims later — never block request handlers on long sims.

**Forbidden:** provider API keys in responses; guest names; venue address; calling every model on every request; turning `hub.py` into this server (import/share libs later if needed).
