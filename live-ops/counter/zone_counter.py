#!/usr/bin/env python3
"""MOTION zone people-counter (MVP), FORGE lane.

Counts how many people are in each named zone of a camera view, once per interval:
  frame -> YOLOv8 (person class only) -> foot point (bottom-centre of box) -> polygon zone
  -> per-frame counts per zone -> robust window statistic + honest confidence
  -> JSON lines on stdout + CSV rows {timestamp, zone, headcount, confidence}.

Privacy by design: counts only. There is no tracking, no IDs, no faces and no identity.
No image is ever written unless --draw-zones is asked for (a single preview PNG).
Offline: ultralytics telemetry/sync off, weights only from a local file, never downloaded.
Logs go to stderr; stdout is clean JSONL.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Optional

import numpy as np

# ---- offline hardening: must happen before ultralytics is imported anywhere ----
os.environ.setdefault("YOLO_OFFLINE", "1")
os.environ.setdefault("YOLO_AUTOINSTALL", "False")
os.environ.setdefault("YOLO_VERBOSE", "False")
# RTSP over TCP with a 5 s socket timeout, so a dead stream can't block a read forever
os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp|timeout;5000000")

log = logging.getLogger("zone_counter")

HERE = Path(__file__).resolve().parent
DEFAULT_WEIGHTS = HERE.parent / "yolov8s.pt"
ZONE_NAMES = ["living_room", "dance_floor", "kitchen_bar", "hallway", "balcony"]
CSV_FIELDS = ["timestamp", "zone", "headcount", "confidence"]
PERSON = 0  # COCO class id

# Default split of the frame for TESTING ONLY. Real polygons are drawn per camera on 29 Oct.
#   +-------------+-------------+-------------+
#   | living_room | dance_floor | kitchen_bar |   top half, three columns
#   +-------------+------+------+-------------+
#   |      hallway       |       balcony      |   bottom half, two columns
#   +--------------------+--------------------+
DEFAULT_ZONES = {
    "living_room": [[0.0, 0.0], [1 / 3, 0.0], [1 / 3, 0.5], [0.0, 0.5]],
    "dance_floor": [[1 / 3, 0.0], [2 / 3, 0.0], [2 / 3, 0.5], [1 / 3, 0.5]],
    "kitchen_bar": [[2 / 3, 0.0], [1.0, 0.0], [1.0, 0.5], [2 / 3, 0.5]],
    "hallway": [[0.0, 0.5], [0.5, 0.5], [0.5, 1.0], [0.0, 1.0]],
    "balcony": [[0.5, 0.5], [1.0, 0.5], [1.0, 1.0], [0.5, 1.0]],
}


# ------------------------------------------------------------------ zones
def load_zones(path: Optional[str]) -> dict[str, np.ndarray]:
    """Zones from JSON ({"zones": {name: [[x,y],...]}} or {name: [[x,y],...]}), normalised 0-1.
    Order matters: a foot point inside two overlapping polygons goes to the FIRST zone listed."""
    if path is None:
        raw = DEFAULT_ZONES
    else:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        raw = data.get("zones", data)
    zones: dict[str, np.ndarray] = {}
    for name, pts in raw.items():
        if str(name).startswith("_"):
            continue  # allow "_comment" keys
        arr = np.asarray(pts, dtype=np.float64)
        if arr.ndim != 2 or arr.shape[1] != 2 or len(arr) < 3:
            raise ValueError(f"zone {name!r}: need >= 3 [x, y] points")
        if arr.min() < -0.001 or arr.max() > 1.001:
            raise ValueError(f"zone {name!r}: coordinates must be normalised 0-1")
        zones[str(name)] = arr
    if not zones:
        raise ValueError("no zones defined")
    return zones


def points_in_polygon(pts: np.ndarray, poly: np.ndarray) -> np.ndarray:
    """Vectorised even-odd ray casting. pts (N,2), poly (M,2); returns bool (N,).
    Points exactly on the right/bottom edge of the frame are nudged inside."""
    if len(pts) == 0:
        return np.zeros(0, dtype=bool)
    x, y = pts[:, 0:1], pts[:, 1:2]
    x1, y1 = poly[:, 0], poly[:, 1]
    x2, y2 = np.roll(x1, -1), np.roll(y1, -1)
    cond = (y1 > y) != (y2 > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xint = (x2 - x1) * (y - y1) / (y2 - y1) + x1
    crosses = cond & (x < xint)
    return (np.count_nonzero(crosses, axis=1) % 2) == 1


def foot_points(xyxy: np.ndarray, w: int, h: int) -> np.ndarray:
    """Bottom-centre of each box, normalised 0-1 and clamped to just inside the frame."""
    if len(xyxy) == 0:
        return np.zeros((0, 2))
    fx = (xyxy[:, 0] + xyxy[:, 2]) / 2.0 / w
    fy = xyxy[:, 3] / h
    eps = 1e-6
    return np.stack([np.clip(fx, eps, 1 - eps), np.clip(fy, eps, 1 - eps)], axis=1)


def load_parents(path: Optional[str], zones: dict[str, np.ndarray]) -> dict[str, str]:
    """Sub-zone -> parent zone. Default: dance_floor is inside living_room (when both exist), so
    living_room's count ALWAYS includes the dance floor. Override with "parents": {...} in the
    zone JSON ("parents": {} turns nesting off)."""
    raw = None
    if path is not None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        raw = data.get("parents")
    if raw is None:
        raw = {"dance_floor": "living_room"}
    parents = {}
    for child, parent in raw.items():
        if str(child).startswith("_") or child not in zones or parent not in zones:
            continue
        if parent in raw and not str(parent).startswith("_"):
            raise ValueError(f"nested parents not supported ({child} -> {parent} -> ...)")
        parents[str(child)] = str(parent)
    return parents


def assign_zones(xyxy: np.ndarray, conf: np.ndarray, zones: dict[str, np.ndarray],
                 w: int, h: int, parents: Optional[dict[str, str]] = None
                 ) -> tuple[dict[str, list[float]], int]:
    """Returns ({zone: [confidences of people whose feet are in it]}, n_outside_all_zones).

    Top-level zones are exclusive: each person counts in at most one, the FIRST listed that
    contains their feet. A sub-zone (e.g. dance_floor, parent living_room) is NOT exclusive:
    its people also count in the parent. The parent's area is its own polygon OR its children's,
    so it works whether living_room is drawn around the whole room including the dance floor
    (overlapping, recommended) or right up to the dance floor's edge (adjacent)."""
    parents = parents or {}
    out = {name: [] for name in zones}
    pts = foot_points(np.asarray(xyxy, dtype=np.float64).reshape(-1, 4), w, h)
    conf = np.asarray(conf)
    inside = {name: points_in_polygon(pts, poly) for name, poly in zones.items()}
    taken = np.zeros(len(pts), dtype=bool)
    owner = {}
    for name in zones:
        if name in parents:
            continue
        eff = inside[name].copy()
        for child, parent in parents.items():
            if parent == name:
                eff |= inside[child]
        m = eff & ~taken
        out[name] = [float(c) for c in conf[m]]
        owner[name] = m
        taken |= m
    for child, parent in parents.items():
        m = inside[child] & owner.get(parent, np.zeros(len(pts), bool))
        out[child] = [float(c) for c in conf[m]]
    return out, int((~taken).sum())


