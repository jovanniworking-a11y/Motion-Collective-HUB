# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_73de2baf34f44069]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""The four limits turned into checks: remote leases, guest-name denylist, coverage gate, agent registry."""
from __future__ import annotations

import json
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from provenance import (
    LeaseConflict,
    LeaseServiceError,
    Ledger,
    Registry,
    RemoteLeaseManager,
    changed_files,
    check_coverage,
    find_guest_names,
    track_agent_work,
)
from provenance.__main__ import main as cli
from provenance.models import WorkSummary
from provenance.privacy import write_denylist

TOKEN = "k" * 40


# ---------------------------------------------------------------- remote leases (fake of /api/agentops/leases)
class _FakeLeaseAPI(BaseHTTPRequestHandler):
    leases: dict = {}

    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def _auth(self):
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            self._send(401, {"detail": "agent token required"}); return False
        return True

    def do_GET(self):
        if self._auth():
            self._send(200, {"leases": [l for l in self.leases.values() if l["expires_at"] > time.time()]})

    def do_POST(self):
        if not self._auth():
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        op, now, cur = self.path.rsplit("/", 1)[-1], time.time(), self.leases.get(body["resource"])
        if op == "acquire":
            if cur and cur["expires_at"] > now and cur["owner"] != body["owner"]:
                return self._send(409, {"detail": f"{body['resource']} is leased by {cur['owner']}"})
            lease = {"resource": body["resource"], "owner": body["owner"], "lease_id": f"ls_{len(self.leases)}{int(now*1e6)%10**6}",
                     "acquired_at": now, "expires_at": now + body["ttl"], "ttl": body["ttl"]}
            self.leases[body["resource"]] = lease
            return self._send(200, {"lease": lease})
        if not cur or cur["lease_id"] != body["lease_id"]:
            return self._send(409, {"detail": "lease lost"}) if op == "heartbeat" else self._send(200, {"released": False})
        if op == "heartbeat":
            cur["expires_at"] = now + cur["ttl"]; return self._send(200, {"lease": cur})
        del self.leases[body["resource"]]; return self._send(200, {"released": True})


@pytest.fixture
def lease_api():
    _FakeLeaseAPI.leases = {}
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _FakeLeaseAPI)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_remote_leases_block_a_second_machine(lease_api):
    a, b = RemoteLeaseManager(lease_api, TOKEN), RemoteLeaseManager(lease_api, TOKEN)
    with a.held("live-ops/fader/server.py", "grok-jerry", ttl=30):
        with pytest.raises(LeaseConflict, match="grok-jerry"):
            b.acquire("live-ops/fader/server.py", "cursor", ttl=30)
        assert b.holder("live-ops/fader/server.py").owner == "grok-jerry"
    assert b.holder("live-ops/fader/server.py") is None
    with pytest.raises(LeaseServiceError, match="401"):
        RemoteLeaseManager(lease_api, "wrong").acquire("x", "cursor")


def test_tracker_uses_remote_leases_when_configured(repo, me, lease_api, monkeypatch):
    monkeypatch.setenv("MOTION_LEASE_URL", lease_api)
    monkeypatch.setenv("MOTION_AGENT_TOKEN", TOKEN)
    (repo / "a.py").write_text("x = 1\n")
    other = RemoteLeaseManager(lease_api, TOKEN).acquire("a.py", "cursor", ttl=60)
    with pytest.raises(LeaseConflict):
        with track_agent_work("a.py", agent=me, intent="edit while leased", repo_root=repo):
            pass
    RemoteLeaseManager(lease_api, TOKEN).release(other)
    with track_agent_work("a.py", agent=me, intent="edit after release", repo_root=repo):
        (repo / "a.py").write_text("x = 2\n")
    assert not (repo / ".agent" / "leases").exists() or not any((repo / ".agent" / "leases").iterdir())


