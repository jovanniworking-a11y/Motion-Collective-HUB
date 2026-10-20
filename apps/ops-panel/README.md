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
| `/assist` | Ask Claude (Next route) |
| `/library` | Pinned tools |
