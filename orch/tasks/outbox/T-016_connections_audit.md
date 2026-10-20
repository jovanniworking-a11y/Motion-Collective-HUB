# T-016 — Connections audit (Cursor online)

**When:** 2026-10-20T15:53Z (UTC) · **Branch tip at audit:** `cursor/muse-cloud-platform-c430` (from `cursor/ops-cloud` @ `4a8a806`)  
**Standing orders:** no spend / send / post / publish · camera **not** ordered · no venue address / guest PII · secrets not printed.

## Cursor presence

| Signal | Evidence |
|--------|----------|
| Root `AGENTS.md` | Present — control-plane + cloud path |
| This agent can push | `git push` auth via `origin` HTTPS token (dry-run OK); prior `cursor/*` remotes exist |
| GitHub *connector* write for other seats | **Unknown from here** — ChatGPT seat blocked is a product/connector setting; Jovanni toggles in GitHub/ChatGPT admin |
| Outbox receipts | This file + T-015_result (studio helper) + board corrections |

## Status table

| Connection | Status | Evidence (command / path) | Bring DEGRADED/DOWN → RUNNABLE |
|---|---|---|---|
| Git remotes + push (this env) | **RUNNABLE** | `git remote -v` → github.com/jovanniworking-a11y/Motion-Collective-HUB; `git push --dry-run` accepted | — |
| Branches `cursor/*` | **RUNNABLE** | Local+remote: ops-cloud, ops-software-8efd, claude-pro-bridge, muse-cloud-platform-c430, … | Merge when Jovanni OK |
| `python hub.py` / root requirements | **RUNNABLE** | After `pip install -r requirements.txt`, `python3 hub.py check` ran (registry report) | Keep pandas/openpyxl in env |
| `apps/ops-panel` build/dev | **RUNNABLE** | `npm run typecheck` · `npm run test` (18) · `npm run build` (includes `/data`) | `npm ci` if node_modules missing |
| `services/api` FastAPI + pytest | **RUNNABLE** | `from app.main import app` · `pytest -q` → **8 passed** | `pip install -r services/api/requirements.txt` |
| `desktop/` optional Electron | **RUNNABLE** (smoke) | `MOTION_OPS_SMOKE=1 npm run smoke` → `[MOTION Ops] smoke OK` (D-Bus noise expected headless) | Optional; cloud panel URL preferred |
| Studio `_t2.py` | **RUNNABLE** | Rebuilt; `python3 _t2.py smoke` → studio ok, items=10, screenshot `shots/t2_smoke.png` | Prelude unblocks `_night2` / `_all2` / `_chk*` |
| Studio `_all2.py` / `_night2.py` | **DEGRADED** | Scripts present; full night/optimize runs are heavy; helper boot via exec **confirmed** | Run with time budget on PC/GPU-capable host; `MOTION_SIM_EXECUTE=1` on API |
| Playwright / Chromium | **RUNNABLE** (patched) | Package installed; launch via cached `chromium-1169` executable_path (new Playwright wanted 1248 — patched in `_t2.py`) | Or `playwright install` if allowed; set `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` |
| `ANTHROPIC_API_KEY` | **DOWN** (absent) | env probe = NO | Jovanni sets only if billed API Assist wanted |
| `CLAUDE_API_KEY` | **DOWN** (absent) | NO | Same |
| `GROQ_API_KEY` | **DOWN** (absent) | NO — ping **skipped** | Add key → cheap model ping |
| Google / Gemini keys | **DOWN** (absent) | GOOGLE_API_KEY / GEMINI_API_KEY / GOOGLE_GENERATIVE_AI_API_KEY = NO — ping **skipped** | Add key → short ping with timeout |
| Fly tokens | **DOWN** (absent) | FLY_API_TOKEN / FLY_ACCESS_TOKEN = NO; `fly`/`flyctl` MISSING | Install CLI + `fly auth login` (human) |
| Vercel token | **DOWN** (absent) | VERCEL_TOKEN = NO; `vercel` MISSING | Dashboard click-path in `docs/CLOUD_HOSTING.md` |
| Cloud hosting configs | **RUNNABLE** (configs only) | `docs/CLOUD_HOSTING.md`, `fly.toml`, Dockerfiles, `vercel.json` | Live URL: Jovanni Path A deploy — **no live URL verified this run** |
| Pro Prompt Bridge | **RUNNABLE** | `apps/ops-panel/CLAUDE_PRO_BRIDGE.md` + `src/lib/proBridge.ts` · panel Assist | Use Open in Claude.ai ($0 API) |
| Muse data platform | **RUNNABLE** (local MVP) | `/api/data/*` + SQLAlchemy SQLite · `docs/MUSE_DATA_PLATFORM.md` · panel `/data` | Attach Postgres `DATABASE_URL` + object storage later |
| Groq live (11 models) claim | **UNKNOWN** here | No key in this env — cannot verify ChatGPT/other seat claim | Supply `GROQ_API_KEY` to re-probe |
| Gemini jobs / verification ping | **UNKNOWN** here | No key; prior timeout reported in briefing only | Re-ping with timeout when keyed |

## Model / spend policy (this run)

- No paid API calls attempted (keys absent).
- No Fly/Vercel/Railway deploy attempted (CLIs missing / not logged in).
- Camera **not** ordered.

## Proposed follow-ups for Jovanni

1. GitHub connector write-access for ChatGPT seat (product toggle) — separate from Cursor cloud push (**already works**).
2. Path A deploy: Vercel panel + Fly API (`docs/CLOUD_HOSTING.md`).
3. Optional keys: Groq (mechanical), Gemini (audit), Anthropic API only if billed Assist desired — prefer Pro bridge.
4. Explicit buy order before any camera purchase.