# ------------------------------------------------------------------ entrances (optional)
_DIRS = {"up": (0.0, -1.0), "down": (0.0, 1.0), "left": (-1.0, 0.0), "right": (1.0, 0.0)}
ENTRY_CSV_FIELDS = ["timestamp", "zone", "ins", "outs", "confidence"]


@dataclass
class Entrance:
    zone: str
    line: np.ndarray                 # [[x1,y1],[x2,y2]] normalised
    in_direction: Optional[str] = None   # None = "towards the zone polygon" (automatic)
    anchor: str = "bottom_center"


def load_entrances(path: Optional[str], zones: dict[str, np.ndarray]) -> list[Entrance]:
    """Optional "entrances" block in the zone JSON:
       "entrances": {"living_room": {"line": [[x1,y1],[x2,y2]], "in_direction": "down"}}
    in_direction is optional: by default IN = moving onto the side of the line where the zone
    polygon's centroid lies."""
    if path is None:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for zone, spec in (data.get("entrances") or {}).items():
        if str(zone).startswith("_"):
            continue
        if zone not in zones:
            raise ValueError(f"entrance for unknown zone {zone!r}")
        line = np.asarray(spec["line"], dtype=np.float64)
        if line.shape != (2, 2) or line.min() < -0.001 or line.max() > 1.001:
            raise ValueError(f"entrance {zone!r}: line must be [[x1,y1],[x2,y2]] in 0-1")
        d = spec.get("in_direction")
        if d is not None and d not in _DIRS:
            raise ValueError(f"entrance {zone!r}: in_direction must be one of {list(_DIRS)}")
        out.append(Entrance(zone, line, d, spec.get("anchor", "bottom_center")))
    return out


def in_is_supervision_in(line_px: np.ndarray, toward: tuple[float, float]) -> bool:
    """supervision's LineZone counts a move onto the LEFT side of start->end (image coords) as
    'in'. Returns True if our IN direction (vector `toward`) points to that side."""
    (x1, y1), (x2, y2) = line_px
    vx, vy = x2 - x1, y2 - y1
    dot = vy * toward[0] - vx * toward[1]          # normal (vy, -vx) . toward
    if abs(dot) < 1e-9 * max(1.0, abs(vx) + abs(vy)):
        raise ValueError("IN direction is parallel to the entrance line")
    return dot > 0


class EntryCounter:
    """ByteTrack (in memory only) + supervision LineZone for one entrance.
    Track IDs exist only inside this object for a few seconds; they are never written,
    logged or emitted. Only the in/out totals leave this class."""

    def __init__(self, ent: Entrance, zone_poly: np.ndarray, w: int, h: int, fps: float,
                 min_crossing_frames: int = 2):
        import supervision as sv
        try:
            from trackers import ByteTrackTracker
            self.tracker = ByteTrackTracker(lost_track_buffer=max(10, int(round(2 * fps))),
                                            frame_rate=fps, track_activation_threshold=0.3,
                                            minimum_consecutive_frames=2,
                                            high_conf_det_threshold=0.45)
        except ImportError:  # older stack
            self.tracker = sv.ByteTrack(frame_rate=int(round(fps)))
        self.sv = sv
        self.zone = ent.zone
        line_px = ent.line * [w, h]
        if ent.in_direction:
            toward = _DIRS[ent.in_direction]
        else:  # towards the zone polygon's centroid
            mid = line_px.mean(axis=0)
            c = (zone_poly * [w, h]).mean(axis=0)
            toward = (c[0] - mid[0], c[1] - mid[1])
        self.swap = not in_is_supervision_in(line_px, toward)
        anchors = {"bottom_center": (sv.Position.BOTTOM_CENTER,), "center": (sv.Position.CENTER,)}
        self.line = sv.LineZone(start=sv.Point(*line_px[0]), end=sv.Point(*line_px[1]),
                                triggering_anchors=anchors.get(ent.anchor, anchors["bottom_center"]),
                                minimum_crossing_threshold=min_crossing_frames)
        self._in = self._out = 0
        log.info("entrance %s: line px=%s IN=%s (swap=%s)", ent.zone,
                 [tuple(int(v) for v in p) for p in line_px], ent.in_direction or "towards zone",
                 self.swap)

    def update(self, xyxy: np.ndarray, conf: np.ndarray) -> tuple[int, int, list[float]]:
        """-> (ins, outs, scores of the boxes that crossed) for this frame."""
        sv = self.sv
        det = sv.Detections(xyxy=np.asarray(xyxy, np.float32).reshape(-1, 4),
                            confidence=np.asarray(conf, np.float32),
                            class_id=np.zeros(len(xyxy), dtype=int))
        tracked = self.tracker.update(det)
        crossed_in, crossed_out = self.line.trigger(tracked)
        a, b = int(np.sum(crossed_in)), int(np.sum(crossed_out))
        scores = [float(c) for c in tracked.confidence[np.asarray(crossed_in) | np.asarray(crossed_out)]] \
            if len(tracked) and tracked.confidence is not None else []
        del tracked  # IDs go out of scope here
        return (b, a, scores) if self.swap else (a, b, scores)


