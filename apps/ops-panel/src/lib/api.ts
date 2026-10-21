/** Client for MOTION control-plane FastAPI backend. */

function resolveApiBase(): string {
  // In the browser, always use same-origin relative URLs. The hosting
  // platform's rewrites route /api/*, /health, /studio/embed to the api
  // service, so this works on production, previews, and custom domains
  // with zero env config. A baked NEXT_PUBLIC_* URL goes stale or points
  // at localhost — that was the "Failed to fetch" outage.
  if (typeof window !== "undefined") return "";
  const raw =
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.NEXT_PUBLIC_MOTION_API_URL ||
    "http://127.0.0.1:8787";
  return raw.replace(/\/$/, "");
}

export function apiBase(): string {
  return resolveApiBase();
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
  dataHealth: () =>
    req<{ ok: boolean; database_url_scheme: string; tables: string[] }>("/api/data/health"),
  dataSims: () => req<{ sims: unknown[]; label: string }>("/api/data/sims"),
  dataObservations: () => req<{ observations: unknown[] }>("/api/data/observations"),
  dataRunSim: (kind: string, params: Record<string, unknown> = {}) =>
    req<{ job: { id: string; status: string }; sim_run: unknown }>("/api/data/sims/run", {
      method: "POST",
      body: JSON.stringify({ kind, params }),
    }),
  dataIngestObservation: (body: {
    crew_count?: number;
    density_est?: number;
    zone?: string;
    image_path?: string;
    label?: string;
  }) =>
    req<{ observation: unknown }>("/api/data/observations", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  dataIngestFlow: (body: { zone?: string; count?: number, label?: string }) =>
    req<{ flow_count: unknown }>("/api/data/flow", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  dataCompare: () => req<{ metrics: Record<string, unknown> }>("/api/data/compare"),
};
