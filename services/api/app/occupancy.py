"""Zone counts only. Boxes are counted in memory and never stored."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from sqlalchemy import select

from .platform_db import OccupancySample, init_platform_db, session_scope

ZONES = ("living", "dance", "kitchen", "hallway", "balcony")
HOUSE_ZONES = ("living", "kitchen", "hallway", "balcony")
CAMERAS = ("wyze_living", "gopro_booth", "action_2", "camcorder", "iphone_spot")
SAMPLE_KINDS = ("primary", "validation", "spot")
QUALITIES = ("ok", "low", "no_feed")
LABELS = ("confirmed", "estimate", "open")

# Confirmed from data/sims/2026-10-16_360_sweep.json (50 guests, 12-seed mean).
SIM_DANCE_PEAK = 30.42
SIM_GUESTS = 50
SIM_JAM_MIN = 15.04
# Night plan from the 20 Oct cap note. Sim was not re-run at this headcount.
CAP = 70
HEADCOUNT_LO = 45
HEADCOUNT_HI = 55
PROVE_ABS = 5.0
BREAK_ABS = 10.0
BREAK_DANCE = 45
JAM_DANCE = 28
JAM_HALL = 4
JAM_BREAK_MIN = 25.0
WINDOW_SEC = 45 * 60
CONF_MIN = 0.35
OVERLAP_LOW = 0.25
SPOT_MOD = 50

CAMERA_ZONES = {
    "wyze_living": ("living", "dance"),
    "gopro_booth": ("dance",),
    "action_2": ("kitchen", "hallway"),
    "camcorder": ("living", "dance"),
    "iphone_spot": ZONES,
}

_ZONES_PATH = Path(__file__).with_name("zones.json")


def load_polygons() -> dict[str, list[list[float]]]:
    raw = json.loads(_ZONES_PATH.read_text(encoding="utf-8"))
    polys = raw["polygons"]
    missing = [z for z in ZONES if z not in polys]
    if missing:
        raise ValueError(f"zones.json missing {missing}")
    return polys


def point_in_poly(x: float, y: float, poly: list[list[float]]) -> bool:
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            denom = (yj - yi) or 1e-12
            if x < (xj - xi) * (y - yi) / denom + xi:
                inside = not inside
        j = i
    return inside


def _iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    iw = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    ih = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union else 0.0


def _mean_iou(boxes: list[tuple[float, float, float, float]]) -> float:
    if len(boxes) < 2:
        return 0.0
    total = 0.0
    n = 0
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            total += _iou(a, b)
            n += 1
    return total / n if n else 0.0


def count_frame(
    detections: list[dict[str, float]],
    *,
    camera_id: str,
    zones: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Turn person boxes into per-zone counts. Boxes are not returned."""
    allowed = list(zones) if zones is not None else list(CAMERA_ZONES[camera_id])
    unknown = [z for z in allowed if z not in ZONES]
    if unknown:
        raise ValueError(f"unknown zone: {unknown[0]}")
    polys = load_polygons()
    kept: list[dict[str, Any]] = []
    rejected_conf: list[float] = []
    for det in detections:
        conf = float(det["conf"])
        box = (float(det["x1"]), float(det["y1"]), float(det["x2"]), float(det["y2"]))
        if conf < CONF_MIN:
            rejected_conf.append(conf)
            continue
        foot_x = (box[0] + box[2]) / 2
        foot_y = box[3]
        hits = [z for z in allowed if point_in_poly(foot_x, foot_y, polys[z])]
        if "dance" in hits and "living" in allowed and "living" not in hits:
            hits.append("living")
        if not hits:
            continue
        kept.append({"conf": conf, "box": box, "zones": hits})

    rows: list[dict[str, Any]] = []
    highest_rejected = max(rejected_conf) if rejected_conf else 0.0
    for zone in allowed:
        members = [d for d in kept if zone in d["zones"]]
        count = len(members)
        if count == 0:
            confidence = max(0.50, 1.0 - highest_rejected) if not kept else 0.50
        else:
            confidence = sum(d["conf"] for d in members) / count
        overlap = _mean_iou([d["box"] for d in members])
        quality = "low" if overlap > OVERLAP_LOW else "ok"
        rows.append(
            {
                "zone": zone,
                "count": count,
                "confidence": round(confidence, 4),
                "count_quality": quality,
            }
        )
    return rows


