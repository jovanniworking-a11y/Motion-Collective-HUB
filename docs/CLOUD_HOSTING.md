# MOTION Ops — cloud hosting (clickable website)

**Goal:** run the crew control plane as a **URL in the browser**, not only on a PC. Electron desktop stays **optional**.

**Recommended free-tier path:** **Vercel (ops panel) + Fly.io (API)**  
**Alt (one vendor):** **all-on-Railway** (panel Docker + API Docker).

Draft only — never spend / send / post / publish without Jovanni’s OK. No venue address, no guest PII in env or logs.

---

## Architecture

| Piece | Path | Cloud host |
|-------|------|------------|
| Frontend | `apps/ops-panel` (Next.js) | **Vercel** (free hobby) or Railway Node/Docker |
| Backend | `services/api` (FastAPI) | **Fly.io** free allowance or Railway / Render |
| Desktop | `desktop/` (Electron) | Optional local shell; cloud users open the panel URL |
| Claude | Pro **Prompt Bridge** | Default on cloud ($0 API). API mode only if `ANTHROPIC_API_KEY` is set on the server |

```
Browser  →  https://<panel>.vercel.app
                │  NEXT_PUBLIC_API_URL
                ▼
         https://<api>.fly.dev   (CORS allows panel origin)
```

### Env contract

| Var | Where | Purpose |
|-----|-------|---------|
| `NEXT_PUBLIC_API_URL` | Panel (Vercel/Railway) | Public API origin, no trailing slash |
| `MOTION_API_CORS` | API | Comma-separated panel origins |
| `MOTION_DATA_DIR` | API | SQLite + JSON store (`/tmp/motion-api-data` OK for MVP) |
| `ANTHROPIC_API_KEY` | API and/or panel Assist route | **Optional.** Omit → mock chat + Pro bridge |

Templates: `apps/ops-panel/.env.example`, `services/api/.env.example`.

### SQLite / ephemeral disk (MVP)

Usage metering uses SQLite under `MOTION_DATA_DIR`. On Fly/Railway **without a volume**, `/tmp` (and often the whole FS) is wiped on redeploy or machine replace. That is **expected for MVP** — label counts `estimate` after a reset. Attach a volume later only if you need persistence (may leave free tier).

---

## Path A — Vercel panel + Fly API (recommended)

### 1) Deploy API on Fly.io (free allowance)

1. Install CLI: https://fly.io/docs/hands-on/install-flyctl/
2. `fly auth login` (browser).
3. From **repo root** on branch `cursor/ops-cloud` (or main after merge):

```bash
fly apps create motion-ops-api   # pick a unique free name; edit `app` in fly.toml to match
fly secrets set MOTION_API_CORS=https://PLACEHOLDER.vercel.app
fly deploy                       # uses root fly.toml → services/api/Dockerfile
```

4. Note the URL: `https://motion-ops-api.fly.dev` (or your app name) — health: `/health`.

Infra files: `fly.toml`, `services/api/Dockerfile`, `services/api/railway.toml` (alt).

### 2) Deploy panel on Vercel (free hobby)

**Dashboard click-path (no CLI required):**

1. Open https://vercel.com/new  
2. Import **jovanniworking-a11y/Motion-Collective-HUB** (GitHub).  
3. **Root Directory** → `apps/ops-panel`  
4. Framework preset: Next.js (auto).  
5. Environment variables:
   - `NEXT_PUBLIC_API_URL` = `https://motion-ops-api.fly.dev` (your Fly URL, no trailing slash)
6. Deploy. Copy the production URL, e.g. `https://ops-panel-xxx.vercel.app`.

**Then update API CORS:**

```bash
fly secrets set MOTION_API_CORS=https://ops-panel-xxx.vercel.app,http://localhost:3000
```

Redeploy API only if secrets do not hot-reload on your plan (`fly deploy`).

CLI alt (if `vercel` is logged in):

```bash
cd apps/ops-panel
vercel link
vercel env add NEXT_PUBLIC_API_URL
vercel --prod
```

Config: `apps/ops-panel/vercel.json`.

### 3) Smoke the live pair

- Panel loads in a phone/laptop browser (no Electron).  
- Dashboard / Agents hit the API (`/health` → `ok`).  
- Assist shows **Pro bridge mode** unless you set an API key.  
- Use **Open in Claude.ai** / **Copy prompt** for $0 API spend.

---

## Path B — All-on-Railway

1. https://railway.app/new → Deploy from GitHub repo.  
2. **Service 1 — API:** Dockerfile path `services/api/Dockerfile` (see `services/api/railway.toml`).  
   Vars: `MOTION_API_CORS`, `MOTION_DATA_DIR=/tmp/motion-api-data`.  
3. **Service 2 — Panel:** Dockerfile `apps/ops-panel/Dockerfile` **or** Railway’s Nixpacks with root `apps/ops-panel`.  
   Vars: `NEXT_PUBLIC_API_URL=https://<api-service>.up.railway.app`  
   For Docker panel builds, pass build arg `NEXT_PUBLIC_API_URL` (Next inlines it at build).  
4. Generate public domains for both services; put the panel origin into `MOTION_API_CORS`.

Railway free/trial credits are limited — prefer Path A if you want long-lived free static UI.

---

## Claude on cloud (Pro bridge default)

- **Do not** put Anthropic keys in the repo or chat.  
- Cloud default = **Pro Prompt Bridge** (same as local): paste-ready prompts + claude.ai. Doc: `apps/ops-panel/CLAUDE_PRO_BRIDGE.md`.  
- Only set `ANTHROPIC_API_KEY` on Fly/Railway/Vercel if Jovanni deliberately wants billed API Assist.

---

## Desktop (optional)

`desktop/` Electron is for crew who want a tray window on a PC. Point it at the cloud panel:

```bash
MOTION_OPS_URL=https://YOUR-PANEL.vercel.app npm run desktop --prefix desktop
```

Cloud-first users never need Electron — open the Vercel URL.

---

## Local smoke (this repo)

```bash
# API
pip install -r services/api/requirements.txt
python3 -m uvicorn app.main:app --app-dir services/api --host 127.0.0.1 --port 8787

# Panel
cd apps/ops-panel && npm ci && npm run build && npm start
# optional: NEXT_PUBLIC_API_URL=http://127.0.0.1:8787

# Docker (if Docker is installed)
docker build -f services/api/Dockerfile -t motion-api .
docker build -f apps/ops-panel/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://127.0.0.1:8787 -t motion-ops-panel .
```

---

## This agent run — deploy status

Deploy CLIs (`fly`, `vercel`, `railway`) were **not logged in** in the cloud agent environment, and paying for credits was avoided. Infra-as-code + this doc are the deliverable; Jovanni can finish Path A with the click-path above using existing free accounts.

After deploy, expected URLs (replace with yours):

- Panel: `https://<project>.vercel.app`  
- API: `https://motion-ops-api.fly.dev/health`
