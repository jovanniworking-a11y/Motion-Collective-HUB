# @agent-provenance [2026-10-24T21:05:00Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_2691f785a6e44d94]
# @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
# @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"""Leases held in the shared database through the API (`/api/agentops/leases/*`).

Same interface as LeaseManager, so `held()` (heartbeat thread, release on exit) works unchanged.
Set MOTION_LEASE_URL (the API origin) and MOTION_AGENT_TOKEN and every tracker/CLI on every machine
uses one lease table. Unset, leases stay file-based (one host).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from .hashing import file_content_hash
from .leases import Lease, LeaseConflict, LeaseManager, StaleWrite


class LeaseServiceError(RuntimeError):
    """The lease service could not be reached or rejected the token. Fail closed: no lease, no write."""


class RemoteLeaseManager(LeaseManager):
    def __init__(self, base_url: str, token: str, timeout: float = 10.0):
        self.base = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _call(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        req = urllib.request.Request(
            f"{self.base}/api/agentops/leases{path}", method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                return json.loads(res.read() or b"{}")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            if exc.code == 409:
                raise LeaseConflict(json.loads(detail).get("detail", detail) if detail.startswith("{") else detail) from exc
            raise LeaseServiceError(f"lease service {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LeaseServiceError(f"lease service unreachable: {exc}") from exc

    def acquire(self, resource: str, owner: str, ttl: float = 900.0, *,
                expected_hash: Optional[str] = None, file_path: Optional[Path] = None) -> Lease:
        if expected_hash is not None and file_path is not None and file_content_hash(file_path) != expected_hash:
            raise StaleWrite(f"{resource} changed since it was read")
        return Lease(**self._call("POST", "/acquire", {"resource": resource, "owner": owner, "ttl": ttl})["lease"])

    def heartbeat(self, lease: Lease) -> Lease:
        return Lease(**self._call("POST", "/heartbeat", {"resource": lease.resource, "lease_id": lease.lease_id})["lease"])

    def release(self, lease: Lease) -> None:
        self._call("POST", "/release", {"resource": lease.resource, "lease_id": lease.lease_id})

    def holder(self, resource: str) -> Optional[Lease]:
        for row in self._call("GET", "")["leases"]:
            if row["resource"] == resource:
                return Lease(**row)
        return None


def lease_manager_for(root: Path) -> LeaseManager:
    url, token = os.environ.get("MOTION_LEASE_URL", ""), os.environ.get("MOTION_AGENT_TOKEN", "")
    if url:
        if not token:
            raise LeaseServiceError("MOTION_LEASE_URL is set but MOTION_AGENT_TOKEN is not")
        return RemoteLeaseManager(url, token)
    return LeaseManager(root)
