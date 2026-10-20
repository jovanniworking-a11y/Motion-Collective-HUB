# T-013 · MOTION control-plane vertical slice

**Owner:** Cursor · **Branch:** `cursor/ops-software-8efd` · **Status:** draft / local only

## What I did
Shipped working control-plane slice on the ops-software product branch:
- FastAPI backend (`services/api`): 5 area agents, chat/correct/form, usage SQLite, activity from BOARD+outbox, Muse layout bridge, sim jobs (stub by default).
- Next modules: `/agents`, `/usage`, `/activity`, `/muse` talking to the API.
- Desktop shell already on branch; README/AGENTS run instructions.
- Model routing: `services/api/MODEL_ROUTING.md`.

## Verified
- `python3 -m pytest -q` in `services/api`
- `npm run test` in `apps/ops-panel`

## Proposed SoT changes
None.

## Questions
1. Keep sims stubbed until you set `MOTION_SIM_EXECUTE=1`?
