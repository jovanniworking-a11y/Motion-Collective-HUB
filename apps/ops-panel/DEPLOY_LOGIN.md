# Login + 2FA for the Vercel deploy

Every page and every `/api/*` call needs a session. You get one with **name + password + a 6-digit authenticator code**. On Vercel the app **fails closed**: if the login settings are missing, it serves nothing (HTTP 503) instead of serving the app openly.

## One-time setup (Jovanni)
1. On your computer, in `apps/ops-panel`, run `npm run auth:add-user -- jovanni` and type a password of 12+ characters.
2. It prints three things:
   - **MOTION_AUTH_USERS entry**: put it inside `[ ]` (add one entry per crew member, separated by commas).
   - **Setup key**: in Google Authenticator / 1Password / Authy, choose "Add account → Enter setup key" and paste it.
   - **Session secret**: shown once.
3. In Vercel → Project → Settings → Environment Variables (Production **and** Preview), add the following, then redeploy:

| Name | Value | Goes to |
|---|---|---|
| `MOTION_SESSION_SECRET` | the session secret (32+ characters) | both services (panel and api) |
| `MOTION_AUTH_USERS` | `[{"u":"jovanni",...}]` | panel |
| `DATABASE_URL` | pooled Postgres URL (`postgres://…` is fine) | api |
| `MOTION_AGENT_TOKEN` | optional: a separate random 32+ character token. It lets agents on other machines use `/api/agentops/*` (shared leases, stamp mirror) and nothing else | api (and as a GitHub Actions secret with `MOTION_API_URL` for the mirror) |
| `GUEST_DENYLIST` | optional: guest full names, comma-separated. The API refuses stamps that contain them | api (and as a GitHub Actions secret for CI) |

4. Recommended extra layer at no cost: Vercel → Settings → Deployment Protection → **Vercel Authentication** on, so preview URLs also need a Vercel login. (On production this would also block agents' token calls. Leave it on previews only, or give agents the Vercel protection-bypass header.) Turn on 2FA on your Vercel and GitHub accounts too.

## How it works
- `src/middleware.ts` gates every panel route and returns 401 for `/api/*` without a session.
- `POST /api/auth/login` checks the scrypt password hash and the TOTP code. It allows ±30 s of clock drift, blocks a code from being reused, and locks out for 15 minutes after 5 failed tries per IP or name.
- The session cookie is `motion_session`: HMAC-signed, httpOnly, Secure, SameSite=Strict, valid for 12 h.
- The FastAPI service checks the same cookie (`services/api/app/auth.py`), because Vercel rewrites send `/api/agents|data|usage|…` straight to it. `/health` stays open and returns no data.
- Logging out clears the cookie and the offline page cache.
- Locally, with no `MOTION_SESSION_SECRET` set and not on Vercel, the login is off so dev and tests work.

## Removing someone
Delete their entry from `MOTION_AUTH_USERS` and redeploy. To sign **everyone** out immediately, change `MOTION_SESSION_SECRET`.

## Limits (be honest)
The lockout counter lives in each server instance's memory, so on serverless it slows down guessing rather than stopping it outright. The strength comes from the password and the 2FA code together. Before adding more people, consider a hosted identity provider (e.g. Clerk/Auth0, which have free tiers; estimate).

<!-- AGENT_WORKLOG:BEGIN -->
<!-- AGENT_LOG {"v":"1.0","ts":"2026-10-24T21:04:59.865Z","agent":"claude-code","trace":"tr_842ee7b5007b4fed","status":"completed","verify":"verified_passed","hash":"sha256:12664d672a54812b6469e23eb6f41a9e74e1c04b0d6bb5ad0144d9ac1ba93607","ledger":".agent/ledger.jsonl"} -->

#### Agent work log
| UTC | Agent | Status | Summary | Next | Trace |
|---|---|---|---|---|---|
| 2026-10-24T21:04:59Z | claude-code | completed / verified_passed | Close the four provenance limits: shared leases, guest denylist, coverage gate, agent reg… | Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION… | `tr_842ee7b5007b4fed` |
<!-- AGENT_WORKLOG:END -->
