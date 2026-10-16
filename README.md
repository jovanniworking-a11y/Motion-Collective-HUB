# MOTION Collective HUB

One place for everything MOTION builds and learns. Event #1: **Devil's Night · AFTERIMAGE 001 · Fri 10.30.2026**.

## Web hub (any computer)
**https://claude.ai/artifact/6nZX6PmhuCXFezNSu6gkfM** is private to the owner and needs a claude.ai sign-in.
Tabs: Home, Panda Library, Room Studio, Tasks + Night, Budget, Learning. Edits save to the hub's own database.
Source: `web/index.html`. Room Studio opens the original studio artifact (https://claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV). First-load data: `web/seed.json`.

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
web/                the web hub (claude.ai artifact) source + seed data
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