class EntryWindow:
    """Per-window ins/outs for one entrance plus an honest confidence:
       det_q   mean score of the boxes that crossed (0.6 if nobody crossed: unverifiable)
       rate    min(1, analysed fps / 8). Tracking across a doorway needs about 8+ frames/s;
               at 2 fps a person can jump the line between frames and be missed.
       cover   sqrt(frames analysed / frames planned)
    No frames: ins/outs None, confidence 0."""

    def __init__(self, zone: str, expected_frames: int, interval: float):
        self.zone, self.expected, self.interval = zone, max(1, expected_frames), interval
        self.total_in = self.total_out = 0
        self.reset()

    def reset(self):
        self.ins = self.outs = self.frames = 0
        self.scores: list[float] = []

    def add(self, ins: int, outs: int, scores: list[float]):
        self.frames += 1
        self.ins += ins; self.outs += outs
        self.total_in += ins; self.total_out += outs
        self.scores.extend(scores)

    def finalize(self) -> dict:
        if self.frames == 0:
            return {"zone": self.zone, "ins": None, "outs": None, "confidence": 0.0}
        det_q = float(np.mean(self.scores)) if self.scores else 0.6
        rate = min(1.0, (self.frames / self.interval) / 8.0)
        cover = math.sqrt(min(1.0, self.frames / self.expected))
        return {"zone": self.zone, "ins": self.ins, "outs": self.outs,
                "confidence": round(det_q * rate * cover, 3)}


# ------------------------------------------------------------------ aggregation
STATS = ("median", "p75", "p90", "max", "mean")


def window_stat(counts: list[int], stat: str) -> int:
    a = np.asarray(counts, dtype=float)
    if stat == "median":
        v = np.median(a)
    elif stat == "mean":
        v = a.mean()
    elif stat == "max":
        v = a.max()
    else:
        v = np.percentile(a, float(stat[1:]))
    return int(math.floor(v + 0.5))  # round half up, deterministic


@dataclass
class ZoneWindowResult:
    zone: str
    headcount: Optional[int]
    confidence: float
    status: str
    frames_used: int
    extra: dict = field(default_factory=dict)


class WindowAggregator:
    """Collects per-frame zone results for one interval and turns them into one row per zone.

    Headcount: a robust statistic (default p75) of the per-frame counts. NOT a cumulative tally.
    Confidence (0-1), the product of three honest terms:
      det_q   detection quality = mean box score, scaled down by the share of low-score boxes
              (< low_conf). With no boxes at all ("0 people") it is a fixed --empty-confidence
              (default 0.4): an empty zone can't be checked (a blocked lens, a dark corner and a
              really empty room all look like 0), so a stable 0 lands exactly on the
              "check manually" line instead of looking trustworthy.
      stab    count stability = 1 / (1 + spread), spread = (p90 - p10) / max(1, headcount).
              A count that jumps around within the window scores low.
      cover   sqrt(frames analysed / frames expected). Fewer frames than planned means less trust.
    No frames (source down or every frame failed): headcount None, confidence 0, status says why.
    """

    def __init__(self, zones: list[str], expected_frames: int, stat: str = "p75",
                 low_conf: float = 0.4, empty_det_q: float = 0.4):
        if stat not in STATS:
            raise ValueError(f"stat must be one of {STATS}")
        self.zones = list(zones)
        self.expected = max(1, int(expected_frames))
        self.stat = stat
        self.low_conf = low_conf
        self.empty_det_q = empty_det_q
        self.reset()

    def reset(self) -> None:
        self.counts: dict[str, list[int]] = {z: [] for z in self.zones}
        self.confs: dict[str, list[float]] = {z: [] for z in self.zones}
        self.ok_frames = 0
        self.failed_frames = 0
        self.outside = 0

    def add_frame(self, zone_confs: Optional[dict[str, list[float]]], outside: int = 0) -> None:
        """zone_confs None = this frame failed (read error, detector error)."""
        if zone_confs is None:
            self.failed_frames += 1
            return
        self.ok_frames += 1
        self.outside += outside
        for z in self.zones:
            c = zone_confs.get(z, [])
            self.counts[z].append(len(c))
            self.confs[z].extend(c)

    def finalize(self, source_status: str = "ok") -> list[ZoneWindowResult]:
        res = []
        for z in self.zones:
            n = self.ok_frames
            if n == 0:
                status = source_status if source_status not in ("ok", "partial_window") else (
                    "all_frames_failed" if self.failed_frames else "no_frames")
                res.append(ZoneWindowResult(z, None, 0.0, status, 0,
                                            {"frames_failed": self.failed_frames}))
                continue
            counts = self.counts[z]
            head = window_stat(counts, self.stat)
            confs = np.asarray(self.confs[z], dtype=float)
            if len(confs):
                low_frac = float((confs < self.low_conf).mean())
                det_q = float(confs.mean()) * (1.0 - 0.5 * low_frac)
            else:
                low_frac, det_q = 0.0, self.empty_det_q
            a = np.asarray(counts, dtype=float)
            spread = (np.percentile(a, 90) - np.percentile(a, 10)) / max(1.0, float(head))
            stab = 1.0 / (1.0 + spread)
            cover = math.sqrt(min(1.0, n / self.expected))
            conf = round(max(0.0, min(1.0, det_q * stab * cover)), 3)
            status = "ok" if n >= 0.5 * self.expected else "partial"
            if source_status != "ok":
                status = source_status  # e.g. "partial_window" at end-of-file
            res.append(ZoneWindowResult(z, head, conf, status, n, {
                "frames_failed": self.failed_frames, "count_min": int(a.min()),
                "count_max": int(a.max()), "count_median": float(np.median(a)),
                "mean_score": round(float(confs.mean()), 3) if len(confs) else None,
                "low_score_frac": round(low_frac, 3)}))
        return res


