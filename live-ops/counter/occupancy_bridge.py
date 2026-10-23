#!/usr/bin/env python3
"""occupancy_bridge.py: counts.jsonl (zone_counter.py --zones-file) -> POST /api/data/occupancy.

FORGE lane, Devil's Night / AFTERIMAGE 001. Stdlib only (urllib, threading), no new deps, $0.

    MOTION_DB_LOCAL=1 python occupancy_bridge.py --counts counts.jsonl

Every --interval seconds (default 5) the main thread reads any new lines of counts.jsonl (tail,
incremental; newest valid line wins; malformed / half-written lines are skipped; missing,
truncated and rotated files are handled), builds ONE payload and hands it to a sender thread:

    {"ts": <now, unix s>, "zones": {"living_room": int|null, "dance_floor": ..., "kitchen_bar": ...,
     "hallway": ..., "balcony": ...}, "total": int|null}          (+ "source_ts" with the flag)

Rules (never invent numbers):
  * zones: always the 5 canonical keys. A value that is null, missing (zone not covered by this
    camera) or not a non-negative integer is sent as null. Unknown zone ids are dropped.
  * total: the line's "total" if the key is present (null stays null). If absent, computed as
    living_room + kitchen_bar + hallway + balcony (dance_floor is INSIDE living_room, never added),
    and null unless ALL four are known: a partial sum would look like a real headcount and
    understate the house (same rule as zone_counter.py's own total).
  * stale: if the newest line is older than --stale-after (default 15 s), or no line has been
    read yet, the payload is still sent (it is the heartbeat) but with every zone null and total
    null, so nothing downstream can show old numbers as live.

Sending never blocks counting: zone_counter.py is a separate process (it only appends to the
file), and here the HTTP work runs in its own thread with a short --timeout; the tick loop only
appends to an in-memory queue. Failures:
  * connection error / timeout / 5xx / 408 / 429 -> keep the payload in the queue (persisted to
    the --spool JSONL file, default bridge_buffer.jsonl next to this script), retry the oldest
    with backoff 2,4,8,16,32,32.. s x jitter 0.5-1.5 (never gives up), then flush oldest-first,
    stopping at the first failure so order is preserved.
  * 400 / other 4xx / 3xx (wrong URL) -> NOT retried and NOT silently dropped: appended to the
    dead-letter JSONL (default bridge_dead_letter.jsonl next to this script) with the response
    detail, plus loud "[BRIDGE] ... OPERATOR ACTION" lines on stderr.
  --preflight sends ONE POST of the newest counts line, prints request/status/response, exits 0
  on 2xx (night-of check before doors). post_frame() is a non-blocking version of the patch's
  helper for other callers.
  * queue bounded (--max-spool, default 2000 = ~2.8 h at 5 s); when full the oldest is dropped
    with a warning.
One stderr line per POST attempt (status, latency ms, queue depth). Ctrl-C/SIGTERM: stop,
persist the queue to the spool, print stats. On start an existing spool is loaded and flushed.
"""
from __future__ import annotations

import argparse
import collections
import json
import logging
import math
import os
import random
import signal
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

log = logging.getLogger("occupancy_bridge")

ZONES = ("living_room", "dance_floor", "kitchen_bar", "hallway", "balcony")
TOP_LEVEL = ("living_room", "kitchen_bar", "hallway", "balcony")   # dance_floor is inside living_room
DEFAULT_LOCAL_URL = "http://localhost:3000/api/data/occupancy"
TAIL_START_BYTES = 64 * 1024        # on open, only look at the last 64 KB for the newest line
MAX_READ_PER_POLL = 4 * 1024 * 1024  # cap one poll's read; later polls continue
RETRY_STATUSES = {408, 429}
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SPOOL = os.path.join(SCRIPT_DIR, "bridge_buffer.jsonl")
DEFAULT_DEAD_LETTER = os.path.join(SCRIPT_DIR, "bridge_dead_letter.jsonl")
# retry schedule from PATCH_bridge-retry_2026-10-22: base 2 s doubling 2,4,8,16,32 then stays at
# 32; each delay x uniform(0.5, 1.5) jitter; BACKOFF_MAX = 60 is the absolute ceiling after jitter.
BACKOFF_BASE = 2.0
BACKOFF_STEPS = 5            # 2 * 2**(5-1) = 32 s is the last doubling
BACKOFF_MAX = 60.0
JITTER = (0.5, 1.5)
DETAIL_CHARS = 500


