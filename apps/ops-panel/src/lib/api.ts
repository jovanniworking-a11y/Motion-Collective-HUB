/** Client for MOTION control-plane FastAPI backend. */

const DEFAULT_BASE =
  process.env.NEXT_PUBLIC_MOTION_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8787";

export function apiBase(): string {
  return DEFAULT_BASE;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${path}: ${text.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

export type Agent = {
  id: string;
  area: string;
  name: string;
  channel: string;
  description: string;
  default_model: string;
  worker: string;
  capabilities: string[];
};

export type ChatMessage = {
  id: string;
  role: string;
  action?: string;
  content: string;
  ts: number;
  model?: string;
  provider?: string;
};

export const api = {
  health: () => req<{ ok: boolean }>("/health"),
  agents: () => req<{ agents: Agent[] }>("/api/agents"),
  agent: (id: string) =>
    req<{ agent: Agent; history: ChatMessage[] }>(`/api/agents/${id}`),
  chat: (id: string, prompt: string, action: "prompt" | "correct" | "form" = "prompt") =>
    req<{ message: ChatMessage; thread: ChatMessage[]; route: { model: string; why: string } }>(
      `/api/agents/${id}/chat`,
      { method: "POST", body: JSON.stringify({ prompt, action }) },
    ),
  usage: () =>
    req<{
      by_bot: { agent_id: string; area: string; model: string; calls: number; tokens_in: number; tokens_out: number }[];
      recent: { id: number; ts: number; agent_id: string; action: string; model: string; label: string }[];
      totals: { calls: number; tokens_in: number; tokens_out: number; label: string };
    }>("/api/usage"),
  activity: () =>
    req<{
      feed: { kind: string; agent_id?: string; title: string; status: string }[];
      board_count: number;
      outbox_count: number;
      live_count: number;
      label: string;
    }>("/api/activity"),
  studio: () =>
    req<{
      paths: { index_exists: boolean };
      layout: { scen: Record<string, unknown>; sim_params: Record<string, unknown>; items: unknown[] };
    }>("/api/studio"),
  patchLayout: (partial: Record<string, unknown>) =>
    req<{ layout: Record<string, unknown> }>("/api/studio/layout", {
      method: "PATCH",
      body: JSON.stringify(partial),
    }),
  sims: () => req<{ kinds: { id: string; description: string }[] }>("/api/sims"),
  runSim: (kind: string) =>
    req<{ job: { id: string; status: string } }>("/api/sims/run", {
      method: "POST",
      body: JSON.stringify({ kind }),
    }),
  simJob: (id: string) =>
    req<{ job: { id: string; status: string; result?: unknown; error?: string } }>(
      `/api/sims/jobs/${id}`,
    ),
  studioEmbedUrl: () => `${apiBase()}/studio/embed`,
  occupancyBoard: () =>
    req<{
      zones: {
        id: number | null;
        zone: string;
        count: number | null;
        confidence: number | null;
        count_quality: string;
        label: "confirmed" | "estimate" | "open";
        age_sec: number | null;
        camera_id: string | null;
      }[];
      house_total: number;
      house_note: string;
      sim_dance_peak: number;
      sim_dance_label: "confirmed" | "estimate" | "open";
      sim_guests: number;
      cap: number;
      cap_label: "confirmed" | "estimate" | "open";
      polygons_label: "confirmed" | "estimate" | "open";
      spot_queue: { id: number; zone: string; count: number; count_quality: string; age_sec: number }[];
      scorecard: {
        verdict: string;
        dance_peak?: number;
        dance_peak_error?: number;
        sim_dance_peak: number;
        label: "confirmed" | "estimate" | "open";
        jam_proxy_min?: number;
        jam_verdict?: string;
      };
    }>("/api/data/occupancy/board"),
  occupancySpot: (id: number, count: number) =>
    req<{ sample: { id: number; count: number; label: string } }>(`/api/data/occupancy/${id}/spot`, {
      method: "POST",
      body: JSON.stringify({ count }),
    }),
};