# ------------------------------------------------------------------ output
def iso(ts: datetime) -> str:
    return ts.isoformat(timespec="seconds")


class Emitter:
    """JSONL to stdout (with extras) + CSV with exactly timestamp,zone,headcount,confidence."""

    def __init__(self, csv_path: Optional[str], csv_extra: bool = False, stream=None):
        self.stream = stream or sys.stdout
        self.csv_extra = csv_extra
        self.fields = CSV_FIELDS + (["status", "frames_used"] if csv_extra else [])
        self._fh = None
        self._w = None
        if csv_path:
            p = Path(csv_path)
            new = not p.exists() or p.stat().st_size == 0
            if not new:
                with p.open(newline="", encoding="utf-8") as fh:
                    header = next(csv.reader(fh), [])
                if header != self.fields:
                    raise ValueError(f"{p} exists with header {header}, expected {self.fields}")
            self._fh = p.open("a", newline="", encoding="utf-8")
            self._w = csv.writer(self._fh)
            if new:
                self._w.writerow(self.fields)
                self._fh.flush()

    def open_entries(self, path: str) -> None:
        p = Path(path)
        new = not p.exists() or p.stat().st_size == 0
        if not new:
            with p.open(newline="", encoding="utf-8") as fh:
                header = next(csv.reader(fh), [])
            if header != ENTRY_CSV_FIELDS:
                raise ValueError(f"{p} exists with header {header}, expected {ENTRY_CSV_FIELDS}")
        self._efh = p.open("a", newline="", encoding="utf-8")
        self._ew = csv.writer(self._efh)
        if new:
            self._ew.writerow(ENTRY_CSV_FIELDS); self._efh.flush()

    def emit(self, ts: datetime, results: list[ZoneWindowResult], json_extra: dict,
             entries: Optional[dict[str, dict]] = None) -> None:
        stamp = iso(ts)
        entries = entries or {}
        for e in entries.values():
            if getattr(self, "_ew", None):
                self._ew.writerow([stamp, e["zone"], "" if e["ins"] is None else e["ins"],
                                   "" if e["outs"] is None else e["outs"], f"{e['confidence']:.3f}"])
        if getattr(self, "_efh", None):
            self._efh.flush()
        for r in results:
            rec = {"timestamp": stamp, "zone": r.zone, "headcount": r.headcount,
                   "confidence": r.confidence, "status": r.status, "frames_used": r.frames_used}
            rec.update(r.extra)
            rec.update(json_extra)
            e = entries.get(r.zone)
            if e:
                rec.update({"ins": e["ins"], "outs": e["outs"],
                            "entries_confidence": e["confidence"],
                            "ins_total": e.get("ins_total"), "outs_total": e.get("outs_total")})
            self.stream.write(json.dumps(rec) + "\n")
            if self._w:
                row = [stamp, r.zone, "" if r.headcount is None else r.headcount,
                       f"{r.confidence:.3f}"]
                if self.csv_extra:
                    row += [r.status, r.frames_used]
                self._w.writerow(row)
        self.stream.flush()
        if self._fh:
            self._fh.flush()

    def close(self) -> None:
        if self._fh:
            self._fh.close()
        if getattr(self, "_efh", None):
            self._efh.close()


class ZonesFileWriter:
    """--zones-file: one JSON object per line for the HQ dashboard (hq-local.html), appended
    once per window (every <= 5 s, the dashboard's heartbeat):
      {"ts": 1792615680.12, "zones": {"living_room": 33, "dance_floor": 15, "kitchen_bar": 7,
       "hallway": 4, "balcony": 2}, "total": 46, "status": "ok", "zone_status": {...},
       "confidence": {...}}
    living_room already includes dance_floor; total = top-level zones only (no double count).
    An unknown zone is null (never a carried-forward number); total is null unless every
    top-level zone is known. Each line is ONE os.write of a complete line on an O_APPEND fd,
    then fsync, so a reader never sees half a line. Write errors are logged, never raised."""

    def __init__(self, path: str, parents: dict[str, str]):
        self.path, self.parents = path, parents
        self.errors = 0

    def line(self, ts_unix: float, results: list[ZoneWindowResult]) -> str:
        zones = {r.zone: r.headcount for r in results}
        top = [r for r in results if r.zone not in self.parents]
        known = all(r.headcount is not None for r in top) and top
        total = sum(r.headcount for r in top) if known else None
        statuses = {r.status for r in results}
        status = "ok" if statuses <= {"ok"} else (
            "unknown" if all(r.headcount is None for r in results) else "partial")
        rec = {"ts": round(ts_unix, 3), "zones": zones, "total": total, "status": status,
               "zone_status": {r.zone: r.status for r in results},
               "confidence": {r.zone: r.confidence for r in results}}
        return json.dumps(rec, separators=(", ", ": ")) + "\n"

    def write(self, ts_unix: float, results: list[ZoneWindowResult]) -> bool:
        data = self.line(ts_unix, results).encode("utf-8")
        try:
            flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0)
            fd = os.open(self.path, flags, 0o644)
            try:
                n = os.write(fd, data)
                if n != len(data):
                    raise OSError(f"short write {n}/{len(data)} bytes")
                try:
                    os.fsync(fd)
                except OSError:
                    pass  # some filesystems/pipes can't fsync; the line is already written
            finally:
                os.close(fd)
            return True
        except Exception as exc:
            self.errors += 1
            if self.errors <= 3 or self.errors % 60 == 0:
                log.error("zones-file write failed (#%d, will keep trying): %s", self.errors, exc)
            return False