# ------------------------------------------------------------------ URL selection
class ConfigError(Exception):
    pass


def select_url(cli_url: Optional[str], env: Optional[dict] = None) -> tuple[str, str]:
    """Return (url, mode). MOTION_DB_LOCAL=1 always wins (show-night switch): MOTION_LOCAL_URL or
    http://localhost:3000/api/data/occupancy. Otherwise --url, else MOTION_API_URL, else error."""
    env = os.environ if env is None else env
    if str(env.get("MOTION_DB_LOCAL", "")).strip().lower() in ("1", "true", "yes", "on"):
        return (env.get("MOTION_LOCAL_URL") or DEFAULT_LOCAL_URL).strip(), "local"
    url = (cli_url or env.get("MOTION_API_URL") or "").strip()
    if not url:
        raise ConfigError(
            "no endpoint: set MOTION_DB_LOCAL=1 (localhost, show-night default) or give "
            "--url / MOTION_API_URL=https://<vercel-app>/api/data/occupancy")
    if not url.startswith(("http://", "https://")):
        raise ConfigError(f"endpoint must start with http:// or https://, got {url!r}")
    return url, "remote"


# ------------------------------------------------------------------ parsing
def _count(v: Any) -> Optional[int]:
    """A headcount is a non-negative int (3.0 accepted). Anything else -> None (unknown)."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return v if v >= 0 else None
    if isinstance(v, float) and math.isfinite(v) and v >= 0 and v == int(v):
        return int(v)
    return None


def parse_line(raw: str) -> Optional[dict]:
    """One counts.jsonl line -> {"ts", "zones", "total"} (normalised) or None if malformed."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        obj = json.loads(raw)
    except (ValueError, RecursionError):
        return None
    if not isinstance(obj, dict):
        return None
    ts = obj.get("ts")
    if isinstance(ts, bool) or not isinstance(ts, (int, float)) or not math.isfinite(ts) or ts <= 0:
        return None
    zin = obj.get("zones")
    if not isinstance(zin, dict):
        return None
    zones = {}
    for z in ZONES:
        v = zin.get(z)
        if isinstance(v, dict):          # tolerate {"count": n} like the dashboard does
            v = v.get("count")
        zones[z] = _count(v)
    if "total" in obj:
        total = _count(obj["total"])
    else:
        total = compute_total(zones)
    return {"ts": float(ts), "zones": zones, "total": total}


def compute_total(zones: dict) -> Optional[int]:
    vals = [zones.get(z) for z in TOP_LEVEL]
    if any(v is None for v in vals):
        return None
    return int(sum(vals))


def build_payload(newest: Optional[dict], now: float, stale_after: float,
                  include_source_ts: bool = False) -> dict:
    stale = newest is None or (now - newest["ts"]) > stale_after
    if stale:
        zones = {z: None for z in ZONES}
        total = None
    else:
        zones = dict(newest["zones"])
        total = newest["total"]
    p = {"ts": round(now, 3), "zones": zones, "total": total}
    if include_source_ts:
        p["source_ts"] = None if newest is None else round(newest["ts"], 3)
    return p


