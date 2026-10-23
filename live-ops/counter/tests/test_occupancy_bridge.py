"""Tests for occupancy_bridge.py (stdlib only; uses the in-process mock API on a free port)."""
import json
import os
import threading
import time

import pytest

import mock_occupancy_api as mock
import occupancy_bridge as ob

FULL = {"living_room": 33, "dance_floor": 15, "kitchen_bar": 7, "hallway": 4, "balcony": 2}


def line(ts, zones=FULL, **extra):
    d = {"ts": ts, "zones": zones}
    d.update(extra)
    return json.dumps(d) + "\n"


# ---------------------------------------------------------------- parsing
def test_parse_valid_and_extras_ignored():
    r = ob.parse_line(line(1792615680.12, total=46, status="ok", confidence={"living_room": 0.6}))
    assert r == {"ts": 1792615680.12, "zones": FULL, "total": 46}


@pytest.mark.parametrize("raw", [
    "", "   ", "not json", "[1,2]", '{"zones": {}}', '{"ts": "x", "zones": {}}',
    '{"ts": 1, "zones": [1]}', '{"ts": -5, "zones": {}}', '{"ts": true, "zones": {}}',
    '{"ts": 17926', '{"ts": NaN, "zones": {}}',
])
def test_parse_malformed(raw):
    assert ob.parse_line(raw) is None


def test_bad_values_become_null_and_unknown_zones_dropped():
    z = {"living_room": "33", "dance_floor": -1, "kitchen_bar": 7.0, "hallway": True,
         "balcony": {"count": 2}, "garage": 9}
    r = ob.parse_line(line(100.0, z))
    assert r["zones"] == {"living_room": None, "dance_floor": None, "kitchen_bar": 7,
                          "hallway": None, "balcony": 2}
    assert "garage" not in r["zones"]


# ---------------------------------------------------------------- totals / nulls
def test_total_from_line_wins_even_if_null():
    assert ob.parse_line(line(100.0, total=50))["total"] == 50
    assert ob.parse_line(line(100.0, total=None))["total"] is None


def test_total_computed_without_dance_floor():
    assert ob.parse_line(line(100.0))["total"] == 33 + 7 + 4 + 2   # 46, not 61


def test_total_null_if_any_top_level_unknown():
    z = dict(FULL, hallway=None)
    assert ob.parse_line(line(100.0, z))["total"] is None
    z = dict(FULL, living_room=None)
    assert ob.parse_line(line(100.0, z))["total"] is None


def test_dance_floor_null_does_not_null_total():
    z = dict(FULL, dance_floor=None)
    r = ob.parse_line(line(100.0, z))
    assert r["total"] == 46 and r["zones"]["dance_floor"] is None


def test_missing_zone_key_is_null_kitchen_cam():
    r = ob.parse_line(line(100.0, {"living_room": 30, "dance_floor": 12}))
    assert r["zones"]["kitchen_bar"] is None and r["total"] is None
    assert set(r["zones"]) == set(ob.ZONES)


# ---------------------------------------------------------------- stale
def test_fresh_payload_and_source_ts_flag():
    now = 1000.0
    rec = ob.parse_line(line(995.0, total=46))
    p = ob.build_payload(rec, now, 15)
    assert p == {"ts": 1000.0, "zones": FULL, "total": 46}
    p2 = ob.build_payload(rec, now, 15, include_source_ts=True)
    assert p2["source_ts"] == 995.0


def test_stale_and_none_give_all_null():
    rec = ob.parse_line(line(900.0, total=46))
    for r in (rec, None):
        p = ob.build_payload(r, 1000.0, 15)
        assert p["zones"] == {z: None for z in ob.ZONES} and p["total"] is None
        assert p["ts"] == 1000.0


# ---------------------------------------------------------------- tail reader
def test_tail_missing_then_appears_partial_line_truncation_rotation(tmp_path):
    f = tmp_path / "counts.jsonl"
    t = ob.CountsTail(str(f))
    assert t.poll() is None                         # not there yet
    f.write_text(line(1.0) + "garbage\n" + line(2.0, total=1))
    assert t.poll()["ts"] == 2.0 and t.lines_bad == 1
    with open(f, "a") as fh:                        # half-written newest line: not used yet
        fh.write('{"ts": 3.0, "zones": {"living_room": 5')
    assert t.poll()["ts"] == 2.0
    with open(f, "a") as fh:
        fh.write(', "kitchen_bar": 1, "hallway": 0, "balcony": 0}}\n')
    r = t.poll()
    assert r["ts"] == 3.0 and r["total"] == 6
    f.write_text(line(4.0))                          # truncated + rewritten (shorter)
    assert t.poll()["ts"] == 4.0
    os.rename(f, tmp_path / "old.jsonl")             # rotated
    assert t.poll()["ts"] == 4.0                     # newest kept while file is gone
    f.write_text(line(5.0))
    assert t.poll()["ts"] == 5.0
    t.close()


