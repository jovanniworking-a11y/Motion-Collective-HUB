# MOTION Control Plane API

Single surviving backend for MOTION Ops (BFF + Muse `/api/data/*`). Draft / local only.

**Seat:** Cursor owns this package until Claude returns. Codex T-002 and T-009 merge in here when they land. Do not add a second HTTP service.

## Run (local)

```bash
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
```

From repo root:

```bash
python3 -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8787
```

## Tests

```bash
python scripts/check_links.py
cd services/api && python3 -m pytest -q
```

## Env

See `.env.example` (no real secrets in git).

| Var | Role |
|---|---|
| `ANTHROPIC_API_KEY` | Optional live chat (billed API; Claude.ai Pro ≠ API). Omit → mock chat; ops-panel Pro bridge for $0 API. |
| `MOTION_SIM_EXECUTE=1` | Run real studio scripts (default off; CI uses `smoke-stub`). |
| `MOTION_DATA_DIR` | Writable dir for usage SQLite + layout/chat JSON + muse platform SQLite (default `services/api/data`). |
| `DATABASE_URL` | Optional Postgres for muse tables; default SQLite under `MOTION_DATA_DIR`. Ignored when `MOTION_DB_LOCAL=1`. |
| `MOTION_DB_LOCAL` | `1` on the venue laptop. API uses localhost Postgres and does not call Neon. |
| `MOTION_DB_LOCAL_URL` | Optional local URL. Host must be localhost or `127.0.0.1`. Default `postgresql+psycopg://motion@127.0.0.1:5432/motion`. |
| `MOTION_API_CORS` | Comma-separated panel origins (default localhost:3000). |

Routing: `MODEL_ROUTING.md`. BFF constraints: `ARCHITECTURE.md` (package) + root `ARCHITECTURE.md`. Data/compare: `/api/data/*` · `docs/MUSE_DATA_PLATFORM.md`.

## Privacy

No guest names, no venue address, no provider keys in responses. Imaging ingest stores path **hashes** + counts/density only.

## Night-of localhost

The venue laptop has no internet. Set `MOTION_DB_LOCAL=1` before starting the API. That flag ignores `DATABASE_URL`, including a Neon URL left in the environment.

```bash
export MOTION_DB_LOCAL=1
curl -s -X POST http://127.0.0.1:8787/api/data/occupancy \
  -H 'content-type: application/json' \
  -d '{"ts":1700000000,"zones":{"living_room":4,"dance_floor":3,"kitchen_bar":2,"hallway":1,"balcony":0},"total":7}'
curl -s http://127.0.0.1:8787/api/data/counter-health
```

`POST /api/data/occupancy` returns 201 and writes six `flow_counts` rows (`source=counter`, label `estimate`): the five zones plus `total` as sent. `GET /api/data/counter-health` returns `live` when the newest counter frame is 15 seconds old or newer, `stale` when it is older than 15 seconds through 60 seconds, and `offline` when it is older than 60 seconds or missing. `last_seen` is that frame's `ts`. Sim flow rows do not change this status.

`POST /api/data/sim_runs` inserts one locked prediction (`sim_id`, `event_id`, `model`, `params_json`, `predicted_peak_curve`, optional `locked_at`) and returns `{"id": ...}`. A second post with the same `sim_id` returns 409 and leaves the first row. The app has no update or delete for that table. This process does not invent a sim row. Codex posts the real curve. On Postgres, when `public.sim_runs` is the muse list (`kind`, `created_at`), the locked row is stored in `motion_contract.sim_runs` so the two shapes do not collide. Writes use `SET LOCAL ROLE motion_api` when that role exists.
