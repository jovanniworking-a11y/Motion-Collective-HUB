# MOTION Control Plane API

Single surviving backend for MOTION Ops (BFF + Muse `/api/data/*`). Draft / local only.

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
cd services/api
python3 -m pytest -q
```

## Env

See `.env.example` (no real secrets in git).

| Var | Role |
|---|---|
| `ANTHROPIC_API_KEY` | Optional live chat (billed API; Claude.ai Pro ≠ API). Omit → mock chat; ops-panel Pro bridge for $0 API. |
| `MOTION_SIM_EXECUTE=1` | Run real studio scripts (default off; CI uses `smoke-stub`). |
| `MOTION_DATA_DIR` | Writable dir for usage SQLite + layout/chat JSON + muse platform SQLite (default `services/api/data`). |
| `DATABASE_URL` | Optional Postgres for muse tables; default SQLite under `MOTION_DATA_DIR`. |
| `MOTION_API_CORS` | Comma-separated panel origins (default localhost:3000). |

Routing: `MODEL_ROUTING.md`. BFF constraints: `ARCHITECTURE.md` (package) + root `ARCHITECTURE.md`. Data/compare: `/api/data/*` · `docs/MUSE_DATA_PLATFORM.md`.

Occupancy (counts only, local SQLite or `DATABASE_URL`):

```bash
# one zone row
curl -s -X POST http://127.0.0.1:8787/api/data/occupancy \
  -H 'content-type: application/json' \
  -d '{"captured_at":1700000000,"zone":"dance","count":12,"confidence":0.8,"count_quality":"ok","camera_id":"wyze_living","sample_kind":"primary"}'
# boxes in, counts out — boxes are not stored
curl -s http://127.0.0.1:8787/api/data/occupancy/board
```

Do not add Ultralytics or camera weights to this repo. The count endpoint accepts person boxes already measured on the crew laptop.

## Privacy

No guest names, no venue address, no provider keys in responses. Imaging ingest stores path **hashes** + counts/density only.
