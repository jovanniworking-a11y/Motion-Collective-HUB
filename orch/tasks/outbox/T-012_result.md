# T-012 · MOTION Operations Panel (Next.js)

## What I did
Shipped a real ops website (not static HTML) at `apps/ops-panel`: dashboard, Night-Of port, Ask Claude, library. Folded Night-Of capabilities from `ops/` (same `localStorage` key `motion-night-ops-v1`). Draft only — no spend/send/post.

## Stack choice (5 lines)
1. **TypeScript + Next.js 15 App Router + React 19** for App Store-grade UI, routing, and server hooks.
2. Domain data in `src/lib/ops-data.ts` (+ time/check-in helpers) shared by dashboard and Night-Of.
3. **Claude proxy** at `POST /api/claude` — keys server-only (`ANTHROPIC_API_KEY` / `CLAUDE_API_KEY`); deterministic mock when absent.
4. **Vitest + Playwright** pipelines (`npm run pipeline`).
5. Native shell (Tauri/Capacitor/Electron) deferred — website is the v1 product surface.

## Files produced
- `apps/ops-panel/` — full Next app (pages, components, API, tests, README)
- `README.md`, `AGENTS.md`, `ops/README.md`, `.gitignore` — point at the panel
- Legacy `ops/` kept as zero-build fallback

## How verified
```bash
cd apps/ops-panel
npm run typecheck   # pass
npm run test        # 10/10 vitest
npm run build       # pass
CI=1 npm run test:e2e  # 4/4 Playwright: dashboard, check-in, welfare log, Claude 200
```

## Proposed SoT changes
None required. Optional later: note “Ops panel = apps/ops-panel” in SoT Index.

## Questions for Jovanni
1. Prefer live Claude (set `ANTHROPIC_API_KEY`) vs keep mock for crew phones?
2. Host this panel privately (Vercel/self-host) when you’re ready, or Electron wrap first?
3. Working cap still **50 estimate** / passes **70 open** — confirm before door night.

## Commit
`7f7d5cb9f709bb8e85017d76ac37e071b46da547` on `cursor/ops-software-1366`
