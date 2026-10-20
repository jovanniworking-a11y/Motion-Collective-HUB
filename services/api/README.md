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

## Privacy

No guest names, no venue address, no provider keys in responses. Imaging ingest stores path **hashes** + counts/density only.