def house_total(counts: dict[str, int]) -> int:
    return sum(int(counts.get(z, 0)) for z in HOUSE_ZONES)


def _row_dict(row: OccupancySample, now: float | None = None) -> dict[str, Any]:
    now = time.time() if now is None else now
    return {
        "id": row.id,
        "captured_at": row.captured_at,
        "zone": row.zone,
        "count": row.count,
        "confidence": row.confidence,
        "count_quality": row.count_quality,
        "camera_id": row.camera_id,
        "sample_kind": row.sample_kind,
        "label": row.label,
        "age_sec": round(now - row.captured_at, 1),
        "needs_spot": row.label != "confirmed" and (row.count_quality == "low" or row.id % SPOT_MOD == 0),
    }


def save_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    init_platform_db()
    now = time.time()
    with session_scope() as session:
        rows = []
        for sample in samples:
            row = OccupancySample(
                captured_at=float(sample["captured_at"]),
                zone=sample["zone"],
                count=int(sample["count"]),
                confidence=float(sample["confidence"]),
                count_quality=sample["count_quality"],
                camera_id=sample["camera_id"],
                sample_kind=sample["sample_kind"],
                label=sample["label"],
            )
            session.add(row)
            rows.append(row)
        session.flush()
        return [_row_dict(r, now) for r in rows]