def test_tail_reads_incrementally_not_whole_file(tmp_path, monkeypatch):
    f = tmp_path / "counts.jsonl"
    big = "".join(line(float(i)) for i in range(1, 3001))   # ~400 KB
    f.write_text(big)
    t = ob.CountsTail(str(f))
    assert t.poll()["ts"] == 3000.0
    assert t.lines_ok < 3000                          # only the last 64 KB were parsed
    first_ok = t.lines_ok
    with open(f, "a") as fh:
        fh.write(line(3001.0))
    assert t.poll()["ts"] == 3001.0
    assert t.lines_ok == first_ok + 1                 # one new line, no reread
    t.close()


# ---------------------------------------------------------------- URL selection
def test_url_selection():
    assert ob.select_url(None, {"MOTION_DB_LOCAL": "1"}) == (ob.DEFAULT_LOCAL_URL, "local")
    assert ob.select_url("https://x/api", {"MOTION_DB_LOCAL": "1",
                                           "MOTION_LOCAL_URL": "http://127.0.0.1:9/a"}) == ("http://127.0.0.1:9/a", "local")
    assert ob.select_url(None, {"MOTION_API_URL": "https://v.app/api/data/occupancy"}) == \
        ("https://v.app/api/data/occupancy", "remote")
    assert ob.select_url("https://cli/api", {"MOTION_API_URL": "https://env/api"})[0] == "https://cli/api"
    assert ob.select_url(None, {"MOTION_DB_LOCAL": "0", "MOTION_API_URL": "https://e/a"})[1] == "remote"
    with pytest.raises(ob.ConfigError):
        ob.select_url(None, {})
    with pytest.raises(ob.ConfigError):
        ob.select_url("ftp://x", {})


def test_main_exits_2_without_url(monkeypatch, tmp_path):
    for k in ("MOTION_DB_LOCAL", "MOTION_API_URL", "MOTION_LOCAL_URL"):
        monkeypatch.delenv(k, raising=False)
    assert ob.main(["--counts", str(tmp_path / "c.jsonl"), "--duration", "0.1"]) == 2


# ---------------------------------------------------------------- network behaviour
class Mock:
    def __init__(self, port=0, **kw):
        self.kw = kw
        self.srv = mock.serve("127.0.0.1", port, quiet=True, **kw)
        self.port = self.srv.server_address[1]
        self.th = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.th.start()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}{mock.PATH}"

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def wait_for(cond, timeout=10.0):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.05)
    return False


def test_successful_post_records_response(tmp_path):
    m = Mock(log_path=str(tmp_path / "rx.jsonl"))
    try:
        s = ob.Sender(m.url, timeout=2, spool_path=str(tmp_path / "spool.jsonl"))
        s.start()
        s.enqueue({"ts": 1.0, "zones": FULL, "total": 46})
        assert wait_for(lambda: s.stats["sent"] == 1)
        payload, status, body = s.last_ok
        assert status == 201 and json.loads(body) == {"ok": True, "received": payload}
        s.stop(); s.join(3)
        assert not (tmp_path / "spool.jsonl").exists()
    finally:
        m.close()


def test_api_down_spools_then_flushes_in_order(tmp_path):
    import socket
    sock = socket.socket(); sock.bind(("127.0.0.1", 0)); port = sock.getsockname()[1]; sock.close()
    url = f"http://127.0.0.1:{port}{mock.PATH}"
    spool = tmp_path / "spool.jsonl"
    s = ob.Sender(url, timeout=0.5, spool_path=str(spool), backoff=lambda a: 0.1 * min(a, 3))
    s.start()
    for i in range(5):
        s.enqueue({"ts": float(i), "zones": FULL, "total": i})
    assert wait_for(lambda: s.stats["failed_attempts"] >= 2)
    assert s.depth() == 5
    assert wait_for(lambda: spool.exists() and len(spool.read_text().splitlines()) == 5)
    rx = tmp_path / "rx.jsonl"
    m = Mock(port=port, log_path=str(rx))           # API comes back
    try:
        assert wait_for(lambda: s.depth() == 0 and s.stats["sent"] == 5)
        got = [json.loads(l)["ts"] for l in rx.read_text().splitlines()]
        assert got == [0.0, 1.0, 2.0, 3.0, 4.0]       # oldest first, none lost
        assert wait_for(lambda: not spool.exists())
    finally:
        s.stop(); s.join(3); m.close()