# ------------------------------------------------------------------ detectors
class FakeDetector:
    """Test/bench detector: returns whatever boxes a callable gives for a frame. No weights."""
    name = "fake"

    def __init__(self, fn: Callable[[np.ndarray], tuple[np.ndarray, np.ndarray]]):
        self.fn = fn

    def detect(self, frame):
        xyxy, conf = self.fn(frame)
        return np.asarray(xyxy, dtype=np.float64).reshape(-1, 4), np.asarray(conf, dtype=np.float64)


def nms(xyxy: np.ndarray, conf: np.ndarray, iou_thr: float, ios_thr: float = 0.85) -> np.ndarray:
    """Greedy NMS on IoU, plus intersection-over-smaller suppression to remove the partial
    duplicates tiling creates (a half-person box inside a whole-person box)."""
    order = np.argsort(-conf)
    keep = []
    area = (xyxy[:, 2] - xyxy[:, 0]).clip(0) * (xyxy[:, 3] - xyxy[:, 1]).clip(0)
    while len(order):
        i = order[0]
        keep.append(i)
        rest = order[1:]
        xx1 = np.maximum(xyxy[i, 0], xyxy[rest, 0]); yy1 = np.maximum(xyxy[i, 1], xyxy[rest, 1])
        xx2 = np.minimum(xyxy[i, 2], xyxy[rest, 2]); yy2 = np.minimum(xyxy[i, 3], xyxy[rest, 3])
        inter = (xx2 - xx1).clip(0) * (yy2 - yy1).clip(0)
        iou = inter / (area[i] + area[rest] - inter + 1e-9)
        ios = inter / (np.minimum(area[i], area[rest]) + 1e-9)
        order = rest[(iou <= iou_thr) & (ios <= ios_thr)]
    return np.asarray(keep, dtype=int)


def tile_grid(w: int, h: int, tile: int, overlap: float) -> list[tuple[int, int, int, int]]:
    step = max(1, int(tile * (1 - overlap)))
    xs = list(range(0, max(1, w - tile) + 1, step)) or [0]
    ys = list(range(0, max(1, h - tile) + 1, step)) or [0]
    if xs[-1] + tile < w:
        xs.append(w - tile)
    if ys[-1] + tile < h:
        ys.append(h - tile)
    return [(x, y, min(w, x + tile), min(h, y + tile)) for y in ys for x in xs]


class YoloDetector:
    """YOLOv8 person-only. Optional SAHI-style tiling (pure numpy, no extra dependency):
    one full-frame pass (catches big/near people) + overlapping tiles at native resolution
    (catches small/far people), merged with NMS. Boxes cut by an interior tile edge are dropped,
    since the overlapping neighbour tile sees that person whole."""
    name = "yolov8"

    def __init__(self, weights: str, conf: float = 0.2, iou: float = 0.6, imgsz: int = 1280,
                 device: str = "auto", tile: int = 0, tile_overlap: float = 0.25,
                 max_det: int = 500):
        p = Path(weights)
        if not p.is_file():
            raise FileNotFoundError(
                f"weights not found: {p}. Run (online, once): python ../prefetch_weights.py. "
                "This script never downloads weights.")
        from ultralytics import YOLO, settings
        try:
            settings.update({"sync": False})
        except Exception as exc:  # pragma: no cover
            log.warning("could not disable ultralytics sync: %s", exc)
        import torch
        if device == "auto":
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.device = device
        self.half = device.startswith("cuda")
        self.model = YOLO(str(p))
        self.conf, self.iou, self.imgsz = conf, iou, imgsz
        self.tile, self.overlap, self.max_det = tile, tile_overlap, max_det
        log.info("YOLO %s on %s (half=%s) conf=%.2f iou=%.2f imgsz=%d tile=%s",
                 p.name, device, self.half, conf, iou, imgsz, tile or "off")

    def _predict(self, imgs, imgsz):
        res = self.model.predict(imgs, classes=[PERSON], conf=self.conf, iou=self.iou,
                                 imgsz=imgsz, device=self.device, half=self.half,
                                 max_det=self.max_det, verbose=False)
        return [(r.boxes.xyxy.cpu().numpy().astype(np.float64),
                 r.boxes.conf.cpu().numpy().astype(np.float64)) for r in res]

    def detect(self, frame: np.ndarray):
        (xyxy, conf), = self._predict(frame, self.imgsz)
        if not self.tile:
            return xyxy, conf
        h, w = frame.shape[:2]
        tiles = tile_grid(w, h, self.tile, self.overlap)
        crops = [np.ascontiguousarray(frame[y1:y2, x1:x2]) for x1, y1, x2, y2 in tiles]
        boxes, scores = [xyxy], [conf]
        margin = 3
        for (x1, y1, x2, y2), (b, s) in zip(tiles, self._predict(crops, self.tile)):
            if not len(b):
                continue
            b = b + np.array([x1, y1, x1, y1])
            cut = np.zeros(len(b), dtype=bool)
            if x1 > 0: cut |= b[:, 0] <= x1 + margin
            if y1 > 0: cut |= b[:, 1] <= y1 + margin
            if x2 < w: cut |= b[:, 2] >= x2 - margin
            if y2 < h: cut |= b[:, 3] >= y2 - margin
            boxes.append(b[~cut]); scores.append(s[~cut])
        xyxy = np.concatenate(boxes); conf = np.concatenate(scores)
        if len(xyxy) == 0:
            return xyxy.reshape(0, 4), conf
        keep = nms(xyxy, conf, self.iou)
        return xyxy[keep], conf[keep]


