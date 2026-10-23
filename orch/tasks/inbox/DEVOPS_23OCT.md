# MOTION Ops · dev work brief · Fri 23 Oct (7 days to doors)
**From:** Claude Code (orchestrator seat) · **To:** Cursor (T-024–T-027, T-029), Codex (T-028)
**Read first:** `AGENTS.md`, `ARCHITECTURE.md`, `services/api/MODEL_ROUTING.md`. MVP only. Night-Of is priority #1, and nothing in the "later" list ships before 30 Oct.

## State checked 23 Oct (Claude Code)
| Check | Result | Label |
|---|---|---|
| `services/api` pytest | 8 passed | confirmed |
| `apps/ops-panel` `npm ci` | **failed**: lock file out of sync (`@testing-library/dom` missing). **Fixed**: lock re-synced in this push | confirmed |
| Panel typecheck / vitest / `next build` | pass / 16 passed / builds | confirmed |
| CI | none: there's no `.github/workflows` | confirmed |
| `vercel.json` | routes panel + API as two services. **No auth**, which ARCHITECTURE.md forbids for anything public | confirmed |
| `ops-data.ts`, `ops/data.js`, `chat.py` seed | still say "Rohan Rali is cut" and buffer $68.87. Now: Rohan back at $175 (slot open), pool $498, buffer $116.87 (estimate) | confirmed |

## T-024 · CI · priority 1 · due Sat 24 Oct
**Goal:** every push to the default branch proves both services still work.
**Deliverable:** `.github/workflows/ci.yml` with two jobs:
- `api`: Python 3.12, `pip install -r services/api/requirements.txt`, `pytest -q services/api`.
- `panel`: Node 20, in `apps/ops-panel`: `npm ci`, `npm run typecheck`, `npx vitest run`, `npm run build`.
**Rules:** no secrets in the workflow. `ANTHROPIC_API_KEY` stays unset, so chat runs in mock mode.
**Done when:** a green run shows on the branch, linked in `outbox/T-024_result.md`.

## T-025 · Night-Of readiness · priority 1 · due Tue 27 Oct
**Goal:** the door and show crew can run the night from phones with bad Wi-Fi.
**Deliverable:**
1. Check-in by pass number with a live count against **cap 70 (confirmed)**, plus a clear "at cap" state.
2. `ops/` PWA and the panel's `/night-of` agree on the same data semantics (`motion-night-ops-v1`).
3. Offline test: load once, switch to airplane mode, check in 5 test passes, reload, and the counts survive.
4. Lineup and run-of-show data: add **Rohan Rali** as booked ($175, confirmed) with his slot as **open** until Jovanni sets it (D-1). Don't move Glamz. Credit HE//THEY exactly `HE//THEY · co.b b2b NiiON`.
5. A Playwright e2e for `/night-of` covering check-in, the cap state and a reload.
**Rules:** pass numbers only, no names/phones/emails. No venue address. Set times are crew-internal and never shown on any public page.
**Done when:** the e2e passes in CI and `outbox/T-025_result.md` has screenshots from the phone-width viewport.

## T-026 · Hosting gate · priority 2 · due Wed 28 Oct
**Goal:** decide how the panel gets to crew phones without going public.
**Deliverable:** a short options note, plus an implemented auth gate behind a flag:
- **Options:** (a) local network only, with the laptop as host; (b) a Vercel preview with Vercel password protection; (c) a Next middleware shared-passcode cookie plus an API token check.
- Recommend one, with its cost (label confirmed, estimate or open).
**Rules:** **do not deploy.** Jovanni OKs any URL that leaves the laptop. API keys stay server-only.
**Done when:** `outbox/T-026_result.md` has the recommendation, and the gate is tested locally.

## T-027 · Metering + seed refresh · priority 2 · due Tue 27 Oct
**Goal:** the usage page tells the truth.
**Deliverable:**
1. A test proving every `/api/agents/*` call writes one `usage_events` row (bot, area, model, counts, latency, status), with no raw prompt text stored.
2. `/api/routing` matches `MODEL_ROUTING.md`.
3. The money facts in `chat.py`, `ops-data.ts` and `ops/data.js` are refreshed:

| Item | Amount | Label |
|---|---|---|
| Pool | $498 (3 × $166) | confirmed (plan) |
| Pool spend | $381.13 | estimate |
| Buffer | $116.87 | estimate |
| DJ fees | $475 = HE//THEY $300 + Rohan $175 | confirmed |
| CDJs | $345 | confirmed |

**Done when:** pytest has the new test, the panel shows the new figures, and `outbox/T-027_result.md` is written.

## T-028 · Desktop on Jovanni's PC · Codex · due Mon 26 Oct
The prompt is in `orch/tasks/PROMPTS_23OCT.md`. Result: `outbox/T-028_result.md`.

## T-029 · Night-of runbook · priority 2 · due Wed 28 Oct
**Deliverable:** `ops/RUNBOOK.md`, one page:
- what to start and when (API, panel, or the phone PWA only);
- which phones load `ops/`, and how to pre-cache it;
- the fallback if the laptop dies (paper list of pass numbers);
- the 2 AM shutdown and the data wipe (nothing personal kept).
**Rules:** no address, no names.

## Out of scope before 30 Oct
- Studio live-edit and real sims (they stay `smoke-stub`)
- cost charts
- multi-user auth
- the hub.py merge
- any in-app coding IDE
