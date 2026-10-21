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
| `DATABASE_URL` | Optional Postgres (Neon). Use the `motion_api` role, or a role that can `SET ROLE motion_api`. Default is SQLite under `MOTION_DATA_DIR`. Ignored when `MOTION_DB_LOCAL=1`. |
| `MOTION_DB_LOCAL` | `1` on the venue laptop. API uses localhost Postgres and does not call Neon. |
| `MOTION_DB_LOCAL_URL` | Optional local URL. Host must be `localhost` or `127.0.0.1`. Default `postgresql+psycopg://motion@127.0.0.1:5432/motion`. |
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

## Night-of localhost (3070 Ti)

The venue laptop has no internet. Set `MOTION_DB_LOCAL=1` before starting the API. That flag ignores `DATABASE_URL`, including a Neon URL left in the environment.

```bash
# once, on the laptop
sudo apt-get install -y postgresql
sudo -u postgres createuser --login motion
sudo -u postgres createdb --owner=motion motion
# The counter uses this login. motion_api is only required for the agent
# write routes (sim_runs, events, zones). Create that role if those run here too.
# pg_hba.conf: trust TCP from this machine only
# host  motion  motion  127.0.0.1/32  trust
sudo systemctl reload postgresql

export MOTION_DB_LOCAL=1
python3 -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8787
```

Jerry posts one JSON object, or JSONL with one object per line. Each frame writes six `flow_counts` rows (`source=counter`, label **estimate**): the five zones plus `total`. Dance is its own zone key here. `total` is the house total Jerry already computed. It is not the sum of the five zones.

```bash
curl -s -D - -X POST http://127.0.0.1:8787/api/data/occupancy \
  -H 'content-type: application/json' \
  -d '{"ts":1700000000,"zones":{"living_room":10,"dance_floor":6,"kitchen_bar":4,"hallway":2,"balcony":1},"total":17}'
curl -s http://127.0.0.1:8787/api/data/counter-health
```

`GET /api/data/counter-health` returns `live` when the newest counter frame is 15 seconds old or newer, `stale` when it is older than 15 seconds through 60 seconds, and `offline` when it is older than 60 seconds or missing. `last_seen` is that frame's `ts`. Sim flow rows do not change this status. A single zone sample (the earlier occupancy body) still returns 200 and does not feed the counter clock.

Agent commits (insert or upsert, no chat relay). On Postgres every write runs as `motion_api` so row-level security applies. `sim_runs` is insert-only: a second post with the same `sim_id` returns 409 and does not change the locked row. Bad bodies return 400.

```bash
curl -s -X POST http://127.0.0.1:8787/api/data/sim_runs \
  -H 'content-type: application/json' \
  -d '{"sim_id":"E001-layout-b","event_id":"E001","model":"room-studio","params_json":{"guests":50},"predicted_peak_curve":[30.42]}'
curl -s -X POST http://127.0.0.1:8787/api/data/events \
  -H 'content-type: application/json' \
  -d '{"event_id":"E001","name":"AFTERIMAGE 001","cap":70}'
curl -s -X POST http://127.0.0.1:8787/api/data/zones \
  -H 'content-type: application/json' \
  -d '{"zone_id":"dance","event_id":"E001","name":"dance","area_sqft":124.5}'
curl -s -X POST http://127.0.0.1:8787/api/data/occupancy_samples \
  -H 'content-type: application/json' \
  -d '{"ts":1700000000,"event_id":"E001","zone_id":"dance","headcount":30,"source":"wyze_living","confidence":0.8}'
curl -s -X POST http://127.0.0.1:8787/api/data/drink_events \
  -H 'content-type: application/json' \
  -d '{"ts":1700000000,"event_id":"E001","drink_id":"paloma","qty":1}'
```

Local SQLite keeps these five tables in `motion_contract.sqlite3` so they do not collide with the muse tables that reuse three of the names. A Postgres `DATABASE_URL` writes to that database.

## Privacy

No guest names, no venue address, no provider keys in responses. Imaging ingest stores path **hashes** + counts/density only.