# ------------------------------------------------------------------ tail reader
class CountsTail:
    """Incremental reader of an append-only JSONL file. Keeps (inode, offset); handles the file
    not existing yet, being deleted, truncated (size < offset) or rotated (new inode). Only
    complete (newline-terminated) lines are parsed; a trailing partial line waits for the next
    poll. The newest valid line wins (by file order, which is time order for zone_counter)."""

    def __init__(self, path: str):
        self.path = path
        self._fh = None
        self._ino = None
        self._off = 0
        self._buf = b""
        self.newest: Optional[dict] = None
        self.lines_ok = 0
        self.lines_bad = 0
        self.reopens = 0
        self._missing_logged = False
        self._ever_opened = False

    def close(self):
        if self._fh:
            try:
                self._fh.close()
            except OSError:
                pass
        self._fh, self._ino, self._off, self._buf = None, None, 0, b""

    def _open(self, st, from_start: bool):
        self.close()
        self._fh = open(self.path, "rb")
        self._ino = (st.st_dev, st.st_ino)
        self._off = 0
        if from_start:
            self.reopens += 1
        elif st.st_size > TAIL_START_BYTES:
            # first open: newest line wins, so skip history; drop the first (partial) line
            self._fh.seek(st.st_size - TAIL_START_BYTES)
            self._fh.readline()
            self._off = self._fh.tell()
        self._ever_opened = True

    def poll(self) -> Optional[dict]:
        """Read whatever is new. Returns the newest valid record seen so far (may be old)."""
        try:
            st = os.stat(self.path)
        except FileNotFoundError:
            if not self._missing_logged:
                log.warning("counts file %s not found yet; sending null heartbeats", self.path)
                self._missing_logged = True
            self.close()
            return self.newest
        except OSError as exc:
            log.warning("stat %s failed: %s", self.path, exc)
            return self.newest
        self._missing_logged = False
        try:
            ident = (st.st_dev, st.st_ino)
            if self._fh is None:
                if self._ever_opened:
                    log.info("counts file (re)appeared; reading it from the start")
                self._open(st, from_start=self._ever_opened)
            elif ident != self._ino:
                log.info("counts file rotated/replaced; reading the new file from the start")
                self._open(st, from_start=True)
            elif st.st_size < self._off:
                log.info("counts file truncated (%d < %d); reading from the start", st.st_size, self._off)
                self._off, self._buf = 0, b""
                self.reopens += 1
            if st.st_size > self._off:
                self._fh.seek(self._off)
                data = self._fh.read(min(st.st_size - self._off, MAX_READ_PER_POLL))
                self._off += len(data)
                self._consume(data)
        except OSError as exc:
            log.warning("reading %s failed: %s", self.path, exc)
            self.close()
        return self.newest

    def _consume(self, data: bytes):
        self._buf += data
        *lines, self._buf = self._buf.split(b"\n")
        if len(self._buf) > 1024 * 1024:     # a runaway line with no newline: drop it
            self._buf = b""
            self.lines_bad += 1
        for raw in lines:
            if not raw.strip():
                continue
            rec = parse_line(raw.decode("utf-8", "replace"))
            if rec is None:
                self.lines_bad += 1
                if self.lines_bad <= 5 or self.lines_bad % 100 == 0:
                    log.warning("skipped malformed line #%d: %.80r", self.lines_bad, raw)
                continue
            self.lines_ok += 1
            self.newest = rec


# ------------------------------------------------------------------ spool + sender
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):   # a redirected POST means a wrong URL; surface it
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def post_json(url: str, payload: dict, timeout: float, token: Optional[str] = None):
    """Return (status or None, body text, latency ms, error text or None)."""
    data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "forge-occupancy-bridge/1")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    t0 = time.monotonic()
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            body = resp.read(65536).decode("utf-8", "replace")
            return resp.status, body, (time.monotonic() - t0) * 1000, None
    except urllib.error.HTTPError as e:
        try:
            body = e.read(65536).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body, (time.monotonic() - t0) * 1000, None
    except Exception as e:   # URLError, timeout, ConnectionError, RemoteDisconnected...
        return None, "", (time.monotonic() - t0) * 1000, f"{type(e).__name__}: {getattr(e, 'reason', e)}"


def backoff_delay(attempt: int, rng: Optional[random.Random] = None) -> float:
    """Delay before retry number `attempt` (1-based): 2,4,8,16,32,32,... s, each x U(0.5, 1.5),
    never above BACKOFF_MAX. attempt 1 -> [1, 3] s ... attempt >= 5 -> [16, 48] s."""
    rng = rng or random
    base = BACKOFF_BASE * (2 ** (min(max(1, attempt), BACKOFF_STEPS) - 1))
    return min(BACKOFF_MAX, base * rng.uniform(*JITTER))


