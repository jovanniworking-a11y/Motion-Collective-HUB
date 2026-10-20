# Claude Pro bridge — $0 API path for MOTION ops

## Honest answer

**Claude.ai Pro / Max is not the Anthropic API.** A subscription to chat at [claude.ai](https://claude.ai) does **not** include API keys and cannot power server-side `POST /v1/messages` calls for free. Those are separate products; API usage is billed by Anthropic when you set `ANTHROPIC_API_KEY`.

Do **not** scrape claude.ai, reuse browser cookies/sessions, or use unofficial reverse APIs — that violates Terms of Service and is out of scope for this panel.

## What we ship instead: Prompt Bridge

In **Assist** (`/assist`) and **agent chat** (`/agents/[id]`):

1. Type your crew question (optional).
2. Click **Open in Claude.ai** (copies a rich prompt + opens [claude.ai/new](https://claude.ai/new)) or **Copy prompt**.
3. Paste into your Pro/Max session in the browser.
4. Usage is logged **locally** in `localStorage` as provider `pro-bridge` with labels `open` / `estimate` — not API tokens.

The prompt is built from **safe Source-of-Truth snippets** only (`CLAUDE_SAFE_CONTEXT` in `src/lib/ops-data.ts`): event hours, lineup order, labeled money numbers, welfare cadence. No guest PII, no venue address.

## Modes in the UI

| Pill | Meaning |
|------|---------|
| **Pro bridge mode** | No `ANTHROPIC_API_KEY` / `CLAUDE_API_KEY`. Prefer Open/Copy. **Send** still runs the deterministic mock. |
| **API mode** | Server has an Anthropic key. In-panel Send calls the API (billed). Pro bridge buttons remain available. |

## Orchestra already has Claude (no API required)

Cursor + Claude Code (if you have them) are the Pro/Cursor-billed brains for coding tasks. The ops panel is the **control plane**: it reads `orch/tasks` inbox/outbox, activity, and Night-Of state so you can see what agents are doing without any Anthropic API key.

## Optional API

See `.env.example`. Keys stay server-side; never commit secrets. Standing orders: draft only — never spend/send/post without Jovanni’s OK.
