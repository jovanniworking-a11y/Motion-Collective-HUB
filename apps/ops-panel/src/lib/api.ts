/** Client for MOTION control-plane FastAPI backend. */

const CONFIGURED = process.env.NEXT_PUBLIC_MOTION_API_URL?.replace(/\/$/, "");

/** Configured URL wins; otherwise local dev talks to :8787 and a deployed panel uses its own origin (Vercel rewrites). */
export function apiBase(): string {
  if (CONFIGURED !== undefined && CONFIGURED !== "") return CONFIGURED;
  if (typeof window !== "undefined" && !["localhost", "127.0.0.1"].includes(window.location.hostname)) return "";
  return "http://127.0.0.1:8787";
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
    credentials: "include",
  });
  if (res.status === 401 && typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.assign(`/login?next=${encodeURIComponent(window.location.pathname)}`);
  }
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
};
