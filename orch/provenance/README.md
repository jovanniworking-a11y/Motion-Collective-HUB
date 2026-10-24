# Agent provenance · quick start
Read before write, stamp on exit. Design: [ARCHITECTURE.md](ARCHITECTURE.md) · worker prompt: [WORKER_PROMPT.md](WORKER_PROMPT.md) · schemas: [schema/](schema/)

```bash
# what happened to this file before me?
python3 orch/provenance/agent.py hydrate apps/ops-panel/src/lib/api.ts

# I edited it; record the work (verification runs first)
python3 orch/provenance/agent.py stamp --target apps/ops-panel/src/lib/api.ts --agent-id cursor --role frontend \
  --session s1 --intent "Same-origin API base" --action "apiBase() returns '' in the browser" \
  --verify "npm --prefix apps/ops-panel run -s typecheck" --next "Re-run e2e after the next deploy"

python3 orch/provenance/agent.py trailers <trace_id>    # paste into the commit message
python3 orch/provenance/agent.py verify-chain           # ledger integrity (CI runs this)
python3 orch/provenance/agent.py state                  # .agent/STATE.md rolling summary
python3 orch/provenance/agent.py approve <key> --by jovanni --scope "…"   # humans only: unlocks one external side effect

python3 orch/provenance/agent.py coverage --base origin/main   # every changed file has a current stamp (CI enforces on agent branches)
python3 orch/provenance/agent.py stamp --changed --base origin/main --agent-id cursor --role frontend \
  --session s1 --intent "Activity page" --verify "npm --prefix apps/ops-panel run -s typecheck"   # stamp the whole change set
python3 orch/provenance/agent.py denylist --stdin < names.txt   # private guest names (gitignored); `denylist` alone prints the count
python3 orch/provenance/agent.py mirror --url "$MOTION_API_URL" # copy ledger stamps to the shared DB (CI does this when secrets exist)
```

Cross-machine leases: `export MOTION_LEASE_URL=https://<panel host> MOTION_AGENT_TOKEN=<32+ chars>`. Lanes live in `.agent/agents.json`.

```python
import sys; sys.path.insert(0, "orch/provenance")
from provenance import AgentIdentity, track_agent_work

me = AgentIdentity(agent_id="claude-code", role="orchestrator", session_id="sess_…")
with track_agent_work("orch/tasks/BOARD.md", agent=me, intent="Update the RSVP line",
                      verify=["python3 orch/hygiene/scan.py"], idempotency_key="rsvp-2026-10-24") as work:
    if not work.already_done:
        print(work.briefing.to_prompt())
        ...  # edit
        work.action("RSVPs 20 → 22"); work.next("Re-pull Tally tomorrow 8:52")
```

Hooks (per clone): `ln -s ../../orch/provenance/hooks/commit-msg .git/hooks/commit-msg` and `ln -s ../../orch/provenance/hooks/pre-commit .git/hooks/pre-commit` (blocks denylisted guest names in staged lines).

<!-- AGENT_WORKLOG:BEGIN -->
<!-- AGENT_LOG {"v":"1.0","ts":"2026-10-24T21:05:00.005Z","agent":"claude-code","trace":"tr_a39bfa1af0954c20","status":"completed","verify":"verified_passed","hash":"sha256:3c82fcfaa9b457413a816a2d957c74708a582ec614f835e33e0fa4245155e601","ledger":".agent/ledger.jsonl"} -->

#### Agent work log
| UTC | Agent | Status | Summary | Next | Trace |
|---|---|---|---|---|---|
| 2026-10-24T21:05:00Z | claude-code | completed / verified_passed | Close the four provenance limits: shared leases, guest denylist, coverage gate, agent reg… | Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION… | `tr_a39bfa1af0954c20` |
<!-- AGENT_WORKLOG:END -->