def test_unreachable_lease_service_fails_closed(repo, me, monkeypatch):
    monkeypatch.setenv("MOTION_LEASE_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("MOTION_AGENT_TOKEN", TOKEN)
    (repo / "a.py").write_text("x = 1\n")
    with pytest.raises(LeaseServiceError):
        with track_agent_work("a.py", agent=me, intent="no lease, no write", repo_root=repo):
            (repo / "a.py").write_text("x = 2\n")
    assert (repo / "a.py").read_text() == "x = 1\n"


# ---------------------------------------------------------------- guest-name denylist
def test_denylist_blocks_names_in_stamps(repo, monkeypatch):
    monkeypatch.chdir(repo)
    write_denylist(["Zelda Quintanilla", "Xochiquetzal"], repo)
    assert find_guest_names("checked in zelda  quintanilla".replace("  ", " ")) == ["zelda quintanilla"]
    assert find_guest_names("Xochiquetzal brought 3") == ["Xochiquetzal"]
    assert find_guest_names("Zelda alone is fine") == []
    with pytest.raises(ValueError, match="guest denylist"):
        WorkSummary(intent="Comp list: add Zelda Quintanilla", verification_status="unverified")
    monkeypatch.setenv("GUEST_DENYLIST", "Ignatius Fernwood")
    assert find_guest_names("hi Ignatius Fernwood") == ["Ignatius Fernwood"]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


@pytest.fixture
def gitrepo(tmp_path: Path, monkeypatch) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@example.invalid"); _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("# r\n")
    _git(tmp_path, "add", "."); _git(tmp_path, "commit", "-qm", "init")
    _git(tmp_path, "checkout", "-qb", "cursor/feature")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_scan_staged_blocks_guest_names(gitrepo):
    write_denylist(["Zelda Quintanilla"], gitrepo)
    (gitrepo / "notes.md").write_text("VIP: Zelda Quintanilla\n")
    _git(gitrepo, "add", "notes.md")
    assert cli(["scan-staged"]) == 1
    (gitrepo / "notes.md").write_text("VIP: (see private list)\n")
    _git(gitrepo, "add", "notes.md")
    assert cli(["scan-staged"]) == 0


# ---------------------------------------------------------------- coverage gate + registry
def _registry(repo: Path) -> None:
    (repo / ".agent").mkdir(exist_ok=True)
    (repo / ".agent" / "agents.json").write_text(json.dumps({"agents": [
        {"id": "claude-code", "seat": "cc", "lane": "orchestrator", "owns": ["**"], "branch_prefixes": ["claude/"]},
        {"id": "cursor", "seat": "cursor", "lane": "code", "owns": ["apps/**"], "branch_prefixes": ["cursor/"]},
    ]}))


def test_coverage_catches_unstamped_and_out_of_lane_edits(gitrepo, monkeypatch):
    monkeypatch.delenv("GITHUB_HEAD_REF", raising=False); monkeypatch.delenv("GITHUB_REF_NAME", raising=False)
    _registry(gitrepo)
    (gitrepo / "apps").mkdir(); (gitrepo / "apps" / "x.ts").write_text("export const x = 1;\n")
    (gitrepo / "live.py").write_text("y = 1\n")
    assert changed_files(gitrepo, "main") == ["apps/x.ts", "live.py"]   # .agent/** exempt
    assert cli(["coverage", "--base", "main"]) == 1                      # cursor/ branch: enforced

    base = ["stamp", "--agent-id", "cursor", "--role", "code", "--session", "s1", "--intent", "Feature"]
    assert cli([*base, "--changed", "--base", "main"]) == 0
    rep = check_coverage(gitrepo, changed_files(gitrepo, "main"), Ledger(gitrepo), Registry.load(gitrepo))
    assert rep.uncovered == [] and rep.lane == ["live.py: last stamped by cursor, outside its lane"]

    assert Registry.load(gitrepo).warnings("cursor", "live.py")
    assert "not in" in Registry.load(gitrepo).warnings("mystery-bot", "apps/x.ts")[0]

    # edit outside the protocol -> uncovered again
    (gitrepo / "apps" / "x.ts").write_text("export const x = 2;\n")
    rep = check_coverage(gitrepo, changed_files(gitrepo, "main"), Ledger(gitrepo), Registry.load(gitrepo))
    assert "apps/x.ts" in rep.uncovered

    # a human branch only reports
    _git(gitrepo, "checkout", "-qb", "jovanni/notes")
    assert cli(["coverage", "--base", "main"]) == 0
    assert cli(["coverage", "--base", "main", "--enforce", "always"]) == 1


# ---------------------------------------------------------------- docs that show example blocks keep them
def test_examples_of_breadcrumbs_survive_stamping(repo, me):
    doc = ("# Guide\n```\n# @agent-provenance [t] [agent:x] [status:completed/unverified] [trace:tr_x]\n# @summary: demo\n```\n"
           "```\n<!-- AGENT_WORKLOG:BEGIN -->\n| UTC | Agent |\n<!-- AGENT_WORKLOG:END -->\n```\nTail.\n")
    (repo / "guide.md").write_text(doc)
    for n in (1, 2):
        with track_agent_work("guide.md", agent=me, intent=f"touch {n}", repo_root=repo):
            pass
    text = (repo / "guide.md").read_text()
    assert text.startswith(doc.rstrip("\n")) and text.count("#### Agent work log") == 1
    assert "touch 2" in text and "touch 1" in text
