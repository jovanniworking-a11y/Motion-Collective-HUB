# MOTION Orchestra — how Claude runs the other agents

**Orchestrator:** Claude (this project, "MOTION EFFEcts"). **Workers:** Codex (code/files), ChatGPT (copy/research), Gemini (long-context, multimodal, Google Workspace). **Owner:** Jovanni (creative director) — final say on anything that costs money, is published, or names a person.

## Why a file protocol
Workers can't call each other or Claude directly. Everything moves through this folder (share it by Git repo, or a shared Drive folder, or just unzip it for each worker):

```
context/        read-only truth: project docs 00–12, Drive exports, latest Source of Truth, studio code, assets
tasks/BOARD.md  the one list of work: who owns what, status
tasks/inbox/    Claude drops one brief per task here (T-###_name.md)
tasks/outbox/   workers drop results here (T-###_result.md + any files)
tasks/done/     Claude archives after review
workers/        one briefing file per worker
```

## Loop
1. Jovanni tells Claude what he wants.
2. Claude splits it, writes `tasks/inbox/T-###.md` from `tasks/TEMPLATE.md`, assigns a worker, updates BOARD.md.
3. Jovanni (or a script) hands the brief to that worker: "Read AGENTS.md / GEMINI.md, then do tasks/inbox/T-###.md."
4. Worker writes result to `tasks/outbox/` and changes nothing in `context/`.
5. Claude reviews against the rules (below), merges, updates the Source of Truth in the Claude Project (`claude/00 …`), and moves the task to `done/`.

**Only Claude edits the Source of Truth.** Workers propose changes in their result file under a "Proposed SoT changes" heading.

## Who gets what
| Worker | Strengths here | Typical tasks |
|---|---|---|
| Claude | Orchestration, Project docs, artifacts, Gmail/Drive/Calendar/Figma/Tally connectors, design review | Decisions, SoT, run-of-show, review every output |
| Codex | Code + file edits, tests | Room Studio (`context/studio/index.html`) changes and Playwright tests, re-run sims with real measurements, rebuild budget workbook (.xlsx), scripts |
| ChatGPT | Copy, quick research, image ideas | IG captions, DM drafts (Glamz, neighbours), vendor price checks, RSVP/Partiful copy |
| Gemini | Long context, video/image understanding, Google Workspace | Review Higgsfield/reel clips, audit Drive sheets, compare flyer versions visually, big research sweeps |

## Hard rules for every agent (from the Source of Truth + Agent Playbook)
1. The **address is never public** and never in any file you produce.
2. **No unconfirmed names on promo.** Rohan Rali is CUT (14 Oct). Glamz is unconfirmed. HE//THEY is credited exactly "HE//THEY · co.b b2b NiiON".
3. **Never spend, send, post or publish.** Draft only. Jovanni approves.
4. No YSL marks, no haze/fog, no lasers. Hairline Bodoni Moda + Jost. Red ≤ 10% of frame. Client taste beats the Playbook.
5. Label every number *confirmed / estimate / open*. Don't invent prices.
6. Don't edit `context/`. Write to `tasks/outbox/`.
7. Everyone on the crew is 21+; guests are ID-checked. No alcohol sales/collection (Texas law).