def test_spool_survives_restart(tmp_path):
    spool = tmp_path / "spool.jsonl"
    s = ob.Sender("http://127.0.0.1:9/x", spool_path=str(spool))   # not started
    for i in range(3):
        s.enqueue({"ts": float(i), "zones": FULL, "total": i})
    s.persist()
    s2 = ob.Sender("http://127.0.0.1:9/x", spool_path=str(spool))
    assert [p["ts"] for p in s2.q] == [0.0, 1.0, 2.0]


def test_queue_bounded_drops_oldest(tmp_path):
    s = ob.Sender("http://127.0.0.1:9/x", spool_path=None, max_spool=3)
    for i in range(5):
        s.enqueue({"ts": float(i), "zones": FULL, "total": i})
    assert [p["ts"] for p in s.q] == [2.0, 3.0, 4.0]
    assert s.stats["dropped_overflow"] == 2


@pytest.mark.parametrize("code", [400, 401, 404, 422])
def test_4xx_dead_lettered_not_retried(tmp_path, capsys, code):
    m = Mock(status=code)
    dl = tmp_path / "dead.jsonl"
    try:
        s = ob.Sender(m.url, timeout=1, spool_path=None, dead_letter_path=str(dl), backoff=lambda a: 0.1)
        s.start()
        s.enqueue({"ts": 1.0, "zones": FULL, "total": 46})
        s.enqueue({"ts": 2.0, "zones": FULL, "total": 46})
        assert wait_for(lambda: s.stats["dead_lettered"] == 2)
        time.sleep(0.3)
        assert s.stats["attempts"] == 2 and s.depth() == 0 and s.stats["failed_attempts"] == 0
        s.stop(); s.join(3)
    finally:
        m.close()
    recs = [json.loads(l) for l in dl.read_text().splitlines()]
    assert [r["payload"]["ts"] for r in recs] == [1.0, 2.0]
    assert all(r["status"] == code and f"forced {code}" in r["detail"] and "at" in r for r in recs)
    assert all(r["payload"]["zones"] == FULL for r in recs)
    err = capsys.readouterr().err
    assert f"[BRIDGE] {code} rejected, dead-lettered: " in err
    assert f"[BRIDGE] OPERATOR ACTION: fix payload shape, see {dl}" in err


def test_dead_letter_detail_truncated_to_500(tmp_path):
    d = ob.DeadLetter(str(tmp_path / "d.jsonl"))
    d.write({"ts": 1.0}, 400, "x" * 2000)
    rec = json.loads((tmp_path / "d.jsonl").read_text())
    assert len(rec["detail"]) == 500


class FakeRng:
    def __init__(self, v):
        self.v = v

    def uniform(self, a, b):
        return a + (b - a) * self.v


def test_backoff_sequence_and_jitter_bounds():
    lo = [ob.backoff_delay(a, FakeRng(0.0)) for a in range(1, 9)]
    mid = [ob.backoff_delay(a, FakeRng(0.5)) for a in range(1, 9)]
    hi = [ob.backoff_delay(a, FakeRng(1.0)) for a in range(1, 9)]
    assert mid == [2, 4, 8, 16, 32, 32, 32, 32]               # stays at the cap, never gives up
    assert lo == [1, 2, 4, 8, 16, 16, 16, 16]                  # x0.5
    assert hi == [3, 6, 12, 24, 48, 48, 48, 48]                # x1.5, under BACKOFF_MAX 60
    import random
    r = random.Random(42)
    for a in range(1, 50):
        d = ob.backoff_delay(a, r)
        base = 2 * 2 ** (min(a, 5) - 1)
        assert 0.5 * base <= d <= 1.5 * base <= ob.BACKOFF_MAX