# ------------------------------------------------------------------ sources
class FileSource:
    """Video file. Clock = video time (frame index / fps), so results don't depend on CPU speed.
    Reads every `step`-th frame (grab() skips decoding colour conversion for the rest)."""
    live = False

    def __init__(self, path: str, sample_fps: float, loop: bool = False):
        import cv2
        self.cv2 = cv2
        self.path, self.loop = path, loop
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise IOError(f"cannot open video file {path!r}")
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise IOError(f"video file {path!r} opened but has no readable frames")
        self.first = frame
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps if fps and 1 <= fps <= 240 else 30.0
        self.step = max(1, int(round(self.fps / sample_fps)))
        self.idx = 0          # index of the frame in self.first
        self.offset = 0.0     # video time added by previous loops
        self._pending_first = True
        self.desc = f"file {Path(path).name} ({self.fps:.2f} fps, every {self.step}th frame)"

    def read(self):
        """-> (frame | None, t_seconds) or raises EOFError."""
        if self._pending_first:
            self._pending_first = False
            return self.first, 0.0
        for _ in range(self.step - 1):
            if not self.cap.grab():
                return self._eof()
            self.idx += 1
        ok, frame = self.cap.read()
        if not ok:
            return self._eof()
        self.idx += 1
        return frame, self.offset + self.idx / self.fps

    def _eof(self):
        if not self.loop:
            raise EOFError
        log.info("end of file, looping")
        self.offset += (self.idx + 1) / self.fps
        self.cap.release()
        self.cap = self.cv2.VideoCapture(self.path)
        self.idx = -1
        ok, frame = self.cap.read()
        if not ok:
            raise EOFError
        self.idx = 0
        return frame, self.offset

    def close(self):
        self.cap.release()


class LiveSource:
    """Webcam index or stream URL. A grabber thread keeps only the newest frame (no lag build-up),
    reopens on failure, and never raises into the main loop. Clock = wall time."""
    live = True

    def __init__(self, spec, open_timeout: float = 8.0):
        import cv2
        self.cv2, self.spec = cv2, spec
        self.desc = f"webcam {spec}" if isinstance(spec, int) else f"stream {spec}"
        self._lock = threading.Lock()
        self._frame, self._ts, self._seq, self._taken = None, 0.0, 0, 0
        self.connected = False
        self._stop = threading.Event()
        self.first = None
        self._t = threading.Thread(target=self._run, daemon=True, name="grabber")
        self._t.start()
        t0 = time.monotonic()
        while time.monotonic() - t0 < open_timeout and self.first is None:
            time.sleep(0.05)
        if self.first is None:
            log.warning("%s: no frame within %.0f s; will keep retrying", self.desc, open_timeout)

    def _run(self):
        backoff = 1.0
        while not self._stop.is_set():
            cap = self.cv2.VideoCapture(self.spec)
            if not cap.isOpened():
                self.connected = False
                log.warning("%s: open failed, retry in %.0f s", self.desc, backoff)
                self._stop.wait(backoff); backoff = min(backoff * 2, 10); continue
            fails = 0
            while not self._stop.is_set():
                ok, frame = cap.read()
                if not ok or frame is None:
                    fails += 1
                    if fails >= 25:
                        break
                    time.sleep(0.02); continue
                fails, backoff = 0, 1.0
                self.connected = True
                with self._lock:
                    self._frame, self._ts, self._seq = frame, time.time(), self._seq + 1
                    if self.first is None:
                        self.first = frame
            cap.release()
            self.connected = False
            log.warning("%s: stream lost, reconnecting", self.desc)

    def read(self):
        """-> (newest unseen frame or None, wall time). Never raises."""
        with self._lock:
            if self._seq != self._taken and self._frame is not None and time.time() - self._ts < 2.0:
                self._taken = self._seq
                return self._frame, self._ts
        return None, time.time()

    def close(self):
        """Stop and JOIN the grabber: a daemon thread killed inside FFmpeg at interpreter
        exit aborts the process ("FATAL: exception not rethrown")."""
        self._stop.set()
        self._t.join(timeout=8.0)
        if self._t.is_alive():
            log.warning("grabber thread did not stop within 8 s")


def open_source(args):
    """File first; webcam only if --webcam was given (as primary, or as fallback with
    --webcam-fallback). Returns a source or None."""
    if args.video:
        try:
            if args.video.startswith(("rtsp://", "http://", "https://")):
                return LiveSource(args.video)
            return FileSource(args.video, args.sample_fps, args.loop)
        except Exception as exc:
            log.error("%s", exc)
            if args.webcam is None or not args.webcam_fallback:
                log.error("no fallback (use --webcam INDEX --webcam-fallback to fall back to a webcam)")
                return None
            log.warning("falling back to webcam %d", args.webcam)
    if args.webcam is not None:
        return LiveSource(args.webcam)
    return None


