"""MOTION Collective control-plane — FastAPI entry."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from . import __version__
from .activity import activity_feed
from .chat import chat, history
from .config import CORS_ORIGINS, STUDIO_DIR
from .platform import (
    compare_sim_vs_imaging,
    ensure_db,
    ingest_drink_event,
    ingest_flow_count,
    ingest_observation,
    list_observations,
    list_sim_runs,
    queue_or_run_sim,
    refresh_sim_from_job,
)
from .routing import AGENT_REGISTRY, MODEL_ROUTES, get_agent, route_for
from .sims import get_job, list_jobs, list_sim_kinds, start_sim
from .studio import load_layout, patch_layout, save_layout, studio_paths
from .occupancy import (
    count_frame,
    latest_board,
    list_samples,
    rollup,
    save_samples,
    scorecard,
    spot_check,
)
from .usage import init_usage_db, usage_summary


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_usage_db()
    ensure_db()
    yield


app = FastAPI(
    title="MOTION Control Plane",
    description="Agent command center + Night-Of ops + Muse sims + data compare. Draft only.",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatIn(BaseModel):
    prompt: str = Field(default="", max_length=8000)
    action: str = Field(default="prompt", pattern="^(prompt|correct|form)$")


class LayoutIn(BaseModel):
    layout: dict[str, Any]


class LayoutPatchIn(BaseModel):
    scen: dict[str, Any] | None = None
    sim_params: dict[str, Any] | None = None
    items: list[dict[str, Any]] | None = None


class SimIn(BaseModel):
    kind: str = "smoke-stub"
    params: dict[str, Any] = Field(default_factory=dict)


class ObservationIn(BaseModel):
    crew_count: int | None = None
    density_est: float | None = None
    zone: str = "unknown"
    image_path: str | None = Field(default=None, description="Optional path; stored as SHA-256 hash only")
    captured_at: float | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    label: str = Field(default="estimate", pattern="^(confirmed|estimate|open)$")


class DrinkEventIn(BaseModel):
    station: str = "island"
    drink_type: str = "unknown"
    quantity: float = 1.0
    source: str = "sim"
    label: str = Field(default="estimate", pattern="^(confirmed|estimate|open)$")
    meta: dict[str, Any] = Field(default_factory=dict)


class FlowCountIn(BaseModel):
    zone: str = "dance"
    count: int = 0
    window_sec: int = 60
    source: str = "sim"
    label: str = Field(default="estimate", pattern="^(confirmed|estimate|open)$")
    meta: dict[str, Any] = Field(default_factory=dict)


class CompareQuery(BaseModel):
    sim_run_id: int | None = None
    zone: str | None = None


class OccupancyIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    captured_at: float
    zone: str = Field(pattern="^(living|dance|kitchen|hallway|balcony)$")
    count: int = Field(ge=0, le=500)
    confidence: float = Field(ge=0, le=1)
    count_quality: str = Field(pattern="^(ok|low|no_feed)$")
    camera_id: str = Field(pattern="^(wyze_living|gopro_booth|action_2|camcorder|iphone_spot)$")
    sample_kind: str = Field(pattern="^(primary|validation|spot)$")
    label: str = Field(default="estimate", pattern="^(confirmed|estimate|open)$")


class OccupancyBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    samples: list[OccupancyIn]


class DetectionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conf: float = Field(ge=0, le=1)
    x1: float
    y1: float
    x2: float
    y2: float


class CountIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    captured_at: float
    camera_id: str = Field(pattern="^(wyze_living|gopro_booth|action_2|camcorder|iphone_spot)$")
    sample_kind: str = Field(default="primary", pattern="^(primary|validation|spot)$")
    zones: list[str] | None = None
    detections: list[DetectionIn]


class SpotIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    count: int = Field(ge=0, le=500)


class RouteQuery(BaseModel):
    area: str
    task_kind: str = ""


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "motion-control-plane", "version": __version__, "draft_only": True}


@app.get("/api/agents")
def api_agents() -> dict[str, Any]:
    return {"agents": AGENT_REGISTRY, "count": len(AGENT_REGISTRY)}


@app.get("/api/agents/{agent_id}")
def api_agent(agent_id: str) -> dict[str, Any]:
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(404, f"unknown agent: {agent_id}")
    return {"agent": agent, "history": history(agent_id)}


@app.post("/api/agents/{agent_id}/chat")
def api_chat(agent_id: str, body: ChatIn) -> dict[str, Any]:
    if not get_agent(agent_id):
        raise HTTPException(404, f"unknown agent: {agent_id}")
    try:
        return chat(agent_id, body.prompt, action=body.action)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/usage")
def api_usage() -> dict[str, Any]:
    return usage_summary()


@app.get("/api/activity")
def api_activity(limit: int = 40) -> dict[str, Any]:
    return activity_feed(limit=min(max(limit, 1), 100))


@app.get("/api/routing")
def api_routing() -> dict[str, Any]:
    return {
        "routes": MODEL_ROUTES,
        "agents": [
            {"id": a["id"], "area": a["area"], "default_model": a["default_model"], "worker": a["worker"]}
            for a in AGENT_REGISTRY
        ],
        "doc": "See services/api/MODEL_ROUTING.md",
    }


@app.post("/api/routing/resolve")
def api_route_resolve(body: RouteQuery) -> dict[str, Any]:
    return {"route": route_for(body.area, body.task_kind)}


@app.get("/api/studio")
def api_studio() -> dict[str, Any]:
    return {"paths": studio_paths(), "layout": load_layout()}


@app.get("/api/studio/layout")
def api_layout_get() -> dict[str, Any]:
    return {"layout": load_layout()}


@app.put("/api/studio/layout")
def api_layout_put(body: LayoutIn) -> dict[str, Any]:
    return {"layout": save_layout(body.layout)}


@app.patch("/api/studio/layout")
def api_layout_patch(body: LayoutPatchIn) -> dict[str, Any]:
    partial = {k: v for k, v in body.model_dump().items() if v is not None}
    return {"layout": patch_layout(partial)}


@app.get("/api/sims")
def api_sims() -> dict[str, Any]:
    return {"kinds": list_sim_kinds(), "jobs": list_jobs()}


@app.post("/api/sims/run")
def api_sims_run(body: SimIn) -> dict[str, Any]:
    try:
        job = start_sim(body.kind, params=body.params)
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"job": job}


@app.get("/api/sims/jobs/{job_id}")
def api_sim_job(job_id: str) -> dict[str, Any]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, f"unknown job: {job_id}")
    return {"job": job}


@app.get("/api/data/health")
def api_data_health() -> dict[str, Any]:
    return ensure_db()


@app.get("/api/data/sims")
def api_data_sims(limit: int = 40) -> dict[str, Any]:
    return {"sims": list_sim_runs(limit=min(max(limit, 1), 100)), "label": "estimate"}


@app.post("/api/data/sims/run")
def api_data_sims_run(body: SimIn) -> dict[str, Any]:
    try:
        return queue_or_run_sim(body.kind, params=body.params)
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/data/sims/jobs/{job_id}/persist")
def api_data_sim_persist(job_id: str) -> dict[str, Any]:
    row = refresh_sim_from_job(job_id)
    if not row:
        raise HTTPException(404, f"job not found or not finished: {job_id}")
    return {"sim_run": row}


@app.post("/api/data/observations")
def api_data_observation(body: ObservationIn) -> dict[str, Any]:
    return {
        "observation": ingest_observation(
            crew_count=body.crew_count,
            density_est=body.density_est,
            zone=body.zone,
            image_path=body.image_path,
            captured_at=body.captured_at,
            meta=body.meta,
            label=body.label,
        )
    }


@app.get("/api/data/observations")
def api_data_observations(limit: int = 40) -> dict[str, Any]:
    return {"observations": list_observations(limit=min(max(limit, 1), 100))}


@app.post("/api/data/drinks")
def api_data_drinks(body: DrinkEventIn) -> dict[str, Any]:
    return {"drink_event": ingest_drink_event(**body.model_dump())}


@app.post("/api/data/flow")
def api_data_flow(body: FlowCountIn) -> dict[str, Any]:
    return {"flow_count": ingest_flow_count(**body.model_dump())}


@app.post("/api/data/compare")
def api_data_compare(body: CompareQuery) -> dict[str, Any]:
    return compare_sim_vs_imaging(sim_run_id=body.sim_run_id, zone=body.zone)


@app.get("/api/data/compare")
def api_data_compare_get(sim_run_id: int | None = None, zone: str | None = None) -> dict[str, Any]:
    return compare_sim_vs_imaging(sim_run_id=sim_run_id, zone=zone)


@app.post("/api/data/occupancy")
def api_occupancy_post(body: OccupancyIn) -> dict[str, Any]:
    return {"sample": save_samples([body.model_dump()])[0]}


@app.post("/api/data/occupancy/batch")
def api_occupancy_batch(body: OccupancyBatch) -> dict[str, Any]:
    return {"samples": save_samples([s.model_dump() for s in body.samples])}


@app.post("/api/data/occupancy/count")
def api_occupancy_count(body: CountIn) -> dict[str, Any]:
    try:
        counted = count_frame(
            [d.model_dump() for d in body.detections],
            camera_id=body.camera_id,
            zones=body.zones,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    samples = save_samples(
        [
            {
                **row,
                "captured_at": body.captured_at,
                "camera_id": body.camera_id,
                "sample_kind": body.sample_kind,
                "label": "estimate",
            }
            for row in counted
        ]
    )
    return {"samples": samples}


@app.get("/api/data/occupancy")
def api_occupancy_list(zone: str | None = None, limit: int = 200) -> dict[str, Any]:
    return {"samples": list_samples(zone=zone, limit=min(max(limit, 1), 500))}


@app.get("/api/data/occupancy/board")
def api_occupancy_board() -> dict[str, Any]:
    return latest_board()


@app.get("/api/data/occupancy/rollup")
def api_occupancy_rollup(bucket_sec: int = 60) -> dict[str, Any]:
    return rollup(bucket_sec=min(max(bucket_sec, 10), 3600))


@app.get("/api/data/occupancy/scorecard")
def api_occupancy_scorecard() -> dict[str, Any]:
    return scorecard()


@app.post("/api/data/occupancy/{sample_id}/spot")
def api_occupancy_spot(sample_id: int, body: SpotIn) -> dict[str, Any]:
    try:
        return {"sample": spot_check(sample_id, body.count)}
    except KeyError as exc:
        raise HTTPException(404, f"unknown sample: {sample_id}") from exc


if STUDIO_DIR.exists():
    app.mount("/studio/static", StaticFiles(directory=str(STUDIO_DIR), html=False), name="studio-static")

    @app.get("/studio/embed")
    def studio_embed() -> FileResponse:
        index = STUDIO_DIR / "index.html"
        if not index.exists():
            raise HTTPException(404, "studio index.html missing")
        return FileResponse(index, media_type="text/html")