def is_retryable(status: Optional[int]) -> bool:
    """None = network error / timeout. 5xx, 408 and 429 are transient. Everything else that is
    not 2xx (400, 401, 403, 404, 422, 3xx...) will fail the same way again: dead-letter it."""
    return status is None or status >= 500 or status in RETRY_STATUSES


def alert(msg: str):
    """Loud operator line on stderr, not through logging (no level/time prefix to hide it)."""
    try:
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()
    except Exception:
        pass


class DeadLetter:
    """Append-only JSONL of payloads the endpoint rejected (never retried, never lost)."""

    def __init__(self, path: Optional[str]):
        self.path = path
        self.lock = threading.Lock()
        self.count = 0

    def write(self, payload: dict, status: Optional[int], body: str) -> str:
        detail = (body or "")[:DETAIL_CHARS]
        rec = {"at": round(time.time(), 3), "payload": payload, "status": status, "detail": detail}
        where = self.path or "(no dead-letter file configured)"
        if self.path:
            try:
                with self.lock, open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
                    fh.flush()
            except OSError as exc:
                where = f"{self.path} (WRITE FAILED: {exc}; payload: {json.dumps(payload)})"
        self.count += 1
        alert(f"[BRIDGE] {status} rejected, dead-lettered: {detail}")
        alert(f"[BRIDGE] OPERATOR ACTION: fix payload shape, see {where}")
        return detail


