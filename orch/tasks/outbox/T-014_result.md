# T-014 — Claude Pro bridge ($0 API path)

## What I did
Shipped a legitimate **Prompt Bridge** so crew can use Claude.ai Pro/Max in the browser without Anthropic API spend. Honest framing: Pro/Max ≠ API keys.

## Files produced
- `apps/ops-panel/src/lib/proBridge.ts` — build paste-ready prompt from safe SoT; local `pro-bridge` usage log (`open` / `estimate`); open `https://claude.ai/new`
- `apps/ops-panel/src/lib/proBridge.test.ts`
- `apps/ops-panel/src/components/ProBridgeActions.tsx` — Open in Claude.ai / Copy prompt
- `apps/ops-panel/src/components/AskClaude.tsx` — Pro bridge mode vs API mode pills + bridge panel
- `apps/ops-panel/src/app/agents/[id]/page.tsx` — same bridge on agent chat
- `apps/ops-panel/src/app/api/claude/route.ts` — `uiMode` + proBridge metadata on GET
- `apps/ops-panel/src/lib/claude.ts` — mock copy points at Pro bridge
- `apps/ops-panel/CLAUDE_PRO_BRIDGE.md` — short doc
- `apps/ops-panel/.env.example` — API key optional
- `apps/ops-panel/README.md`, e2e smoke, `services/api` mock note

## How verified
- `npm run typecheck` + `npm run test` in `apps/ops-panel` (vitest includes proBridge + claude)

## Proposed SoT changes
None.

## Questions for Jovanni
None — draft only; no spend.
