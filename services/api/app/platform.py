"""Muse data platform — ingest, list sims, compare sim vs imaging (stub metrics)."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from sqlalchemy import select

from .platform_db import DrinkEvent, FlowCount, ImagingObservation, SimRun, init_platform_db, session_scope
from .sims import ALLOWLIST, get_job, list_jobs, start_sim


BANNED_META_KEYS = {
    "address",
    "venue_address",
    "guest",
    "guests_named",
    "phone",
    "email",
    "face",
    "faces",
    "embedding",
    "name",
    "names",
}


def _clean_meta(meta: dict[str, Any] | None) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in (meta or {}).items():
        if k.lower() in BANNED_META_KEYS:
            continue
        if isinstance(v, str) and len(v) > 500:
            continue
        out[k] = v
    return out


def _hash_path(path: str | None) -> str | None:
    if not path:
        return None
    return hashlib.sha256(path.encode("utf-8")).hexdigest()


def ensure_db() -> dict[str, Any]:
    return init_platform_db()


def record_sim_from_job(job: dict[str, Any]) -> dict[str, Any]:
    ensure_db()
    result = job.get("result") or {}
    score = result.get("score") if isinstance(result, dict) else None
    label = result.get("label", "estimate") if isinstance(result, dict) else "estimate"
    with session_scope() as session:
        row = SimRun(
            created_at=time.time(),
            kind=str(job.get("kind") or "unknown"),
            job_id=str(job.get("id") or ""),
            status=str(job.get("status") or "unknown"),
            params_json=json.dumps(job.get("params") or {}, separators=(",", ":")),
            result_json=json.dumps(result if isinstance(result, dict) else {"raw": result}, separators=(",", ":")),
            score=float(score) if isinstance(score, (int, float)) else None,
            label=str(label),
            source="muse",
        )
        session.add(row)
        session.flush()
        return _sim_row(row)


def queue_or_run_sim(kind: str = "smoke-stub", params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Start an allowlisted sim and store one row.

    Short stubs are waited out (under 2s) so the Data page does not freeze on
    "running". Heavy studio jobs return the queued snapshot and stay off the
    request thread.
    """
    job = start_sim(kind, params=params)
    heavy = bool(ALLOWLIST.get(kind, {}).get("heavy"))
    if not heavy:
        deadline = time.time() + 2.0
        while time.time() < deadline:
            current = get_job(str(job.get("id"))) or job
            job = current
            if current.get("status") in {"completed", "failed"}:
                break
            time.sleep(0.05)
    row = record_sim_from_job(job)
    return {"job": job, "sim_run": row}


def refresh_sim_from_job(job_id: str) -> dict[str, Any] | None:
    job = get_job(job_id)
    if not job:
        return None
    if job.get("status") in {"completed", "failed"}:
        return record_sim_from_job(job)
    return None


def list_sim_runs(limit: int = 40) -> list[dict[str, Any]]:
    ensure_db()
    with session_scope() as session:
        rows = session.scalars(select(SimRun).order_by(SimRun.id.desc()).limit(limit)).all()
        return [_sim_row(r) for r in rows]


def ingest_observation(
    *,
    crew_count: int | None = None,
    density_est: float | None = None,
    zone: str = "unknown",
    image_path: str | None = None,
    captured_at: float | None = None,
    meta: dict[str, Any] | None = None,
    label: str = "estimate",
) -> dict[str, Any]:
    """Imaging ingest stub — metadata + optional path hash only. No face recognition."""
    ensure_db()
    cleaned = _clean_meta(meta)
    with session_scope() as session:
        row = ImagingObservation(
            created_at=time.time(),
            captured_at=captured_at,
            crew_count=crew_count,
            density_est=density_est,
            zone=zone[:64],
            image_path_hash=_hash_path(image_path),
            meta_json=json.dumps(cleaned, separators=(",", ":")),
            label=label if label in {"confirmed", "estimate", "open"} else "estimate",
            note="no faces/PII stored",
        )
        session.add(row)
        session.flush()
        return _obs_row(row)