def list_samples(*, zone: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    init_platform_db()
    now = time.time()
    with session_scope() as session:
        stmt = select(OccupancySample).order_by(OccupancySample.id.desc()).limit(limit)
        if zone:
            stmt = stmt.where(OccupancySample.zone == zone)
        rows = list(session.scalars(stmt).all())
        return [_row_dict(r, now) for r in rows]


def latest_board() -> dict[str, Any]:
    init_platform_db()
    now = time.time()
    with session_scope() as session:
        rows = list(
            session.scalars(
                select(OccupancySample)
                .where(OccupancySample.sample_kind == "primary")
                .order_by(OccupancySample.captured_at.desc(), OccupancySample.id.desc())
            ).all()
        )
        spot_rows = list(
            session.scalars(
                select(OccupancySample).order_by(OccupancySample.captured_at.desc()).limit(400)
            ).all()
        )
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.zone not in latest:
            latest[row.zone] = _row_dict(row, now)
    counts = {z: int(latest[z]["count"]) if z in latest else 0 for z in ZONES}
    queue = []
    for row in spot_rows:
        item = _row_dict(row, now)
        if item["needs_spot"]:
            queue.append(item)
        if len(queue) >= 40:
            break
    return {
        "zones": [latest.get(z) or _empty_zone(z, now) for z in ZONES],
        "house_total": house_total(counts),
        "house_note": "living + kitchen + hallway + balcony. dance is inside living.",
        "sim_dance_peak": SIM_DANCE_PEAK,
        "sim_dance_label": "confirmed",
        "sim_guests": SIM_GUESTS,
        "sim_guests_label": "confirmed",
        "cap": CAP,
        "cap_label": "confirmed",
        "polygons_label": "open",
        "spot_queue": queue,
        "scorecard": scorecard(),
    }


def _empty_zone(zone: str, now: float) -> dict[str, Any]:
    return {
        "id": None,
        "captured_at": None,
        "zone": zone,
        "count": None,
        "confidence": None,
        "count_quality": "no_feed",
        "camera_id": None,
        "sample_kind": "primary",
        "label": "open",
        "age_sec": None,
        "needs_spot": False,
        "as_of": now,
    }


def spot_check(sample_id: int, count: int) -> dict[str, Any]:
    init_platform_db()
    now = time.time()
    with session_scope() as session:
        row = session.get(OccupancySample, sample_id)
        if row is None:
            raise KeyError(sample_id)
        row.count = int(count)
        row.label = "confirmed"
        session.flush()
        return _row_dict(row, now)


def rollup(bucket_sec: int = 60) -> dict[str, Any]:
    init_platform_db()
    with session_scope() as session:
        rows = list(
            session.scalars(
                select(OccupancySample).where(OccupancySample.sample_kind == "primary")
            ).all()
        )
    buckets: dict[tuple[int, str], list[OccupancySample]] = {}
    for row in rows:
        key = (int(row.captured_at // bucket_sec) * bucket_sec, row.zone)
        buckets.setdefault(key, []).append(row)
    out = []
    for (start, zone), group in sorted(buckets.items()):
        out.append(
            {
                "bucket_start": start,
                "zone": zone,
                "count": max(r.count for r in group),
                "confidence": round(sum(r.confidence for r in group) / len(group), 4),
                "samples": len(group),
                "label": "estimate",
            }
        )
    return {"bucket_sec": bucket_sec, "rows": out, "label": "estimate"}


def _frames(rows: list[OccupancySample]) -> list[dict[str, Any]]:
    grouped: dict[int, dict[str, OccupancySample]] = {}
    for row in rows:
        if row.sample_kind != "primary":
            continue
        grouped.setdefault(int(row.captured_at), {})[row.zone] = row
    frames = []
    for ts, zones in sorted(grouped.items()):
        if any(z not in zones for z in HOUSE_ZONES):
            continue
        counts = {z: zones[z].count for z in zones}
        frames.append(
            {
                "ts": ts,
                "house": house_total(counts),
                "dance": counts.get("dance", 0),
                "hallway": counts.get("hallway", 0),
            }
        )
    return frames


def scorecard() -> dict[str, Any]:
    init_platform_db()
    with session_scope() as session:
        rows = list(session.scalars(select(OccupancySample)).all())
    frames = _frames(rows)
    if not frames:
        return {
            "verdict": "inconclusive_headcount",
            "reason": "no primary frame with living, kitchen, hallway, and balcony",
            "sim_dance_peak": SIM_DANCE_PEAK,
            "sim_dance_label": "confirmed",
            "sim_guests": SIM_GUESTS,
            "label": "open",
        }
    best_start = frames[0]["ts"]
    best_mean = -1.0
    for frame in frames:
        window = [f for f in frames if frame["ts"] - WINDOW_SEC <= f["ts"] <= frame["ts"]]
        mean_house = sum(f["house"] for f in window) / len(window)
        if mean_house > best_mean:
            best_mean = mean_house
            best_start = window[0]["ts"]
    window = [f for f in frames if best_start <= f["ts"] <= best_start + WINDOW_SEC]
    band = [f for f in window if HEADCOUNT_LO <= f["house"] <= HEADCOUNT_HI]
    if not band:
        return {
            "verdict": "inconclusive_headcount",
            "reason": "busiest 45 min has no frame with house total 45–55",
            "busiest_window_start": best_start,
            "sim_dance_peak": SIM_DANCE_PEAK,
            "sim_dance_label": "confirmed",
            "sim_guests": SIM_GUESTS,
            "cap": CAP,
            "label": "open",
        }
    peak_frame = max(band, key=lambda f: f["dance"])
    dance_peak = peak_frame["dance"]
    error = round(dance_peak - SIM_DANCE_PEAK, 2)
    if dance_peak > BREAK_DANCE and peak_frame["house"] <= HEADCOUNT_HI:
        verdict = "break"
    elif abs(error) > BREAK_ABS:
        verdict = "break"
    elif abs(error) <= PROVE_ABS:
        verdict = "prove"
    else:
        verdict = "inconclusive"
    jam_buckets = {
        f["ts"] // 60
        for f in band
        if f["dance"] >= JAM_DANCE and f["hallway"] >= JAM_HALL
    }
    jam_min = float(len(jam_buckets))
    jam_verdict = "break" if jam_min > JAM_BREAK_MIN else "prove"
    return {
        "verdict": verdict,
        "dance_peak": dance_peak,
        "dance_peak_error": error,
        "sim_dance_peak": SIM_DANCE_PEAK,
        "sim_dance_label": "confirmed",
        "sim_guests": SIM_GUESTS,
        "sim_guests_label": "confirmed",
        "house_at_peak": peak_frame["house"],
        "band": [HEADCOUNT_LO, HEADCOUNT_HI],
        "band_label": "estimate",
        "busiest_window_start": best_start,
        "jam_proxy_min": jam_min,
        "jam_proxy_label": "estimate",
        "sim_jam_min": SIM_JAM_MIN,
        "sim_jam_label": "confirmed",
        "jam_verdict": jam_verdict,
        "restroom_wait": "unscored",
        "cap": CAP,
        "cap_label": "confirmed",
        "label": "estimate" if verdict in {"prove", "break"} else "open",
    }
