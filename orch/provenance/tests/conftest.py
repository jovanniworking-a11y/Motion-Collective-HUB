# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_054e72e5eb3c4299]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from provenance import AgentIdentity  # noqa: E402


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    return tmp_path


@pytest.fixture
def me() -> AgentIdentity:
    return AgentIdentity(agent_id="test-agent", role="backend-builder", session_id="sess_test")
