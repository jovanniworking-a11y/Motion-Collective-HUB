# services/data — superseded as a separate backend

**One backend survives:** `services/api` on the `cursor/claude-pro-bridge` line (this monorepo path).

Do **not** grow a second HTTP service here. Muse / sim / imaging MVP models and `/api/data/*` live inside FastAPI:

- `services/api/app/platform_db.py` — SQLAlchemy models (`sim_runs`, `imaging_observations`, `drink_events`, `flow_counts`)
- `services/api/app/platform.py` — ingest + compare stubs
- Endpoints under `/api/data/*` (see `docs/MUSE_DATA_PLATFORM.md`)

The Muse data MVP that landed on `cursor/muse-cloud-platform-c430` @ `220f6b6` is **folded** into `services/api`; treat that branch’s data surface as superseded by this package.

Set `DATABASE_URL` for Postgres when the cloud stack is live (Jovanni OK). Default is SQLite under `MOTION_DATA_DIR`.

**Privacy:** counts, density estimates, and image path hashes only. No face recognition, no guest PII, no venue address.
