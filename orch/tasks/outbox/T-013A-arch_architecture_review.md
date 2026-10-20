# T-013A-arch · Architecture / product-sense review — MOTION Ops control plane

**Rename note (20 Oct):** was `orch/tasks/outbox/T-013_architecture_review.md` on `cursor/architecture-review-07eb`. Renamed to **T-013A-arch** so it does not collide with **board T-013** (Abraham’s brief). Board numbering untouched.

**Owner:** Cursor (Claude Code seat)  
**Source branch:** `cursor/architecture-review-07eb` @ `e7b4fe8` (from `cursor/ops-software-8efd`)  
**Carried onto:** `cursor/backend-reconcile-c926` (from `cursor/claude-pro-bridge`)  
**Compared (original review):** `cursor/night-of-ops-6609` (`ops/`), `cursor/ops-desktop-e7a0` (`desktop/`), in-flight `apps/ops-panel` + empty `services/api` on ops-software  
**Status:** draft / steer only — no spend, no publish  
**Numbers:** none changed (labels N/A)

---

## 1. Verdict

**Yes — the idea makes sense.** A Discord-like crew shell + one Python BFF + metered agent rooms + Night-Of dashboards is a real product shape (ops console / control plane), not vapor — **if** you ship it in phases and refuse to boil the ocean before Oct 30.

Blunt: trying to land *live Muse/Room Studio edit + sim jobs + multi-model router + usage live-view + full bot workspace* in one release is **overscoped**. Industry teams ship (1) the shell + night-critical UI, (2) a thin API + usage log, (3) agent channels with a router table, (4) Studio/sim as a later pane. One control plane is the right north star; one mega-app on day one is not.

---

## 2. Industry pattern map (name the patterns)

| Our idea | Known-good pattern | Reference shape |
|---|---|---|
| One desktop + web ops UI | **BFF + desktop shell** (Electron/Tauri wraps web UI) | Discord, VS Code, Figma desktop |
| Channel list of crew + bots | **Team chat rooms with bot members** | Discord/Slack channels; bots are first-class participants |
| Prompt/form bots by area | **Role-routed multi-agent orchestration** | Orchestrator + specialist workers (already `orch/`) |
| Usage metering + live agent status | **Agent / LLM observability control plane** | LangSmith, Helicone, OpenAI usage dashboards |
| Muse / Room Studio live + sims | **Digital twin + parameter panel** | Unreal/Unity twin UIs; we use three.js Studio |
| Side-by-side “IDE + agent” vs separate console | **Cursor = IDE+agent; MOTION Ops = separate ops console** | Keep Cursor for building code; Ops for crew night + bot ops — don’t clone Cursor inside Ops |
| Multi-model routing | **Router table (area → model/provider)** | Not “fan-out every model on every click” (anti-pattern: N+1 LLM calls) |

---

## 3. Industry-standard stack recommendation (concrete)

Approved target stack for builders (also in root / `services/api` `ARCHITECTURE.md`):

| Layer | Standard choice | Why |
|---|---|---|
| UI | **TypeScript · Next.js (App Router) · React** in `apps/ops-panel` | Real component tree, typed data, testable; matches in-flight panel |
| Desktop | **Electron shell** in `desktop/` (already shipped) | Discord/VS Code pattern; thin host, loads web UI |
| Night-Of fallback | Keep static **`ops/`** PWA | Offline phones; zero Node on crew Wi‑Fi |
| Backend / BFF | **Python FastAPI** in `services/api` | Aligns with hub/studio Python; one place for keys, routing, jobs |
| Persistence (MVP) | **SQLite** (usage events, job rows, session meta) | Zero ops burden for a six-person crew |
| Sims / long work | **Job queue** (DB-backed jobs table + worker process; RQ/Arq later if needed) | Don’t block HTTP on Studio Monte Carlo |
| Secrets | **Server-only `.env`**, never in client bundles or git | Industry default |
| Auth | **Later** (local-trusted MVP); add when anything leaves the laptop | Don’t block Oct 30 on OAuth |

**Explicit non-goals for MVP:** rewrite `hub.py` into the BFF; replace Room Studio with a new engine; multi-tenant cloud; CapCut-in-the-browser; calling every model on every UI click.

---

## 4. What’s already standard vs amateur / risky

### Already standard (keep)
- **Electron host + web UI target resolver** (`desktop/`) — correct BFF/shell split.
- **Offline-first Night-Of** (`ops/` + SW + localStorage, pass numbers only) — right for event night.
- **File-protocol orchestration** (`orch/` inbox/outbox) — honest multi-agent coordination without fake “autonomous swarm.”
- **Labeled numbers** + no venue address / no guest PII in shipped ops seeds — privacy-correct.
- **In-flight Next panel** with typed `ops-data` / check-in hooks — right direction (even while `page.tsx` is still create-next-app chrome).

### Amateur / risky (steer away)
- **Single giant HTML artifacts as the long-term product** (`web/index.html`, Studio one-file) — fine as creative tools; bad as the only control plane (no typed API, hard tests, key leakage risk if someone “just fetch” from the page).
- **`hub.py` as the runtime backend** — great CLI catalog/learning loop; **not** an HTTP control plane. Don’t bolt sockets onto the menu script; grow FastAPI beside it and call shared libs later.
- **Empty `services/api` + Next default landing** — fine WIP; risk is shipping nav chrome (“Claude / Library”) with no BFF contract → UI invents APIs, agents diverge.
- **Live-editing Studio + running sims inside the Electron renderer** — digital-twin UI is fine; **heavy sims must be jobs on the Python side**, not `while(true)` in the browser tab.
- **Per-click multi-model fan-out** — cost and latency blow up; use a **router table**.
- **Usage “live view” of every agent with no event schema** — without a single `usage_events` / `agent_runs` table, dashboards become screenshots and lies.
- **Building a second Cursor** inside Ops — kill. Ops = crew + bot rooms + night dashboards; code stays in Cursor/Claude Code.

