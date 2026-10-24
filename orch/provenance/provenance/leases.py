"""Time-bounded resource leases with heartbeats and optimistic concurrency (ETag = content hash).

Leases live in `.agent/leases/<sha1(resource)>.json`. Acquisition is atomic (O_EXCL create);
an expired lease can be taken over. While held, a background heartbeat extends the expiry.
Scope: one host or a shared filesystem. Across machines, agents coordinate through git branches
plus the ledger; a Postgres-backed lease table is the drop-in for a shared server (see ARCHITECTURE.md).
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, Optional

from .hashing import file_content_hash


class LeaseConflict(RuntimeError):
    """Another agent holds an unexpired lease on the resource."""


class StaleWrite(RuntimeError):
    """Optimistic-concurrency failure: the resource changed since the caller read it."""


@dataclass
class Lease:
    resource: str
    owner: str
    lease_id: str
    acquired_at: float
    expires_at: float
    ttl: float

    @property
    def expired(self) -> bool:
        return time.time() >= self.expires_at


class LeaseManager:
    def __init__(self, root: Path):
        self.dir = Path(root) / ".agent" / "leases"
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, resource: str) -> Path:
        return self.dir / (hashlib.sha1(resource.encode()).hexdigest() + ".json")

    def _read(self, resource: str) -> Optional[Lease]:
        try:
            return Lease(**json.loads(self._path(resource).read_text()))
        except FileNotFoundError:
            return None
        except (ValueError, TypeError):
            return None  # corrupt lease file: treat as absent

    def _write_atomic(self, lease: Lease) -> None:
        tmp = self._path(lease.resource).with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
        tmp.write_text(json.dumps(asdict(lease)))
        os.replace(tmp, self._path(lease.resource))

    def acquire(self, resource: str, owner: str, ttl: float = 900.0, *,
                expected_hash: Optional[str] = None, file_path: Optional[Path] = None) -> Lease:
        if expected_hash is not None and file_path is not None:
            current = file_content_hash(file_path)
            if current != expected_hash:
                raise StaleWrite(f"{resource} changed since it was read (expected {expected_hash[:19]}…, now {str(current)[:19]}…)")
        now = time.time()
        lease = Lease(resource, owner, f"ls_{os.urandom(6).hex()}", now, now + ttl, ttl)
        p = self._path(resource)
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as fh:
                fh.write(json.dumps(asdict(lease)))
            return lease
        except FileExistsError:
            held = self._read(resource)
            if held and not held.expired and held.owner != owner:
                raise LeaseConflict(f"{resource} is leased by {held.owner} until {time.strftime('%H:%M:%S', time.gmtime(held.expires_at))}Z")
            # expired, corrupt, or ours: take it over, then confirm we won any race
            self._write_atomic(lease)
            if (cur := self._read(resource)) is None or cur.lease_id != lease.lease_id:
                raise LeaseConflict(f"lost the takeover race for {resource}")
            return lease

    def heartbeat(self, lease: Lease) -> Lease:
        cur = self._read(lease.resource)
        if cur is None or cur.lease_id != lease.lease_id:
            raise LeaseConflict(f"lease on {lease.resource} was lost (taken over after expiry)")
        cur.expires_at = time.time() + cur.ttl
        self._write_atomic(cur)
        return cur

    def release(self, lease: Lease) -> None:
        cur = self._read(lease.resource)
        if cur is not None and cur.lease_id == lease.lease_id:
            self._path(lease.resource).unlink(missing_ok=True)

    def holder(self, resource: str) -> Optional[Lease]:
        cur = self._read(resource)
        return cur if cur and not cur.expired else None

    @contextmanager
    def held(self, resource: str, owner: str, ttl: float = 900.0, *,
             heartbeat_every: Optional[float] = None, expected_hash: Optional[str] = None,
             file_path: Optional[Path] = None) -> Iterator[Lease]:
        lease = self.acquire(resource, owner, ttl, expected_hash=expected_hash, file_path=file_path)
        stop = threading.Event()
        lost: list[BaseException] = []

        def beat() -> None:
            interval = heartbeat_every or max(1.0, ttl / 3)
            while not stop.wait(interval):
                try:
                    self.heartbeat(lease)
                except LeaseConflict as exc:
                    lost.append(exc)
                    return

        t = threading.Thread(target=beat, daemon=True)
        t.start()
        try:
            yield lease
            if lost:
                raise lost[0]
        finally:
            stop.set()
            t.join(timeout=2)
            self.release(lease)
