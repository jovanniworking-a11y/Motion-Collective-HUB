"""Sim job runners — wrap studio Python scripts safely; stub by default."""

from __future__ import annotations

import json
import subprocess
import threading
import time
import uuid
from typing import Any

from .activity import clear_live, set_live
from .config import SIM_EXECUTE, STUDIO_DIR
from .usage import log_usage

ALLOWLIST: dict[str, dict[str, Any]] = {
    "chk": {"script": "_chk.py", "argv": [], "description": "Determinism spot check.", "heavy": True},
    "err": {"script": "_err.py", "argv": [], "description": "Studio error probe.", "heavy": True},
    "night": {"script": "_night2.py", "argv": [], "description": "Night crowd sim.", "heavy": True},
    "all-baths-1": {"script": "_all2.py", "argv": ["1"], "description": "optimizeEverything baths=1.", "heavy": True},
    "all-baths-2": {"script": "_all2.py", "argv": ["2"], "description": "optimizeEverything baths=2.", "heavy": True},
    "smoke-stub": {"script": None, "argv": [], "description": "Safe no-op for CI/UI smoke.", "heavy": False},
}

_JOBS: dict[str, dict[str, Any]] = {}
_LOCK = threading.Lock()


def list_sim_kinds() -> list[dict[str, Any]]:
    return [
        {
            "id": k,
            "script": v["script"],
            "description": v["description"],
            "heavy": v["heavy"],
            "execute_enabled": SIM_EXECUTE and v["script"] is not None,
        }
        for k, v in ALLOWLIST.items()
    ]


def get_job(job_id: str) -> dict[str, Any] | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        return dict(job) if job else None


def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    with _LOCK:
        jobs = sorted(_JOBS.values(), key=lambda j: j.get("created_at", 0), reverse=True)
        return [dict(j) for j in jobs[:limit]]


def _update(job_id: str, **fields: Any) -> None:
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id].update(fields)
            _JOBS[job_id]["updated_at"] = time.time()
            set_live(
                job_id,
                {
                    "id": job_id,
                    "agent_id": "muse",
                    "title": f"sim · {_JOBS[job_id].get('kind')}",
                    "status": _JOBS[job_id].get("status"),
                    "action": "sim",
                },
            )


def _run_real(job_id: str, script: str, argv: list[str]) -> None:
    try:
        proc = subprocess.run(
            ["python3", str(STUDIO_DIR / script), *argv],
            cwd=str(STUDIO_DIR),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        _update(
            job_id,
            status="completed" if proc.returncode == 0 else "failed",
            returncode=proc.returncode,
            stdout=(proc.stdout or "")[-4000:],
            stderr=(proc.stderr or "")[-2000:],
        )
    except subprocess.TimeoutExpired:
        _update(job_id, status="failed", error="timeout after 120s")
    except OSError as exc:
        _update(job_id, status="failed", error=str(exc))
    finally:
        clear_live(job_id)


def _run_stub(job_id: str, kind: str) -> None:
    time.sleep(0.15)
    report: dict[str, Any] = {
        "kind": kind,
        "mode": "stub",
        "note": "MOTION_SIM_EXECUTE not set — safe stub.",
        "script": ALLOWLIST[kind]["script"],
        "studio_dir": str(STUDIO_DIR),
        "score": None,
        "label": "estimate",
    }
    for name in ("_report_b1.json", "_report_b2.json"):
        p = STUDIO_DIR / name
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                final = data.get("final") or {}
                report["existing_report"] = name
                report["score"] = final.get("score")
                report["label"] = "confirmed" if final.get("score") is not None else "estimate"
            except (OSError, json.JSONDecodeError):
                pass
            break
    _update(job_id, status="completed", result=report, returncode=0)
    clear_live(job_id)


def start_sim(kind: str = "smoke-stub", *, params: dict[str, Any] | None = None) -> dict[str, Any]:
    if kind not in ALLOWLIST:
        raise KeyError(f"unknown sim kind: {kind}")
    spec = ALLOWLIST[kind]
    job_id = f"sim-{uuid.uuid4().hex[:10]}"
    job = {
        "id": job_id,
        "kind": kind,
        "script": spec["script"],
        "params": params or {},
        "status": "queued",
        "created_at": time.time(),
        "updated_at": time.time(),
        "execute": bool(SIM_EXECUTE and spec["script"]),
    }
    with _LOCK:
        _JOBS[job_id] = job
    set_live(
        job_id,
        {"id": job_id, "agent_id": "muse", "title": f"sim · {kind}", "status": "queued", "action": "sim"},
    )
    log_usage(
        agent_id="muse",
        area="muse",
        model="sim-runner",
        action=f"sim:{kind}",
        label="estimate",
        meta=job_id,
    )

    def worker() -> None:
        _update(job_id, status="running")
        if SIM_EXECUTE and spec["script"]:
            if not (STUDIO_DIR / spec["script"]).exists():
                _update(job_id, status="failed", error=f"missing script: {spec['script']}")
                clear_live(job_id)
                return
            _run_real(job_id, spec["script"], list(spec["argv"]))
        else:
            _run_stub(job_id, kind)

    threading.Thread(target=worker, daemon=True).start()
    return dict(job)
