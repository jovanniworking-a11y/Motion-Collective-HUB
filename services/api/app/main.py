"""MOTION Collective control-plane — FastAPI entry."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__
from .activity import activity_feed
from .chat import chat, history
from .config import CORS_ORIGINS, STUDIO_DIR
from .routing import AGENT_REGISTRY, MODEL_ROUTES, get_agent, route_for
from .sims import get_job, list_jobs, list_sim_kinds, start_sim
from .studio import load_layout, patch_layout, save_layout, studio_paths
from .usage import init_usage_db, usage_summary


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_usage_db()
    yield


app = FastAPI(
    title="MOTION Control Plane",
    description="Agent command center + Night-Of ops + Muse sims. Draft only.",
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


if STUDIO_DIR.exists():
    app.mount("/studio/static", StaticFiles(directory=str(STUDIO_DIR), html=False), name="studio-static")

    @app.get("/studio/embed")
    def studio_embed() -> FileResponse:
        index = STUDIO_DIR / "index.html"
        if not index.exists():
            raise HTTPException(404, "studio index.html missing")
        return FileResponse(index, media_type="text/html")