def ingest_drink_event(
    *,
    station: str = "island",
    drink_type: str = "unknown",
    quantity: float = 1.0,
    source: str = "sim",
    label: str = "estimate",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ensure_db()
    with session_scope() as session:
        row = DrinkEvent(
            created_at=time.time(),
            station=station[:64],
            drink_type=drink_type[:64],
            quantity=float(quantity),
            source=source[:64],
            label=label if label in {"confirmed", "estimate", "open"} else "estimate",
            meta_json=json.dumps(_clean_meta(meta), separators=(",", ":")),
        )
        session.add(row)
        session.flush()
        return {
            "id": row.id,
            "station": row.station,
            "drink_type": row.drink_type,
            "quantity": row.quantity,
            "source": row.source,
            "label": row.label,
        }


def ingest_flow_count(
    *,
    zone: str = "dance",
    count: int = 0,
    window_sec: int = 60,
    source: str = "sim",
    label: str = "estimate",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ensure_db()
    with session_scope() as session:
        row = FlowCount(
            created_at=time.time(),
            zone=zone[:64],
            count=int(count),
            window_sec=int(window_sec),
            source=source[:64],
            label=label if label in {"confirmed", "estimate", "open"} else "estimate",
            meta_json=json.dumps(_clean_meta(meta), separators=(",", ":")),
        )
        session.add(row)
        session.flush()
        return {
            "id": row.id,
            "zone": row.zone,
            "count": row.count,
            "window_sec": row.window_sec,
            "source": row.source,
            "label": row.label,
        }


def list_observations(limit: int = 40) -> list[dict[str, Any]]:
    ensure_db()
    with session_scope() as session:
        rows = session.scalars(
            select(ImagingObservation).order_by(ImagingObservation.id.desc()).limit(limit)
        ).all()
        return [_obs_row(r) for r in rows]


def compare_sim_vs_imaging(
    *,
    sim_run_id: int | None = None,
    zone: str | None = None,
) -> dict[str, Any]:
    """Simple metrics stub: compare latest (or chosen) sim score/crowd vs imaging density/count.

    All deltas labeled estimate until night-of ground truth exists.
    """
    ensure_db()
    with session_scope() as session:
        if sim_run_id is not None:
            sim = session.get(SimRun, sim_run_id)
        else:
            sim = session.scalars(select(SimRun).order_by(SimRun.id.desc()).limit(1)).first()
        obs_q = select(ImagingObservation).order_by(ImagingObservation.id.desc()).limit(20)
        obs_rows = list(session.scalars(obs_q).all())
        if zone:
            obs_rows = [o for o in obs_rows if o.zone == zone] or obs_rows

    live_jobs = list_jobs(limit=5)
    sim_payload = _sim_row(sim) if sim else None
    obs_payload = [_obs_row(o) for o in obs_rows[:5]]

    sim_guests = None
    if sim and sim.params_json:
        try:
            params = json.loads(sim.params_json)
            sim_guests = params.get("guests") or params.get("N")
        except json.JSONDecodeError:
            sim_guests = None

    obs_counts = [o.crew_count for o in obs_rows if o.crew_count is not None]
    obs_density = [o.density_est for o in obs_rows if o.density_est is not None]
    mean_count = sum(obs_counts) / len(obs_counts) if obs_counts else None
    mean_density = sum(obs_density) / len(obs_density) if obs_density else None

    delta_count = None
    if mean_count is not None and sim_guests is not None and isinstance(sim_guests, (int, float)):
        delta_count = float(mean_count) - float(sim_guests)

    return {
        "sim_run": sim_payload,
        "observations": obs_payload,
        "live_jobs": live_jobs,
        "metrics": {
            "sim_score": sim.score if sim else None,
            "sim_guests": sim_guests,
            "obs_mean_crew_count": mean_count,
            "obs_mean_density": mean_density,
            "delta_crew_vs_sim_guests": delta_count,
            "n_observations": len(obs_rows),
            "label": "estimate",
            "note": "Stub compare — not ground truth. Camera hardware not ordered.",
        },
        "privacy": "counts/features/hashes only; no face recognition in MVP",
    }


def _sim_row(row: SimRun) -> dict[str, Any]:
    return {
        "id": row.id,
        "created_at": row.created_at,
        "kind": row.kind,
        "job_id": row.job_id,
        "status": row.status,
        "score": row.score,
        "label": row.label,
        "source": row.source,
        "params": _safe_json(row.params_json),
        "result": _safe_json(row.result_json),
    }


def _obs_row(row: ImagingObservation) -> dict[str, Any]:
    return {
        "id": row.id,
        "created_at": row.created_at,
        "captured_at": row.captured_at,
        "crew_count": row.crew_count,
        "density_est": row.density_est,
        "zone": row.zone,
        "image_path_hash": row.image_path_hash,
        "label": row.label,
        "note": row.note,
        "meta": _safe_json(row.meta_json),
    }


def _safe_json(raw: str) -> Any:
    try:
        return json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
