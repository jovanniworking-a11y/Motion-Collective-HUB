# services/data — Muse / sim / imaging store

MVP models and SQLite/Postgres access live in the FastAPI app for one deployable unit:

- `services/api/app/platform_db.py` — SQLAlchemy models (`sim_runs`, `imaging_observations`, `drink_events`, `flow_counts`)
- `services/api/app/platform.py` — ingest + compare stubs
- Endpoints under `/api/data/*` (see `docs/MUSE_DATA_PLATFORM.md`)

Set `DATABASE_URL` for Postgres when the cloud stack is live. Default is SQLite under `MOTION_DATA_DIR`.

**Privacy:** counts, density estimates, and image path hashes only. No face recognition, no guest PII, no venue address.
