# MOTION Operations Panel

Crew website + Night-Of ops for **Devil's Night · AFTERIMAGE 001**.

**Stack:** TypeScript · Next.js 15 (App Router) · React 19 · Vitest · Playwright.

**Draft only** — never spend, send, post, or publish from this app. No venue address, no guest PII.

## Why this stack

Apple-level ops UI needs real components, routing, and server hooks — not another static HTML throwaway. Next.js App Router gives polished client UI + server-only Claude proxy (`/api/claude`). Night-Of from `ops/` is ported into React with the same localStorage key (`motion-night-ops-v1`). Native (Tauri/Capacitor) can wrap this later; the website is the v1 product surface.

## Run locally

```bash
cd apps/ops-panel
npm install
npm run dev
# → http://localhost:3000
```

Optional live Claude (server-side only):

```bash
export ANTHROPIC_API_KEY=sk-ant-…   # or CLAUDE_API_KEY
# optional: export CLAUDE_MODEL=claude-sonnet-4-20250514
npm run dev
```

Without a key, Ask Claude uses a deterministic **mock** that still returns 200 and labeled facts.

## Pipelines

```bash
cd apps/ops-panel
npm run typecheck
npm run test          # vitest unit
npm run build
npx playwright install chromium   # once per machine
npm run test:e2e      # build+start via Playwright webServer
```

Or one shot:

```bash
npm run pipeline
```

## Routes

| Path | Role |
|------|------|
| `/` | Dashboard — countdown, status tiles, lineup (no public set times) |
| `/night-of` | Door check-in, run-of-show, welfare 30-min + 12:30 collision, budget |
| `/assist` | Ask Claude (POST `/api/claude`) |
| `/library` | Studio / Logistics / Board / FX cards |

Numbers are labeled **confirmed** / **estimate** / **open**. Check-ins + welfare logs stay in `localStorage` on the device; service worker caches the shell for offline-ish use.
