# MOTION Collective HUB

One place for everything MOTION builds and learns. Event #1: **Devil's Night · AFTERIMAGE 001 · Fri 10.30.2026**.

## MOTION Ops control plane (primary crew software)

Next.js UI + Python FastAPI. **Cloud website is the primary run path** (clickable URL). Electron desktop is optional.

### Cloud (recommended)

See **[`docs/CLOUD_HOSTING.md`](docs/CLOUD_HOSTING.md)** — Vercel panel + Fly/Railway API, free-tier notes, Pro Prompt Bridge ($0 API).

### Local

```bash
# Backend
pip install -r services/api/requirements.txt
python3 -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8787

# Web UI
cd apps/ops-panel && npm install && npm run dev   # → http://localhost:3000

# Optional desktop shell (or open the cloud panel URL in a browser)
cd desktop && npm install && npm run desktop
# Cloud panel in Electron: MOTION_OPS_URL=https://YOUR-PANEL.vercel.app npm run desktop
```

Tests: `cd services/api && python3 -m pytest -q` · `cd apps/ops-panel && npm run test`  
Routing: `services/api/MODEL_ROUTING.md`. Draft only — never publish.

## Web hub (static / Claude artifact)
**https://claude.ai/artifact/6nZX6PmhuCXFezNSu6gkfM** is private to the owner and needs a claude.ai sign-in.
Source: `web/index.html`. Seed: `web/seed.json`. Room Studio: https://claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV.

## Python hub (this repo)
```bash
pip install -r requirements.txt
python hub.py            # menu: list, search, open, run, board, compare, lessons, export
```

| Command | What it does |
|---|---|
| `python hub.py list --area money` | Every app, builder, workbook and doc, as a pandas table |
| `python hub.py open room-studio` | Opens it (browser, Excel, PowerPoint, image viewer…) |
| `python hub.py run drinks-build` | Runs a builder; output goes to `hub_out/<id>/` |
| `python hub.py board` | Task board (`orch/tasks/BOARD.md`) as a table |
| `python hub.py check` | What's missing, what can't run yet, what isn't catalogued |
| `python hub.py compare E001` | Planned vs actual for every tracked number |
| `python hub.py export` | `hub_catalog.xlsx` with every table on its own sheet |

## Layout
```
hub.py              the hub
hub/registry.csv    catalog of all MOTION software + files (edit in Excel to add things)
data/               what we learn from events
  events.csv        one row per event
  metrics.csv       planned vs actual numbers, labelled confirmed / estimate / open
  lessons.csv       what happened -> what we do next time
  DEBRIEF_TEMPLATE.md   fill within 48 h of every event
orch/               agent orchestration kit (briefs, task board, project context)
apps/ops-panel/     Next.js control-plane UI (ops, agents, usage, activity, Muse)
services/api/       Python FastAPI backend (chat proxy, metering, sims)
desktop/            optional Electron shell (cloud users use the website)
docs/               CLOUD_HOSTING.md and related
ops/                legacy static Night-Of HTML (still works offline)
web/                the web hub (claude.ai artifact) source + seed data
site/               fan site (static)
legacy/ch31-planner the 21 Sep CH31 planner, kept for reference (runs only on ChatGPT Sites)
```

## Getting better every event
1. **Before:** put the plan into `data/metrics.csv` (`planned` column).
2. **On the night:** count the numbers in the debrief template (door count, midnight peak, drinks left, longest line).
3. **Within 48 h:** `python hub.py add-metric E001 guests_total 52` for each number, and
   `python hub.py add-lesson E001 drinks "Ice ran out at 00:30" "Buy 200 lb"`.
4. **Next event:** add a row to `events.csv` (E002…), copy the metric names, then run `compare` to see every event side by side.

## Rules
- The venue address never goes in this repo.
- Guest data stays local: `orch/context/assets/guest_list/` and doc 11 are git-ignored.
- API keys go in `.env` (git-ignored), never in code.