class Sender(threading.Thread):
    def __init__(self, url: str, timeout: float = 3.0, token: Optional[str] = None,
                 spool_path: Optional[str] = None, max_spool: int = 2000,
                 dead_letter_path: Optional[str] = None,
                 backoff: Optional[Callable[[int], float]] = None,
                 rng: Optional[random.Random] = None):
        super().__init__(name="occupancy-sender", daemon=True)
        self.url, self.timeout, self.token = url, timeout, token
        self.spool_path, self.max_spool = spool_path, max(1, int(max_spool))
        self.rng = rng or random.Random()
        self.backoff = backoff or (lambda attempt: backoff_delay(attempt, self.rng))
        self.dead = DeadLetter(dead_letter_path)
        self.q: collections.deque = collections.deque()
        self.lock = threading.Lock()
        self.wake = threading.Event()
        self.stop_ev = threading.Event()
        self.stats = collections.Counter()
        self.last_ok: Optional[tuple] = None      # (payload, status, body)
        self.delays: list = []                    # backoff delays actually used (diagnostics/tests)
        self._dirty = False
        self._in_backoff = False
        self._load_spool()

    # -- queue / spool
    def _load_spool(self):
        if not self.spool_path or not os.path.exists(self.spool_path):
            return
        n = 0
        try:
            with open(self.spool_path, "r", encoding="utf-8") as fh:
                for raw in fh:
                    try:
                        p = json.loads(raw)
                    except ValueError:
                        continue
                    if isinstance(p, dict) and "ts" in p and "zones" in p:
                        self.q.append(p)
                        n += 1
        except OSError as exc:
            log.warning("could not read spool %s: %s", self.spool_path, exc)
        while len(self.q) > self.max_spool:
            self.q.popleft()
            self.stats["dropped_overflow"] += 1
        if n:
            log.info("loaded %d unsent payload(s) from spool %s", len(self.q), self.spool_path)
            self.stats["loaded_from_spool"] = len(self.q)

    def persist(self):
        """Rewrite the spool atomically with what is still queued (delete it when empty)."""
        if not self.spool_path:
            return
        with self.lock:
            items = list(self.q)
            self._dirty = False
        try:
            if not items:
                if os.path.exists(self.spool_path):
                    os.remove(self.spool_path)
                return
            tmp = self.spool_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                for p in items:
                    fh.write(json.dumps(p, separators=(",", ":")) + "\n")
                fh.flush()
                try:
                    os.fsync(fh.fileno())
                except OSError:
                    pass
            os.replace(tmp, self.spool_path)
        except OSError as exc:
            log.warning("spool write failed (%s): %s", self.spool_path, exc)

    def enqueue(self, payload: dict):
        """Never blocks on the network. Called from the tick loop."""
        with self.lock:
            self.q.append(payload)
            self.stats["enqueued"] += 1
            while len(self.q) > self.max_spool:
                old = self.q.popleft()
                self.stats["dropped_overflow"] += 1
                log.warning("queue full (%d): dropped oldest unsent payload ts=%s",
                            self.max_spool, old.get("ts"))
            self._dirty = True
        self.wake.set()

    def depth(self) -> int:
        with self.lock:
            return len(self.q)

    def drain(self, max_wait: float) -> bool:
        """On shutdown: give the thread up to max_wait s to send what is queued (no new retries
        are forced; if the API is down the rest stays in the spool). True if the queue emptied."""
        end = time.monotonic() + max_wait
        while time.monotonic() < end and self.is_alive():
            if self.depth() == 0:
                return True
            if self.stats["failed_attempts"] and self._in_backoff:
                break
            time.sleep(0.05)
        return self.depth() == 0

    # -- thread
    def stop(self):
        self.stop_ev.set()
        self.wake.set()

    def run(self):
        attempt = 0                                # consecutive failures of the head payload
        while not self.stop_ev.is_set():
            with self.lock:
                head = self.q[0] if self.q else None
            if head is None:
                if self._dirty:
                    self.persist()
                self.wake.wait(1.0)
                self.wake.clear()
                continue
            status, body, ms, err = post_json(self.url, head, self.timeout, self.token)
            self.stats["attempts"] += 1
            ok = status is not None and 200 <= status < 300
            retry = not ok and is_retryable(status)
            with self.lock:
                if (ok or not retry) and self.q and self.q[0] is head:
                    self.q.popleft()
                    self._dirty = True
                depth = len(self.q)
            label = str(status) if status is not None else "ERR"
            if ok:
                self.stats["sent"] += 1
                self.last_ok = (head, status, body)
                if attempt:
                    log.info("endpoint back after %d failed attempt(s); flushing %d queued", attempt, depth)
                attempt = 0
                log.info("POST %s %4.0fms q=%d ts=%s total=%s", label, ms, depth, head.get("ts"), head.get("total"))
                if depth == 0 or self._dirty and self.stats["sent"] % 50 == 0:
                    self.persist()
                continue                            # drain backlog oldest-first, no wait
            if not retry:
                self.stats["dead_lettered"] += 1
                log.error("POST %s %4.0fms q=%d REJECTED ts=%s (not retried, dead-lettered)",
                          label, ms, depth, head.get("ts"))
                self.dead.write(head, status, body)
                attempt = 0
                continue
            # transient: keep it at the head (order preserved), back off, retry forever
            self.stats["failed_attempts"] += 1
            attempt += 1
            delay = self.backoff(attempt)
            self.delays.append(delay)
            log.warning("POST %s %4.0fms q=%d retry #%d in %.1fs (%s)", label, ms, depth, attempt,
                        delay, err or f"body={body[:120]!r}")
            if self._dirty:
                self.persist()            # outage: make the queue durable now
            self._in_backoff = True
            self.stop_ev.wait(delay)
            self._in_backoff = False
        self.persist()


# ------------------------------------------------------------------ post_frame (patch API)
_default_senders: dict = {}
_default_lock = threading.Lock()


def _sender_for(url: str, timeout: float) -> "Sender":
    with _default_lock:
        s = _default_senders.get(url)
        if s is None or not s.is_alive():
            s = Sender(url, timeout=timeout, token=os.environ.get("MOTION_API_TOKEN") or None,
                       spool_path=DEFAULT_SPOOL, dead_letter_path=DEFAULT_DEAD_LETTER)
            s.start()
            _default_senders[url] = s
        return s


