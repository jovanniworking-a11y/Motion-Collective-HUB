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
```

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

Commit-msg hook (optional, per clone): `ln -s ../../orch/provenance/hooks/commit-msg .git/hooks/commit-msg`.
