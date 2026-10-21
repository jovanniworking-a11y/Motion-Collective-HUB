# T-019 result · Link audit and autonomous check

**Seat:** Cursor  
**Branch:** `cursor/architecture-link-audit-3a45`  
**Status:** draft / local only. Nothing spent, sent, posted, or published.  
**Not touched:** `orch/context/` Source of Truth · Fly/Vercel/Docker hosting · camera order

## What I did

Audited the control plane on `main` against `ARCHITECTURE.md` and the Muse data contract. The API `/api/data/*` was already on `main`. The panel route the Muse doc names (`/data`) was not, Library was a page with no nav link, and the crew-hub card pointed at `/legacy-note` (no page). GitHub library links still used the old default branch.

- Added the Data / Compare page and client calls for the existing FastAPI routes.
- Nav now includes Data and Library. The bottom bar sizes from the link count (it was locked at 7).
- Service worker precache matches those routes.
- Crew hub, Source of Truth, and the task board open the `main` blobs.
- Teaser/promo HTML now points at `media/brand/MOTION_mark_3d.png` and `media/flyers/final_v6/eyes_hc.png`.
- Added `scripts/check_links.py` (also `python hub.py links` and pytest `test_repo_links_and_routes`). GitHub Actions workflow `autonomy` runs that check, API pytest, and the panel typecheck + unit tests.

Hosting configs stay on `cursor/muse-cloud-platform-c430`. This branch does not deploy.

## Files

- `apps/ops-panel/src/app/data/page.tsx`, `src/lib/api.ts`, `src/components/AppShell.tsx`, `src/app/library/page.tsx`, `src/lib/ops-data.ts`, `src/app/globals.css`, `public/sw.js`
- `scripts/check_links.py`, `services/api/tests/test_links.py`, `.github/workflows/autonomy.yml`
- `media/posts/teaser_breakdown/shotlist.html`, `media/posts/lineup_v2/src/promo_18oct.html`, `media/teasers/teaser_cards_source.html`
- `README.md`, `ARCHITECTURE.md`, `docs/MUSE_DATA_PLATFORM.md`, `hub.py`

## How verified

- `python scripts/check_links.py` → OK. **36** missing font files reported as open, not a failure. **confirmed** this run.
- `cd services/api && python3 -m pytest -q` → **9 passed** (includes the link check and a completed `smoke-stub` row). **confirmed** this run.
- `cd apps/ops-panel && npm run typecheck && npm test` → typecheck clean, **16** vitest tests passed. **confirmed** this run.
- Live uvicorn `:8787` and Next `:3000`: every nav route returned 200. `/legacy-note` is 404 because that card now opens the `main` blob for `web/index.html`. GitHub blobs for the Source of Truth, board, and `web/index.html` returned 200. **confirmed** this run.
- Browser: seed on `/data` finishes `completed` and stays `estimate`; Compare shows `label: estimate`; Library, Night pass 003 (count 0 → 1), and Dash all load. **confirmed** this run.

Debug fixed in the same branch: `/api/data/sims/run` used to store the row while the thread was still `running`. Short stubs now wait (under 2s) and store the finished row. A copied studio score stays `estimate` because the stub did not re-run the night.

## Open

- **36** local font files (fontsource `.woff2`) referenced by teaser HTML are not in git. The check reports them and does not fail. Pages fall back to system faces. Label: **open**.
- `_t2.py` studio smoke is still only on the muse branch. Label: **open**.
- Live Fly/Vercel URLs are not created. Label: **open** until Jovanni OKs a deploy.
- Route aliases `/ops/snapshot` and `/usage/events` are still not the live paths. Live contract is `/api/*`. Label: **open** naming, behavior present.

## Proposed SoT changes

None.

## Questions for Jovanni

1. OK to leave font packs out of git?
2. Fold `_t2.py` in a later branch, separate from hosting?
3. Deploy stays off until you log into Fly/Vercel?
