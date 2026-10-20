# T-015 — MOTION Ops cloud hosting (clickable website)

## What I did
Made the control plane **cloud-first**: infra-as-code + docs for a free-tier website (Vercel panel + Fly/Railway API). Electron marked optional. Pro Prompt Bridge remains the default Claude path ($0 API). Did **not** run a paid deploy — no `fly` / `vercel` / `railway` login in this environment.

## Files produced
- `docs/CLOUD_HOSTING.md` — deploy paths, env contract, SQLite ephemeral warning, Pro bridge, click-path for Jovanni
- `services/api/Dockerfile` + root `.dockerignore` — API image (repo-root context)
- `apps/ops-panel/Dockerfile` — optional panel image (`DOCKER_BUILD=1` standalone)
- `fly.toml` — Fly.io API (shared-cpu / auto-stop)
- `services/api/railway.toml`, `apps/ops-panel/railway.toml`, `apps/ops-panel/vercel.json`
- `services/api/.env.example`, `apps/ops-panel/.env.example` — cloud vars (`NEXT_PUBLIC_API_URL`, `MOTION_API_CORS`, `MOTION_DATA_DIR`)
- `services/api/app/config.py` — `MOTION_DATA_DIR` / `MOTION_REPO_ROOT` / CORS
- `apps/ops-panel/src/lib/api.ts` — prefers `NEXT_PUBLIC_API_URL`
- README / `AGENTS.md` / `desktop/README.md` — cloud primary, desktop optional
- `orch/tasks/outbox/T-015_result.md`

## How verified
- Tip SHA: `63884e8360c28618f54325dec992925a1744d499` on `cursor/ops-cloud`
- `cd apps/ops-panel && npm run typecheck && npm run test && npm run build` (18 vitest OK)
- `cd services/api && python3 -m pytest -q` (7 passed)
- Docker CLI **not installed** here — Dockerfile smoke skipped; build commands documented
- Deploy CLIs not authenticated — stopped before paid deploy per standing orders

## Proposed SoT changes
None.

## Questions for Jovanni
1. Finish Path A in `docs/CLOUD_HOSTING.md` with your Vercel + Fly free accounts when ready (no keys in chat).
2. Confirm app name `motion-ops-api` on Fly or edit `fly.toml` `app =`.

## Branch
https://github.com/jovanniworking-a11y/Motion-Collective-HUB/tree/cursor/ops-cloud