def test_sender_uses_patch_schedule_and_keeps_retrying(tmp_path):
    """Real backoff_delay with a seeded RNG, time compressed x100 via the backoff hook."""
    import random
    rng = random.Random(7)
    expected = [ob.backoff_delay(a, random.Random(7)) for a in (1,)]  # first draw check below
    seen = []

    def hook(attempt):
        d = ob.backoff_delay(attempt, rng)
        seen.append((attempt, d))
        return d / 100.0

    s = ob.Sender("http://127.0.0.1:9/x", timeout=0.2, spool_path=None, backoff=hook)
    s.start()
    s.enqueue({"ts": 1.0, "zones": FULL, "total": 46})
    assert wait_for(lambda: len(seen) >= 7, timeout=15)
    s.stop(); s.join(3)
    assert [a for a, _ in seen[:7]] == [1, 2, 3, 4, 5, 6, 7]
    assert seen[0][1] == expected[0]
    for a, d in seen:
        base = 2 * 2 ** (min(a, 5) - 1)
        assert 0.5 * base <= d <= 1.5 * base
    assert s.depth() == 1 and s.stats["dead_lettered"] == 0    # still buffered after 7+ failures


def test_post_frame_contract(tmp_path):
    ok = Mock()
    bad = Mock(status=400)
    try:
        s = ob.Sender(ok.url, timeout=1, spool_path=str(tmp_path / "b.jsonl"),
                      dead_letter_path=str(tmp_path / "d.jsonl"), backoff=lambda a: 0.1)
        r = ob.post_frame(ok.url, {"ts": 1.0, "zones": FULL, "total": 46}, 1, sender=s)
        assert r["ok"] is True and r["status"] == 201 and json.loads(r["body"])["ok"] is True
        r = ob.post_frame(bad.url, {"ts": 2.0, "zones": FULL, "total": 46}, 1, sender=s)
        assert r == {"ok": False, "reason": "rejected_400", "status": 400,
                     "detail": json.dumps({"ok": False, "error": "forced 400"})}
        assert (tmp_path / "d.jsonl").exists() and s.depth() == 0
        t0 = time.monotonic()
        r = ob.post_frame("http://127.0.0.1:9/x", {"ts": 3.0, "zones": FULL, "total": 1}, 1, sender=s)
        assert r["ok"] is False and r["reason"] == "buffered" and s.depth() == 1
        assert time.monotonic() - t0 < 1.5                     # returned, didn't sleep/retry
        r = ob.post_frame(ok.url, {"ts": 4.0, "zones": FULL, "total": 1}, 1, sender=s)
        assert r["reason"] == "buffered" and s.depth() == 2     # backlog -> queued behind, order kept
    finally:
        ok.close(); bad.close()


def test_backlog_drain_stops_at_first_failure_keeps_order(tmp_path):
    """Mock fails every other request with 503: everything still arrives, strictly in order."""
    rx = tmp_path / "rx.jsonl"
    import random as _r
    m = Mock(fail_rate=0.5, log_path=str(rx), rng=_r.Random(3))
    try:
        s = ob.Sender(m.url, timeout=1, spool_path=None, backoff=lambda a: 0.02)
        for i in range(20):
            s.enqueue({"ts": float(i), "zones": FULL, "total": i})
        s.start()
        assert wait_for(lambda: s.depth() == 0, timeout=15)
        assert s.stats["failed_attempts"] > 0
        got = [json.loads(l)["ts"] for l in rx.read_text().splitlines()]
        assert got == [float(i) for i in range(20)]
        s.stop(); s.join(3)
    finally:
        m.close()


def test_default_paths_next_to_script():
    import os
    d = os.path.dirname(os.path.abspath(ob.__file__))
    assert ob.DEFAULT_SPOOL == os.path.join(d, "bridge_buffer.jsonl")
    assert ob.DEFAULT_DEAD_LETTER == os.path.join(d, "bridge_dead_letter.jsonl")
    a = ob.build_parser().parse_args([])
    assert a.spool == ob.DEFAULT_SPOOL and a.dead_letter == ob.DEFAULT_DEAD_LETTER


def _preflight(tmp_path, monkeypatch, url, counts_text=None):
    f = tmp_path / "counts.jsonl"
    if counts_text is not None:
        f.write_text(counts_text)
    monkeypatch.setenv("MOTION_DB_LOCAL", "1")
    monkeypatch.setenv("MOTION_LOCAL_URL", url)
    return ob.main(["--counts", str(f), "--preflight", "--timeout", "1",
                    "--spool", str(tmp_path / "b.jsonl"), "--dead-letter", str(tmp_path / "d.jsonl")])