def post_frame(url: str, payload: dict, timeout: float = 3.0, sender: Optional["Sender"] = None) -> dict:
    """Drop-in for the patch's post_frame(), but NON-BLOCKING on failure: at most one HTTP
    attempt (bounded by `timeout`), never a sleep/retry loop in the caller's thread.
      2xx                     -> {"ok": True, "status": 201, "body": "..."}
      400/other 4xx/3xx       -> dead-lettered + alert -> {"ok": False, "reason": "rejected_400",
                                 "status": <code>, "detail": "<first 500 chars>"}
      network/timeout/5xx/408/429, or a backlog already queued (to keep order)
                              -> queued to the background sender (spool bridge_buffer.jsonl,
                                 retried with backoff) -> {"ok": False, "reason": "buffered",
                                 "status": <code or None>, "detail": "..."}
    "rejected_400" is used for every non-retryable rejection (the patch's contract); check
    "status" for the exact code."""
    s = sender or _sender_for(url, timeout)
    if s.depth():
        s.enqueue(payload)
        return {"ok": False, "reason": "buffered", "status": None,
                "detail": f"backlog of {s.depth()} queued; sent in order by the background sender"}
    status, body, _ms, err = post_json(url, payload, timeout, s.token)
    if status is not None and 200 <= status < 300:
        return {"ok": True, "status": status, "body": body}
    if not is_retryable(status):
        detail = s.dead.write(payload, status, body)
        return {"ok": False, "reason": "rejected_400", "status": status, "detail": detail}
    s.enqueue(payload)
    return {"ok": False, "reason": "buffered", "status": status,
            "detail": err or (body or "")[:DETAIL_CHARS]}


