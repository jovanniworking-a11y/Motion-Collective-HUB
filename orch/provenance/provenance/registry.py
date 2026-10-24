# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_6cc66ecf4bba4ed1]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Agent registry (`.agent/agents.json`): who each agent is and which files its lane owns.

Replaces the empty `agent.model` field as the identity record (no model ids in pushed artifacts).
Lane rule: an agent may write a file only if one of its `owns` globs matches. The orchestrator owns
`**` and reviews everything. Unregistered agents can still stamp, with a warning.
"""
from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

REGISTRY_REL = Path(".agent/agents.json")


@dataclass
class AgentEntry:
    id: str
    seat: str
    lane: str
    owns: list[str] = field(default_factory=list)
    max_tier: str = "mutate_shared"
    branch_prefixes: list[str] = field(default_factory=list)


def _match(path: str, glob: str) -> bool:
    if glob == "**":
        return True
    if glob.endswith("/**"):
        return path == glob[:-3] or path.startswith(glob[:-2])
    return fnmatch.fnmatchcase(path, glob)


class Registry:
    def __init__(self, entries: list[AgentEntry]):
        self.entries = {e.id: e for e in entries}

    @classmethod
    def load(cls, root: Path) -> "Registry":
        p = Path(root) / REGISTRY_REL
        if not p.exists():
            return cls([])
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls([AgentEntry(**a) for a in data["agents"]])

    def get(self, agent_id: str) -> Optional[AgentEntry]:
        return self.entries.get(agent_id)

    def may_write(self, agent_id: str, path: str) -> bool:
        e = self.get(agent_id)
        return bool(e and any(_match(path, g) for g in e.owns))

    def lane_owners(self, path: str) -> list[str]:
        """Agents whose lane names this file specifically (orchestrator `**` excluded)."""
        return [e.id for e in self.entries.values() if any(g != "**" and _match(path, g) for g in e.owns)]

    def agent_for_branch(self, branch: str) -> Optional[str]:
        for e in self.entries.values():
            if any(branch.startswith(p) for p in e.branch_prefixes):
                return e.id
        return None

    def warnings(self, agent_id: str, path: str) -> list[str]:
        if not self.entries:
            return []
        if agent_id not in self.entries:
            return [f"{agent_id} is not in {REGISTRY_REL}; add it so its lane can be checked"]
        if not self.may_write(agent_id, path):
            owners = ", ".join(self.lane_owners(path)) or "the orchestrator"
            return [f"{path} is outside {agent_id}'s lane (owned by {owners})"]
        return []