def test_preflight_ok(tmp_path, monkeypatch, capsys):
    m = Mock()
    try:
        rc = _preflight(tmp_path, monkeypatch, m.url, line(time.time(), total=46))
    finally:
        m.close()
    out = capsys.readouterr().out
    assert rc == 0 and "STATUS   201" in out and "PREFLIGHT OK" in out
    req = json.loads(out.split("REQUEST  ", 1)[1].splitlines()[0])
    assert req["zones"] == FULL and req["total"] == 46
    assert not (tmp_path / "b.jsonl").exists()                # preflight never buffers


def test_preflight_rejected_and_unreachable(tmp_path, monkeypatch, capsys):
    m = Mock(status=400)
    try:
        assert _preflight(tmp_path, monkeypatch, m.url, line(time.time())) == 1
    finally:
        m.close()
    assert (tmp_path / "d.jsonl").exists()
    assert "[BRIDGE] 400 rejected" in capsys.readouterr().err
    assert _preflight(tmp_path, monkeypatch, "http://127.0.0.1:9/x", line(time.time())) == 3


def test_429_and_503_are_retried(tmp_path):
    for code in (429, 503):
        m = Mock(status=code)
        try:
            s = ob.Sender(m.url, timeout=1, spool_path=None, backoff=lambda a: 0.05)
            s.start()
            s.enqueue({"ts": 1.0, "zones": FULL, "total": 46})
            assert wait_for(lambda: s.stats["failed_attempts"] >= 3)
            assert s.depth() == 1 and s.stats["dead_lettered"] == 0
            s.stop(); s.join(3)
        finally:
            m.close()


def test_slow_api_does_not_delay_ticks(tmp_path):
    f = tmp_path / "counts.jsonl"
    f.write_text(line(time.time()))
    m = Mock(delay=2.0)                               # every answer takes 2 s
    try:
        s = ob.Sender(m.url, timeout=0.3, spool_path=None, backoff=lambda a: 0.1)
        b = ob.Bridge(str(f), s, interval=0.2, stale_after=60)
        s.start()
        t0 = time.monotonic()
        b.run(max_ticks=10)
        elapsed = time.monotonic() - t0
        gaps = [b2 - a for a, b2 in zip(b.tick_times, b.tick_times[1:])]
        assert b.ticks == 10
        assert elapsed < 2.3, elapsed                 # 9 gaps * 0.2 s = 1.8 s, not blocked by 2 s POSTs
        assert max(gaps) < 0.35, gaps
        assert s.depth() >= 8                         # payloads waited in the queue instead
        assert s.stats["failed_attempts"] >= 1        # timeouts were treated as retryable
        s.stop(); s.join(3)
    finally:
        m.close()


def test_bridge_end_to_end_inprocess(tmp_path):
    f = tmp_path / "counts.jsonl"
    f.write_text(line(time.time(), total=46))
    rx = tmp_path / "rx.jsonl"
    m = Mock(log_path=str(rx))
    try:
        s = ob.Sender(m.url, timeout=1, spool_path=str(tmp_path / "sp.jsonl"))
        b = ob.Bridge(str(f), s, interval=0.1, stale_after=60)
        s.start()
        b.run(max_ticks=3)
        assert wait_for(lambda: s.stats["sent"] == 3)
        bodies = [json.loads(l) for l in rx.read_text().splitlines()]
        assert all(set(p) == {"ts", "zones", "total"} for p in bodies)
        assert bodies[0]["zones"] == FULL and bodies[0]["total"] == 46
        s.stop(); s.join(3)
    finally:
        m.close()


def test_drain_sends_last_tick_on_shutdown(tmp_path):
    m = Mock(delay=0.3)
    try:
        s = ob.Sender(m.url, timeout=2, spool_path=str(tmp_path / "sp.jsonl"))
        s.start()
        s.enqueue({"ts": 1.0, "zones": FULL, "total": 46})
        assert s.drain(2.0) is True and s.stats["sent"] == 1
        s.stop(); s.join(3)
        assert not (tmp_path / "sp.jsonl").exists()
    finally:
        m.close()


def test_drain_gives_up_fast_when_api_down(tmp_path):
    spool = tmp_path / "sp.jsonl"
    s = ob.Sender("http://127.0.0.1:9/x", timeout=0.5, spool_path=str(spool), backoff=lambda a: 5)
    s.start()
    s.enqueue({"ts": 1.0, "zones": FULL, "total": 46})
    t0 = time.monotonic()
    assert s.drain(3.0) is False
    assert time.monotonic() - t0 < 1.5
    s.stop(); s.join(3)
    assert len(spool.read_text().splitlines()) == 1     # kept for next start
