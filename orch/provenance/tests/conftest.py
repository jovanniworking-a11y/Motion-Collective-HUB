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