# ------------------------------------------------------------------ preview
def draw_zones_png(frame: np.ndarray, zones: dict[str, np.ndarray], out_path: str) -> None:
    import cv2
    img = frame.copy()
    h, w = img.shape[:2]
    colors = [(0, 200, 255), (255, 0, 200), (0, 255, 0), (255, 160, 0), (0, 0, 255),
              (200, 200, 0), (128, 0, 255)]
    overlay = img.copy()
    th = max(2, w // 400)
    for i, (name, poly) in enumerate(zones.items()):
        pts = (poly * [w, h]).round().astype(np.int32)
        col = colors[i % len(colors)]
        cv2.fillPoly(overlay, [pts], col)
        cv2.polylines(img, [pts], True, col, th)
    img = cv2.addWeighted(overlay, 0.18, img, 0.82, 0)
    fs = max(0.5, max(w, h) / 1400)
    for i, (name, poly) in enumerate(zones.items()):
        pts = (poly * [w, h]).round().astype(np.int32)
        cx, cy = pts.mean(axis=0).astype(int)
        (tw, tth), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, fs, th)
        org = (int(cx - tw / 2), int(cy + tth / 2))
        cv2.putText(img, name, org, cv2.FONT_HERSHEY_SIMPLEX, fs, (0, 0, 0), th + 4, cv2.LINE_AA)
        cv2.putText(img, name, org, cv2.FONT_HERSHEY_SIMPLEX, fs, colors[i % len(colors)], th, cv2.LINE_AA)
        for (x, y), (nx, ny) in zip(pts, poly):  # vertex coords, to help edit the JSON
            lbl = f"{nx:.2f},{ny:.2f}"
            (lw, lh), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, fs * 0.45, 1)
            px = int(min(max(x + 4, 2), w - lw - 2)); py = int(min(max(y - 4, lh + 2), h - 2))
            cv2.putText(img, lbl, (px, py), cv2.FONT_HERSHEY_SIMPLEX, fs * 0.45, (255, 255, 255),
                        max(1, th // 2), cv2.LINE_AA)
    if not cv2.imwrite(out_path, img):
        raise IOError(f"could not write {out_path}")


# ------------------------------------------------------------------ main loop
def run(args, detector=None, source=None, emitter=None, now=None) -> int:
    zones = load_zones(args.zones)
    names = list(zones)
    parents = load_parents(args.zones, zones)
    entrances = load_entrances(args.zones, zones) if not args.no_entries else []
    if args.sample_fps is None:  # tracking across a doorway needs a higher frame rate
        args.sample_fps = 10.0 if entrances else 2.0
    now = now or (lambda: datetime.now().astimezone())
    if args.start_time:
        start = datetime.fromisoformat(args.start_time)
        if start.tzinfo is None:
            start = start.astimezone()
    else:
        start = now()

    source = source or open_source(args)
    emitter = emitter or Emitter(args.csv, args.csv_extra)
    zfile = ZonesFileWriter(args.zones_file, parents) if args.zones_file else None
    if zfile and args.interval > 5.0:
        log.warning("--zones-file needs a line at least every 5 s: interval %.1f -> 5.0", args.interval)
        args.interval = 5.0

    def emit_all(ts: datetime, results, extra, ent=None):
        emitter.emit(ts, results, extra, ent)
        if zfile:
            zfile.write(ts.timestamp(), results)
    if entrances and args.entries_csv:
        emitter.open_entries(args.entries_csv)
    expected = max(1, int(round(args.interval * args.sample_fps)))
    agg = WindowAggregator(names, expected, args.stat, args.low_conf, args.empty_confidence)

    if source is None:
        emit_all(start, agg.finalize("source_unavailable"), {"source": "none"})
        emitter.close()
        return 2

    if args.draw_zones:
        if source.first is not None:
            draw_zones_png(source.first, zones, args.draw_zones)
            log.info("zone preview written to %s", args.draw_zones)
        else:
            log.error("no frame available for --draw-zones")
        if args.draw_only:
            source.close(); emitter.close()
            return 0

    if detector is None:
        try:
            detector = YoloDetector(args.weights, args.conf, args.iou, args.imgsz, args.device,
                                    args.tile, args.tile_overlap, args.max_det)
        except Exception as exc:
            log.error("detector unavailable: %s", exc)
            emit_all(start, agg.finalize("detector_unavailable"), {"source": source.desc})
            source.close(); emitter.close()
            return 3

    log.info("source: %s | zones: %s | interval %.1fs, sample %.1f fps, stat %s",
             source.desc, ", ".join(names), args.interval, args.sample_fps, args.stat)
    per_frame = open(args.per_frame, "w", encoding="utf-8") if args.per_frame else None
    win_start = 0.0 if not source.live else time.time()
    windows_done = 0
    det_time, det_n, det_errors = 0.0, 0, 0
    period = 1.0 / args.sample_fps
    entry_counters: list = []      # built on the first frame (needs the frame size)
    entry_windows = {e.zone: EntryWindow(e.zone, expected, args.interval) for e in entrances}
    next_sample = time.time()

    def close_window(t_end_label: datetime, status="ok"):
        nonlocal windows_done
        extra = {"window_s": args.interval}
        if per_frame is None and agg.outside:
            extra["outside_zones_frames_sum"] = agg.outside
        if source.live and not getattr(source, "connected", True) and agg.ok_frames == 0:
            status = "source_down"
        ent = {}
        for z, ew in entry_windows.items():
            ent[z] = dict(ew.finalize(), ins_total=ew.total_in, outs_total=ew.total_out)
            ew.reset()
        emit_all(t_end_label, agg.finalize(status), extra, ent)
        agg.reset()
        windows_done += 1

    try:
        while True:
            if args.max_windows and windows_done >= args.max_windows:
                break
            if source.live:
                t_now = time.time()
                if t_now >= win_start + args.interval:
                    close_window(now())
                    win_start += args.interval
                    if t_now - win_start > args.interval:  # fell behind: realign, don't burst
                        win_start = t_now
                    continue
                if t_now < next_sample:
                    time.sleep(min(next_sample - t_now, 0.05)); continue
                next_sample = max(next_sample + period, t_now - period)
                frame, t = source.read()
                if frame is None:
                    time.sleep(0.02)
                    continue
            else:
                try:
                    frame, t = source.read()
                except EOFError:
                    if agg.ok_frames or agg.failed_frames:
                        close_window(start + timedelta(seconds=win_start + args.interval),
                                     "partial_window")
                    log.info("end of file after %d windows", windows_done)
                    break
                except Exception as exc:
                    log.warning("read error: %s", exc)
                    agg.add_frame(None)
                    continue
                while t >= win_start + args.interval:
                    close_window(start + timedelta(seconds=win_start + args.interval))
                    win_start += args.interval
                    if args.max_windows and windows_done >= args.max_windows:
                        break
                if args.max_windows and windows_done >= args.max_windows:
                    break
            if frame is None or not isinstance(frame, np.ndarray) or frame.ndim != 3:
                agg.add_frame(None); continue
            h, w = frame.shape[:2]
            try:
                t0 = time.perf_counter()
                xyxy, conf = detector.detect(frame)
                det_time += time.perf_counter() - t0; det_n += 1
                zc, outside = assign_zones(xyxy, conf, zones, w, h, parents)
                if entrances and not entry_counters:
                    entry_counters = [EntryCounter(e, zones[e.zone], w, h, args.sample_fps,
                                                   args.min_crossing_frames) for e in entrances]
                for ec in entry_counters:
                    entry_windows[ec.zone].add(*ec.update(xyxy, conf))
            except Exception as exc:
                det_errors += 1
                if det_errors <= 3 or det_errors % 100 == 0:
                    log.warning("detector error #%d (frame skipped): %s", det_errors, exc)
                agg.add_frame(None); continue
            agg.add_frame(zc, outside)
            if per_frame:
                per_frame.write(json.dumps({"t": round(float(t), 3),
                                            **{z: len(c) for z, c in zc.items()},
                                            "outside": outside}) + "\n")
            if det_n % 50 == 0:
                log.info("detector %.2f frames/s (%d frames)", det_n / det_time, det_n)
    except KeyboardInterrupt:
        log.info("stopped by user")
    finally:
        if det_n:
            log.info("SUMMARY detector frames=%d mean %.1f ms/frame = %.2f fps", det_n,
                     1000 * det_time / det_n, det_n / det_time)
        source.close(); emitter.close()
        if per_frame:
            per_frame.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Zone people-counter (counts only, offline).")
    src = p.add_argument_group("input")
    src.add_argument("--video", help="video file (primary) or rtsp:// URL")
    src.add_argument("--webcam", type=int, default=None, help="webcam index (primary if no --video)")
    src.add_argument("--webcam-fallback", action="store_true",
                     help="if --video fails to open, use --webcam instead of stopping")
    src.add_argument("--loop", action="store_true", help="loop the video file at end-of-file")
    z = p.add_argument_group("zones and output")
    z.add_argument("--zones", help="zone JSON (normalised 0-1). Default: test split of the frame")
    z.add_argument("--draw-zones", metavar="PNG", help="write a preview of the zones on the first frame")
    z.add_argument("--draw-only", action="store_true", help="with --draw-zones: write the PNG and exit")
    z.add_argument("--interval", type=float, default=5.0, help="seconds per count window (default 5)")
    z.add_argument("--sample-fps", type=float, default=None,
                   help="frames analysed per second (default 2; 10 when an entrance line is configured)")
    z.add_argument("--stat", choices=STATS, default="p75", help="window statistic (default p75)")
    z.add_argument("--csv", help="CSV file to append (timestamp,zone,headcount,confidence)")
    z.add_argument("--csv-extra", action="store_true", help="add status,frames_used columns to the CSV")
    z.add_argument("--zones-file", metavar="JSONL",
                   help="dashboard heartbeat file: one {ts, zones, total} line per window (<= 5 s)")
    z.add_argument("--entries-csv", help="CSV for entrance counts: timestamp,zone,ins,outs,confidence")
    z.add_argument("--no-entries", action="store_true", help="ignore entrances in the zone JSON")
    z.add_argument("--min-crossing-frames", type=int, default=2,
                   help="frames a person must stay across the entrance line before it counts")
    z.add_argument("--start-time", help="ISO time of the file's first frame (default: now)")
    z.add_argument("--per-frame", metavar="JSONL", help="debug: per-frame zone counts (numbers only)")
    z.add_argument("--max-windows", type=int, default=0, help="stop after N windows (0 = no limit)")
    d = p.add_argument_group("detector")
    d.add_argument("--weights", default=str(DEFAULT_WEIGHTS), help="local .pt file (never downloaded)")
    d.add_argument("--device", default="auto", help="auto | cpu | cuda:0")
    d.add_argument("--conf", type=float, default=0.2, help="min box score (default 0.2; lower = more recall)")
    d.add_argument("--iou", type=float, default=0.6, help="NMS IoU (default 0.6; higher keeps overlapping people)")
    d.add_argument("--imgsz", type=int, default=1280,
                   help="inference size (default 1280; 640 is faster but misses small/far people)")
    d.add_argument("--tile", type=int, default=0, help="tile size px for tiled inference (0 = off, e.g. 640)")
    d.add_argument("--tile-overlap", type=float, default=0.25)
    d.add_argument("--max-det", type=int, default=500)
    d.add_argument("--low-conf", type=float, default=0.4, help="boxes below this score lower confidence")
    d.add_argument("--empty-confidence", type=float, default=0.4,
                   help="confidence given to a zone with no boxes at all (default 0.4; was 0.6)")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    if not args.video and args.webcam is None:
        log.error("give --video PATH or --webcam INDEX")
        return 2
    if args.interval <= 0 or (args.sample_fps is not None and args.sample_fps <= 0):
        log.error("--interval and --sample-fps must be > 0")
        return 2
    try:
        return run(args)
    except Exception as exc:  # last-resort guard: report, don't traceback-spam stdout
        log.exception("fatal: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
