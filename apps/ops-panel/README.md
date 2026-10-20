# MOTION Operations Panel

Crew control-plane UI for **Devil's Night · AFTERIMAGE 001**.

**Stack:** Next.js 15 · React 19 · Vitest · Playwright · talks to `services/api` (FastAPI).

**Draft only** — never spend/send/post/publish. No venue address, no guest PII.

## Run (local)

```bash
# Terminal A — API
pip install -r ../../services/api/requirements.txt
python3 -m uvicorn app.main:app --app-dir ../../services/api --port 8787

# Terminal B — UI
npm install && npm run dev
# → http://localhost:3000
```

Set `NEXT_PUBLIC_API_URL` when the API is not on `http://127.0.0.1:8787` (see `.env.example`).

## Cloud (primary for “run on cloud”)

Host this app on **Vercel** and point `NEXT_PUBLIC_API_URL` at the Fly/Railway API.  
Step-by-step: [`docs/CLOUD_HOSTING.md`](../../docs/CLOUD_HOSTING.md).

Desktop Electron (`desktop/`) is **optional** — cloud users open the Vercel URL in a browser.

## Tests

```bash
npm run typecheck && npm run test
# optional: npm run test:e2e
```

## Routes

| Path | Role |
|------|------|
| `/` | Dashboard |
| `/night-of` | Door / show / welfare / budget |
| `/agents` · `/agents/[id]` | Area bots → FastAPI chat |
| `/usage` | Metered calls |
| `/activity` | Board + outbox feed |
| `/muse` | Studio embed + Run sim |
| `/data` | Muse sim vs imaging compare (counts/hashes only) |
| `/assist` | Ask Claude (Next route) + Pro bridge |
| `/library` | Pinned tools |

## Claude Pro ≠ API

Claude.ai Pro/Max does **not** include Anthropic API keys. For $0 API cost use **Open in Claude.ai** / **Copy prompt** on Assist and agent chat (paste into the browser). Details: [`CLAUDE_PRO_BRIDGE.md`](./CLAUDE_PRO_BRIDGE.md).
