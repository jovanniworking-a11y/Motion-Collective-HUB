/**
 * LIVE OPS helpers — pure, testable.
 *
 * Data source: live-ops/counter/server.py (Chaka's door counter, LAN only).
 *   HTTP :8765 serves the HQ dashboard (live-ops/dashboard/index.html).
 *   WS   :8766 pushes {occupancy, ins, outs, peak, cap, space_left, ts, health}.
 *   No MOTION_TOKEN → binds 127.0.0.1 only. With MOTION_TOKEN → binds the LAN
 *   and every URL must carry ?token=.
 * Zone counts: GET /api/data/observations (api service), latest crew_count per zone.
 */
import { VENUE_CAP } from "./capacity";

export const READING_MAX_MS = 5_000;
export const STALE_MAX_MS = 30_000;

export const DEFAULT_HQ_URL =
  process.env.NEXT_PUBLIC_HQ_URL?.trim() || "http://127.0.0.1:8765/";
export const DEFAULT_COUNTER_WS_URL = process.env.NEXT_PUBLIC_COUNTER_WS_URL?.trim() || "";

export type CounterStatus = "reading" | "stale" | "offline";

export type CounterPayload = {
  occupancy: number;
  ins: number;
  outs: number;
  peak: number;
  cap: number;
  space_left: number;
  ts: string;
  camera: "green" | "red" | "unknown";
  fps: number;
};

const num = (v: unknown): number | null =>
  typeof v === "number" && Number.isFinite(v) ? v : null;

/** Validate one WebSocket message. Returns null for anything malformed. */
export function parseCounterMessage(raw: unknown): CounterPayload | null {
  let data: unknown = raw;
  if (typeof raw === "string") {
    if (raw.length > 4096) return null;
    try {
      data = JSON.parse(raw);
    } catch {
      return null;
    }
  }
  if (!data || typeof data !== "object") return null;
  const d = data as Record<string, unknown>;
  const occupancy = num(d.occupancy);
  if (occupancy === null) return null;
  const health = (d.health && typeof d.health === "object" ? d.health : {}) as Record<string, unknown>;
  const cam = health.camera;
  return {
    occupancy,
    ins: num(d.ins) ?? 0,
    outs: num(d.outs) ?? 0,
    peak: num(d.peak) ?? occupancy,
    cap: num(d.cap) ?? VENUE_CAP,
    space_left: num(d.space_left) ?? Math.max(0, VENUE_CAP - occupancy),
    ts: typeof d.ts === "string" ? d.ts : "",
    camera: cam === "green" || cam === "red" ? cam : "unknown",
    fps: num(health.counter_fps) ?? 0,
  };
}

/**
 * Freshness → status. Age is measured from when THIS browser received the
 * last message (not the server's ts), so clock skew can't fake freshness.
 *   < 5s   READING  (unless the counter itself reports camera red → STALE)
 *   5–30s  STALE
 *   ≥ 30s or never → OFFLINE
 */
export function counterStatus(
  lastAt: number | null,
  now: number,
  camera: CounterPayload["camera"] = "unknown",
): CounterStatus {
  if (lastAt === null) return "offline";
  const age = now - lastAt;
  if (age >= STALE_MAX_MS) return "offline";
  if (age >= READING_MAX_MS) return "stale";
  return camera === "red" ? "stale" : "reading";
}

const LOOPBACK = /^(localhost|127(?:\.\d{1,3}){3}|\[::1\])$/i;

export function isLoopbackHost(hostname: string): boolean {
  return LOOPBACK.test(hostname);
}

