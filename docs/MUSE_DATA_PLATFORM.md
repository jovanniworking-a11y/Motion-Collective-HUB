# Muse data platform — 24/7 cloud topology (MVP)

Draft only. Never spend / send / post / publish without Jovanni’s OK. **Camera (+$67.96 estimate from muse brief @ `220f6b6`) is not ordered** — awaits explicit human buy order.

**Canonical home:** `/api/data/*` inside `services/api` (Cursor’s seat until Claude returns). Codex T-002 and T-009 fold into this package when they land. `services/data/` is a pointer only (no second HTTP server). Cloud deploy files (`fly.toml`, Docker) may live on other branches — local run does not require them.

## Vision (active scaffold)

Train and store **sim + night-of observation** data so Muse can compare Room Studio runs against real imaging features (crew counts / density placeholders). SQL now; object storage for images later.

```
Browser (ops-panel /data + /muse)
        │  NEXT_PUBLIC_API_URL
        ▼
FastAPI (services/api) ── SQLAlchemy ── SQLite (MVP) / Postgres (DATABASE_URL)
        │                      │
        ├─ /api/sims/*         ├─ sim_runs
        ├─ /api/data/*         ├─ imaging_observations
        └─ worker thread       ├─ drink_events
           (_t2 / _all2 jobs)  └─ flow_counts

Later: object storage (R2/S3) for image blobs · always store path hash + features, never faces
```

## 24/7 cloud pieces

| Piece | Now | When live |
|-------|-----|-----------|
| API | `services/api` (uvicorn :8787) | Fly/Railway URL (**open** — deploy needs Jovanni login; configs may be on muse branch) |
| Panel | `apps/ops-panel` | Vercel hobby (**open**) |
| Worker | in-process sim threads (`MOTION_SIM_EXECUTE`) | same image or separate worker process |
| SQL | SQLite under `MOTION_DATA_DIR` | Postgres via `DATABASE_URL` |
| Images | path hash only | object storage; features/counts in SQL |
| Models | Pro Prompt Bridge default ($0 API) | Groq cheap mechanical · Gemini/Claude reasoning via bridge or keyed API |

See also: `apps/ops-panel/CLAUDE_PRO_BRIDGE.md`, `services/api/MODEL_ROUTING.md`. Cloud hosting doc may appear when that lane is folded (not required for local API).

## Schema (MVP)

| Table | Purpose |
|-------|---------|
| `sim_runs` | Kind, job id, params, result JSON, optional score, label |
| `imaging_observations` | Zone, crew_count, density_est, image_path_hash, meta (stripped), label |
| `drink_events` | Station, drink_type, quantity, source |
| `flow_counts` | Zone, count, window_sec, source |

## API

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/data/health` | Creates tables; reports DB scheme |
| GET | `/api/data/sims` | List persisted sim runs |
| POST | `/api/data/sims/run` | Queue allowlisted Muse job + persist row |
| POST | `/api/data/sims/jobs/{id}/persist` | Snapshot finished job into `sim_runs` |
| POST | `/api/data/observations` | Ingest count/density + optional path → hash |
| GET | `/api/data/observations` | List observations |
| POST | `/api/data/drinks` | Drink event |
| POST | `/api/data/flow` | Flow count |
| POST | `/api/data/occupancy` | Counter frame `{ts, zones, total}` → `flow_counts` (201) |
| GET | `/api/data/counter-health` | `live` ≤15s, `stale` >15s through 60s, `offline` >60s |
| GET/POST | `/api/data/compare` | Stub metrics (all `estimate`) |

## Privacy

- **No face recognition** in MVP. No embeddings, no guest names, no venue address.
- Imaging ingest accepts metadata + optional `image_path` and stores **SHA-256 hash only**.
- Banned meta keys stripped: address, guest, phone, email, face, embedding, name, …

## Model router (anti-hallucination)

| Work | Prefer |
|------|--------|
| Mechanical / JSON / routing | Groq (when `GROQ_API_KEY` present) or local stubs |
| Reasoning / SoT decisions | Claude via **Pro Prompt Bridge** or API if keyed |
| Video / sheet audit | Gemini (when keyed) |
| Always | Source pointers · label numbers · unknown OK · receipts in outbox |

## Local smoke

```bash
pip install -r services/api/requirements.txt
python scripts/check_links.py
python3 -m uvicorn app.main:app --app-dir services/api --port 8787
# panel Data page: apps/ops-panel → /data
```

`orch/context/studio/_t2.py` is **not on this branch** (**open** — it lives on `cursor/muse-cloud-platform-c430`). Do not treat that smoke command as runnable here.

## Status this run

Configs + scaffold **RUNNABLE locally**. Live 24/7 URLs need Jovanni Fly/Vercel login. API keys absent in this cloud agent env (see `orch/tasks/outbox/T-016_connections_audit.md`).