---

## 5. Security / privacy standards (non-negotiable)

1. **No guest PII** in git, client logs, analytics, or usage rows (pass numbers OK; names/phones/emails never).
2. **No venue address** in any client bundle, log line, screenshot fixture, or model prompt that might be pasted into chats.
3. **API keys server-only** (FastAPI / `.env`); renderer and Next public env get **zero** provider secrets.
4. **Auth later** — local MVP assumes trusted crew machine; before any hosted URL: session auth + least privilege.
5. **Draft only** — no spend/send/post from the app; any “send” action stays stubbed until Jovanni OK.
6. **Usage logs store:** bot id, area, model id, token/char counts, latency, status — **not** raw prompts that contain private guest or address material. Redact or hash if prompts are retained.
7. **Desktop** loads `http://127.0.0.1` / localhost targets; don’t enable remote `MOTION_OPS_URL` to untrusted hosts with nodeIntegration.

---

## 6. Multi-model efficiency — router table (not N+1)

```
area            → default_model     → fallback        → max_parallel
night_ops       → local/rules       → cheap-small     → 1
copy            → mid-chat          → mid-chat        → 1
studio_sim      → (no LLM; job)     → —               → 1 worker
code            → (Cursor seat)     → —               → 0 in-app
research        → long-context      → mid             → 1
```

Rules for builders:
- **One route resolution per user action** (read table → one primary call). Fallbacks only on failure, not in parallel “for quality.”
- **No** “ask Claude + GPT + Gemini and vote” on MVP clicks.
- Meter **every** routed call into SQLite (`usage_events`).
- Live view = subscribe/poll **run status** for open runs, not re-invoke models to refresh the dashboard.

---

## 7. MVP vs later (so it isn’t vapor)

### Must ship first (MVP — “real product”)
1. **Night-Of** working on phone (`ops/`) **and** inside desktop/panel (same data semantics).
2. **Electron shell** stable (already) loading panel or `ops/`.
3. **FastAPI BFF skeleton:** health, read ops seed, append usage event, list agent run status (even if runs are stubs).
4. **Agent workspace v0:** channel list by area (copy / night / studio / money) + one bot thread UI that calls BFF (not provider keys in browser).
5. **Router table** config file + metering rows.

### Later (post–Oct 30 or after MVP feels real)
- Live Muse/Room Studio embed with parameter UI + **job-queued** sims.
- Rich observability (token charts, cost rollups — Helicone-like).
- Multi-user auth / hosted deploy.
- Deep hub.py merge (registry/search inside panel).
- Fancy Discord pixel-perfect UX (voice, reactions, etc.) — pure sugar.

---

## 8. Go / adjust / kill (by major feature)

| Feature | Call | Why |
|---|---|---|
| Discord-like desktop + website ops UI | **GO** | Standard shell pattern; desktop already landed. |
| Dedicated Python backend (FastAPI BFF) | **GO** | Required for keys, metering, jobs; start thin. |
| Agent workspace (bots by area, prompt/form) | **GO (MVP thin)** | Channels + one form → one routed call. |
| Usage metering + live “what is agent doing” | **GO (schema first)** | Industry control-plane core; stub runs OK. |
| Multi-model routing | **ADJUST** | Router table only; no ensemble fan-out. |
| Night-Of ops + dashboards | **GO (priority #1)** | Event-critical; already has a working local app. |
| Live edit Muse/Room Studio + run sims | **ADJUST → later pane** | Keep Studio; drive sims via **jobs**, not renderer loops; don’t block MVP. |
| “One control plane” vision | **GO as north star** | Sequence features; don’t ship all surfaces at once. |
| Replacing Cursor with in-app coding agent IDE | **KILL** | Wrong product; use Cursor/Claude Code for code. |
| Rewriting hub.py into the panel | **KILL / defer** | Keep CLI; BFF can shell out or import later. |
| Hosting / public URL before auth | **KILL** | Local/trusted only until auth exists. |

---

## 9. Minimum steering applied (this task)

- `ARCHITECTURE.md` (repo root) — ≤1 page approved standard for builders on the ops-software line.
- `services/api/ARCHITECTURE.md` — pointer + BFF constraints (backend root).
- Short constraint block appended to root `AGENTS.md` under MOTION Ops.
- **No** app rewrite; other agents keep building against this steer.

---

## 10. Proposed SoT changes
None. Optional later: SoT pointer to `ARCHITECTURE.md` as the ops software standard once Jovanni accepts.

## Questions for Jovanni
1. OK to treat **Oct 30 Night-Of + desktop + thin BFF + one bot channel** as the only MVP bar (Studio live-edit after the event)?
2. Prefer **SQLite on the crew laptop** for usage/jobs, or is “JSON files under `data/`” enough for v0? (Review recommends SQLite.)
3. Product name on the shell: keep **MOTION Ops** (T-012 open question)?