# ------------------------------------------------------------------ main loop
class Bridge:
    def __init__(self, counts_path: str, sender: Sender, interval: float = 5.0,
                 stale_after: float = 15.0, include_source_ts: bool = False):
        self.tail = CountsTail(counts_path)
        self.sender = sender
        self.interval = interval
        self.stale_after = stale_after
        self.include_source_ts = include_source_ts
        self.stop_ev = threading.Event()
        self.tick_times: list[float] = []      # monotonic, for tests/diagnostics
        self.ticks = 0

    def tick(self) -> dict:
        newest = self.tail.poll()
        now = time.time()
        payload = build_payload(newest, now, self.stale_after, self.include_source_ts)
        if newest is not None and now - newest["ts"] > self.stale_after:
            self.sender.stats["stale_ticks"] += 1
        self.sender.enqueue(payload)
        self.ticks += 1
        self.tick_times.append(time.monotonic())
        return payload

    def run(self, duration: float = 0.0, max_ticks: int = 0):
        start = nxt = time.monotonic()
        while not self.stop_ev.is_set():
            self.tick()
            if max_ticks and self.ticks >= max_ticks:
                break
            nxt += self.interval
            now = time.monotonic()
            if nxt < now:                       # fell behind (laptop sleep): skip, don't burst
                nxt = now + self.interval
            if duration and nxt - start > duration:
                break
            self.stop_ev.wait(max(0.0, nxt - now))

    def stop(self):
        self.stop_ev.set()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="counts.jsonl -> POST /api/data/occupancy (stdlib, offline-capable)")
    p.add_argument("--counts", default="counts.jsonl", help="zone_counter.py --zones-file output")
    p.add_argument("--url", help="remote endpoint (ignored when MOTION_DB_LOCAL=1); or MOTION_API_URL")
    p.add_argument("--interval", type=float, default=5.0, help="seconds between POSTs (default 5)")
    p.add_argument("--stale-after", type=float, default=15.0,
                   help="newest line older than this -> send all-null (default 15 s)")
    p.add_argument("--timeout", type=float, default=3.0, help="HTTP timeout per POST (default 3 s)")
    p.add_argument("--spool", default=DEFAULT_SPOOL,
                   help="on-disk queue of unsent payloads (default bridge_buffer.jsonl next to this script)")
    p.add_argument("--dead-letter", default=DEFAULT_DEAD_LETTER,
                   help="JSONL of rejected (4xx/3xx) payloads (default bridge_dead_letter.jsonl next to this script)")
    p.add_argument("--preflight", action="store_true",
                   help="send ONE POST of the newest counts line, print request/response, exit 0 on 2xx")
    p.add_argument("--max-spool", type=int, default=2000, help="queue bound; oldest dropped beyond it")
    p.add_argument("--include-source-ts", action="store_true",
                   help="add source_ts (the counts line's ts); off by default (endpoint allowlist unconfirmed)")
    p.add_argument("--duration", type=float, default=0.0, help="stop after N seconds (0 = forever)")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def preflight(args, url: str, mode: str, token: Optional[str]) -> int:
    """One synchronous POST of the newest counts line. Not buffered (it's a check), but a
    rejection is dead-lettered like any other. Exit 0 on 2xx, 1 on rejection, 3 if unreachable."""
    tail = CountsTail(args.counts)
    newest = tail.poll()
    tail.close()
    now = time.time()
    payload = build_payload(newest, now, args.stale_after, args.include_source_ts)
    if newest is None:
        alert(f"[BRIDGE] PREFLIGHT WARNING: no valid line in {args.counts}; sending an all-null frame")
    elif now - newest["ts"] > args.stale_after:
        alert(f"[BRIDGE] PREFLIGHT WARNING: newest line is {now - newest['ts']:.0f}s old (> "
              f"{args.stale_after:.0f}s): sending all-null. Is zone_counter.py running?")
    body_out = json.dumps(payload, separators=(",", ":"))
    print(f"PREFLIGHT [{mode}] POST {url}", flush=True)
    print(f"REQUEST  {body_out}", flush=True)
    status, body, ms, err = post_json(url, payload, args.timeout, token)
    print(f"STATUS   {status if status is not None else 'ERR'} ({ms:.0f} ms){'  ' + err if err else ''}", flush=True)
    print(f"RESPONSE {body}", flush=True)
    if status is not None and 200 <= status < 300:
        print("PREFLIGHT OK", flush=True)
        return 0
    if status is not None and not is_retryable(status):
        DeadLetter(args.dead_letter).write(payload, status, body)
        print("PREFLIGHT FAILED (rejected)", flush=True)
        return 1
    print("PREFLIGHT FAILED (endpoint unreachable / transient error)", flush=True)
    return 3


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, stream=sys.stderr,
                        format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    try:
        url, mode = select_url(args.url, os.environ)
    except ConfigError as exc:
        log.error("%s", exc)
        return 2
    if args.interval <= 0 or args.timeout <= 0:
        log.error("--interval and --timeout must be > 0")
        return 2
    if args.timeout >= args.interval:
        log.warning("--timeout %.1f >= --interval %.1f: a slow API will grow the queue", args.timeout, args.interval)
    token = os.environ.get("MOTION_API_TOKEN") or None
    if args.preflight:
        return preflight(args, url, mode, token)
    if mode == "remote":
        log.warning("REMOTE mode (%s) needs internet; show night should use MOTION_DB_LOCAL=1", url)
    log.info("bridge: %s -> %s [%s mode, token %s], every %.1fs, stale>%.0fs, spool %s, dead-letter %s",
             args.counts, url, mode, "set" if token else "none", args.interval, args.stale_after,
             args.spool, args.dead_letter)
    sender = Sender(url, timeout=args.timeout, token=token, spool_path=args.spool,
                    max_spool=args.max_spool, dead_letter_path=args.dead_letter)
    bridge = Bridge(args.counts, sender, args.interval, args.stale_after, args.include_source_ts)

    def _sig(signum, _frame):
        log.info("signal %s: stopping", signum)
        bridge.stop()
    signal.signal(signal.SIGINT, _sig)
    try:
        signal.signal(signal.SIGTERM, _sig)
    except (AttributeError, ValueError):
        pass
    sender.start()
    try:
        bridge.run(duration=args.duration)
    finally:
        bridge.stop()
        sender.drain(args.timeout + 0.5)   # send the last tick if the API is up (<= ~3.5 s)
        sender.stop()
        sender.join(timeout=args.timeout + 2)
        sender.persist()
        bridge.tail.close()
        s = dict(sender.stats)
        s.update(lines_ok=bridge.tail.lines_ok, lines_bad=bridge.tail.lines_bad,
                 queued_left=sender.depth(), ticks=bridge.ticks)
        log.info("stopped. stats %s%s", json.dumps(s, sort_keys=True),
                 f" (unsent kept in {args.spool})" if sender.depth() else "")
        if sender.stats["dead_lettered"]:
            alert(f"[BRIDGE] OPERATOR ACTION: {sender.stats['dead_lettered']} payload(s) were rejected "
                  f"this run, see {args.dead_letter}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
