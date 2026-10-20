# MOTION Control Plane API

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
# or from repo root:
python3 -m uvicorn app.main:app --app-dir services/api --port 8787
```

Tests: `python3 -m pytest -q`  
Env: see `.env.example`. `ANTHROPIC_API_KEY` optional (live chat — billed API; Claude.ai Pro ≠ API). Without it, chat stays mock; ops-panel Pro bridge opens claude.ai for $0 API. `MOTION_SIM_EXECUTE=1` (real studio scripts). `DATABASE_URL` optional (Postgres); default SQLite muse platform DB under `MOTION_DATA_DIR`.  
Routing: `MODEL_ROUTING.md`. Data/compare: `/api/data/*` · `docs/MUSE_DATA_PLATFORM.md`.

## Cloud

Docker + Fly/Railway configs live with the monorepo:

- Dockerfile: `services/api/Dockerfile` (build from **repo root**)
- Fly: root `fly.toml`
- Railway: `services/api/railway.toml`
- Full guide: [`docs/CLOUD_HOSTING.md`](../../docs/CLOUD_HOSTING.md)

`MOTION_DATA_DIR=/tmp/motion-api-data` is fine for MVP (SQLite resets on redeploy without a volume).
