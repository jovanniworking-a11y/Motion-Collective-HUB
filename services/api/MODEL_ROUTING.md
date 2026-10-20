# Model routing — MOTION control plane

Route each ask to the cheapest capable model/worker. Do not spam one model for everything. Never spend/send/post/publish from any model.

| Area | Channel | Default model | Worker |
|---|---|---|---|
| muse | #muse-3d | claude-sonnet → Codex for code | Codex |
| night-of | #night-of | claude-haiku | Claude |
| logistics | #logistics | claude-sonnet → Codex | Codex |
| creative | #creative | chatgpt (copy) / gemini (video) | ChatGPT / Gemini |
| orch | #orch | claude-sonnet | Claude orchestrator |

Overrides: IG captions → ChatGPT; reel audit → Gemini; SoT decisions → Claude only; spend/post → human gate.

API: `GET /api/routing`, `POST /api/routing/resolve`.
