# MOTION Control Plane API

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
# or from repo root:
python3 -m uvicorn app.main:app --app-dir services/api --port 8787
```

Tests: `python3 -m pytest -q`  
Env: `ANTHROPIC_API_KEY` (live chat), `MOTION_SIM_EXECUTE=1` (real studio scripts).  
Routing: `MODEL_ROUTING.md`.