/** ws(s)://host:8766/ (+ ?token=) derived from the HQ page URL. */
export function deriveWsUrl(hqUrl: string): string {
  try {
    const u = new URL(hqUrl);
    const proto = u.protocol === "https:" ? "wss:" : "ws:";
    // Copy the token verbatim. URLSearchParams would turn "+" into a space, and
    // server.py compares the unquote()d raw value exactly.
    const raw = /[?&]token=([^&#]*)/.exec(u.search)?.[1] ?? "";
    const q = raw ? `?token=${raw}` : "";
    return `${proto}//${u.hostname}:8766/${q}`;
  } catch {
    return "";
  }
}

/**
 * Why an https page can't reach this URL, or null if the browser should allow it.
 * http/ws to loopback is allowed by Chrome/Edge/Firefox; anything else on the LAN
 * is mixed content and gets blocked.
 */
export function mixedContentReason(pageProtocol: string, target: string): string | null {
  let u: URL;
  try {
    u = new URL(target);
  } catch {
    return "Not a valid URL.";
  }
  if (pageProtocol !== "https:") return null;
  const insecure = u.protocol === "http:" || u.protocol === "ws:";
  if (!insecure) return null;
  if (isLoopbackHost(u.hostname)) return null;
  return `This page is HTTPS, so the browser blocks ${u.protocol}// to ${u.hostname} (mixed content). Open HQ in its own tab, or run this panel on the booth PC and use 127.0.0.1.`;
}

export type ZoneCount = { zone: string; count: number; at: number | null; label: string };

/** Latest crew_count per zone from /api/data/observations (newest first). */
export function zonesFromObservations(rows: unknown): ZoneCount[] {
  if (!Array.isArray(rows)) return [];
  const seen = new Map<string, ZoneCount>();
  for (const r of rows) {
    if (!r || typeof r !== "object") continue;
    const o = r as Record<string, unknown>;
    const zone = typeof o.zone === "string" && o.zone ? o.zone : "unknown";
    const count = num(o.crew_count);
    if (count === null || seen.has(zone)) continue;
    const at = num(o.captured_at) ?? num(o.created_at);
    seen.set(zone, {
      zone,
      count,
      at,
      label: typeof o.label === "string" ? o.label : "estimate",
    });
  }
  return [...seen.values()];
}

/* ---------- settings + checklist persistence ---------- */

export const SETTINGS_KEY = "motion-liveops-settings-v1";
export const CHECKLIST_KEY = "motion-liveops-checklist-v1";

export type LiveOpsSettings = { hqUrl: string; wsUrl: string };

export function loadSettings(): LiveOpsSettings {
  const fallback = { hqUrl: DEFAULT_HQ_URL, wsUrl: DEFAULT_COUNTER_WS_URL };
  if (typeof window === "undefined") return fallback;
  try {
    const s = JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") as Partial<LiveOpsSettings>;
    return {
      hqUrl: typeof s.hqUrl === "string" && s.hqUrl ? s.hqUrl : fallback.hqUrl,
      wsUrl: typeof s.wsUrl === "string" ? s.wsUrl : fallback.wsUrl,
    };
  } catch {
    return fallback;
  }
}

export function saveSettings(s: LiveOpsSettings): void {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
  } catch {
    /* private mode / quota — settings stay in memory */
  }
}

export function loadChecks(): Record<string, number> {
  if (typeof window === "undefined") return {};
  try {
    const v = JSON.parse(localStorage.getItem(CHECKLIST_KEY) || "{}");
    if (!v || typeof v !== "object" || Array.isArray(v)) return {};
    const out: Record<string, number> = {};
    for (const [k, t] of Object.entries(v)) if (typeof t === "number") out[k] = t;
    return out;
  } catch {
    return {};
  }
}

export function saveChecks(c: Record<string, number>): void {
  try {
    localStorage.setItem(CHECKLIST_KEY, JSON.stringify(c));
  } catch {
    /* ignore */
  }
}

export type CheckItem = { id: string; at: string; text: string; lead: string; template?: boolean };

/** Run-of-show from OPS_DATA plus pre-door live-ops checks (template, editable in code). */
export function buildChecklist(
  runOfShow: ReadonlyArray<{ id: string; at: string; moment: string; lead: string }>,
): CheckItem[] {
  const pre: CheckItem[] = [
    { id: "lo-counter", at: "20:00", text: "Counter server running on booth PC", lead: "Chaka", template: true },
    { id: "lo-hq", at: "20:05", text: "HQ dashboard open · camera tile green", lead: "Chaka", template: true },
    { id: "lo-status", at: "20:10", text: "Live Ops counter status reads READING", lead: "Jovanni", template: true },
    { id: "lo-door", at: "20:15", text: "Door iPad on ?view=door · cap 70", lead: "Door", template: true },
  ];
  const show = runOfShow.map((r) => ({ id: r.id, at: r.at, text: r.moment, lead: r.lead }));
  // Event-night order: 18:00 … 23:59, then 00:00 … 03:00.
  const key = (at: string) => {
    const [h, m] = at.split(":").map(Number);
    return (h < 12 ? h + 24 : h) * 60 + (m || 0);
  };
  return [...show, ...pre].sort((a, b) => key(a.at) - key(b.at));
}

/** "21:00" → "9:00 PM". */
export function fmt12(at: string): string {
  const [h, m] = at.split(":").map(Number);
  if (!Number.isFinite(h)) return at;
  const hh = h % 12 === 0 ? 12 : h % 12;
  return `${hh}:${String(m || 0).padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`;
}
