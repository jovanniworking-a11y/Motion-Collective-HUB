# MOTION Operations Panel

Crew control-plane UI for **Devil's Night · AFTERIMAGE 001**.

**Stack:** Next.js 15 · React 19 · Vitest · Playwright · talks to `services/api` (FastAPI).

**Draft only** — never spend/send/post/publish. No venue address, no guest PII.

## Run

```bash
# Terminal A — API
pip install -r ../../services/api/requirements.txt
python3 -m uvicorn app.main:app --app-dir ../../services/api --port 8787

# Terminal B — UI
npm install && npm run dev
# → http://localhost:3000
```

Desktop: from repo root `npm run desktop` (loads this panel when :3000 is up).

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
| `/data` | Muse sim vs imaging compare |
| `/assist` | Ask Claude (Next route) + Pro bridge |
| `/library` | Pinned tools |
| `/live-ops` | Night-of desk: door counter status, zones, HQ, run of show |
| `/counter-demo` | In-browser people counter. Frames stay on the device |
| `/hq` | Chaka live-ops dashboard (HQ view). Booth websocket is the counter on :8766 |

## Claude Pro ≠ API

Claude.ai Pro/Max does **not** include Anthropic API keys. For $0 API cost use **Open in Claude.ai** / **Copy prompt** on Assist and agent chat (paste into the browser). Details: [`CLAUDE_PRO_BRIDGE.md`](./CLAUDE_PRO_BRIDGE.md).
