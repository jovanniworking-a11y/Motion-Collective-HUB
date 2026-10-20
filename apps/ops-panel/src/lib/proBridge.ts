import { CLAUDE_SAFE_CONTEXT } from "./ops-data";

/** Claude.ai new-chat entry — human pastes the prompt (Pro/Max subscription). */
export const CLAUDE_AI_NEW_URL = "https://claude.ai/new";

export const PRO_BRIDGE_USAGE_KEY = "motion-pro-bridge-usage-v1";

export type ProBridgeAction = "open" | "copy";
export type ProBridgeSource = "assist" | "agent";

/** Local meter only — not Anthropic API tokens. */
export type ProBridgeUsageEvent = {
  id: string;
  ts: number;
  /** Provider tag for local meters / usage UI. */
  provider: "pro-bridge";
  action: ProBridgeAction;
  source: ProBridgeSource;
  agentId?: string;
  chars: number;
  /** estimate = opened/copied without measuring tokens; open = human will use Pro in browser. */
  label: "estimate" | "open";
};

export type BuildProBridgePromptInput = {
  question: string;
  history?: { role: "user" | "assistant"; content: string }[];
  /** Optional area-bot framing for agent chat. */
  agent?: {
    name?: string;
    channel?: string;
    description?: string;
    area?: string;
  };
};

const STANDING = [
  "Standing orders: never spend, send, post, or publish without Jovanni's OK. Draft only.",
  "Never invent or share a venue address. Never include guest personal data.",
  "Label every money/capacity number confirmed / estimate / open.",
  "You are helping MOTION Collective crew ops for Devil's Night · AFTERIMAGE 001.",
].join("\n");

/** Build a paste-ready prompt from safe SoT snippets + the crew question. */
export function buildProBridgePrompt(input: BuildProBridgePromptInput): string {
  const question = (input.question || "").trim();
  const parts: string[] = [
    "# MOTION ops · Claude.ai Pro bridge (paste into claude.ai)",
    "",
    "## Standing orders",
    STANDING,
    "",
    "## Safe Source-of-Truth context (no guest PII, no venue address)",
    CLAUDE_SAFE_CONTEXT,
  ];

  if (input.agent) {
    const a = input.agent;
    parts.push(
      "",
      "## Area agent framing",
      [
        a.channel ? `Channel: ${a.channel}` : null,
        a.name ? `Bot: ${a.name}` : null,
        a.area ? `Area: ${a.area}` : null,
        a.description ? `Role: ${a.description}` : null,
      ]
        .filter(Boolean)
        .join("\n") || "(agent)",
    );
  }

  const hist = (input.history ?? []).filter(
    (h) => h.content?.trim() && h.role !== ("system" as string),
  );
  if (hist.length) {
    parts.push("", "## Recent thread (ops panel)");
    for (const h of hist.slice(-8)) {
      parts.push(`${h.role === "user" ? "Crew" : "Assist"}: ${h.content.trim()}`);
    }
  }

  parts.push(
    "",
    "## Crew question",
    question || "(no question yet — ask me about budget, lineup, welfare, or capacity)",
    "",
    "Answer briefly from the context above. If something is unknown, say so and label it open.",
  );

  return parts.join("\n");
}

export function loadProBridgeUsage(): ProBridgeUsageEvent[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(PRO_BRIDGE_USAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as ProBridgeUsageEvent[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function logProBridgeUsage(
  event: Omit<ProBridgeUsageEvent, "id" | "ts" | "provider" | "label"> & {
    label?: ProBridgeUsageEvent["label"];
  },
): ProBridgeUsageEvent {
  const full: ProBridgeUsageEvent = {
    id: `pb-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`,
    ts: Date.now(),
    provider: "pro-bridge",
    label: event.label ?? (event.action === "open" ? "open" : "estimate"),
    action: event.action,
    source: event.source,
    agentId: event.agentId,
    chars: event.chars,
  };
  if (typeof window === "undefined") return full;
  const prev = loadProBridgeUsage();
  const next = [...prev, full].slice(-200);
  localStorage.setItem(PRO_BRIDGE_USAGE_KEY, JSON.stringify(next));
  return full;
}

export async function copyText(text: string): Promise<boolean> {
  try {
    if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    /* fall through */
  }
  /* Fallback for older environments / denied clipboard. */
  if (typeof document === "undefined") return false;
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.left = "-9999px";
  document.body.appendChild(ta);
  ta.select();
  let ok = false;
  try {
    ok = document.execCommand("copy");
  } catch {
    ok = false;
  }
  document.body.removeChild(ta);
  return ok;
}

/**
 * Copy prompt + open Claude.ai new chat. Does not call Anthropic API.
 * Human pastes into the Pro/Max session in the browser.
 */
export async function openInClaudeAi(opts: {
  prompt: string;
  source: ProBridgeSource;
  agentId?: string;
}): Promise<{ copied: boolean; opened: boolean }> {
  const copied = await copyText(opts.prompt);
  logProBridgeUsage({
    action: "open",
    source: opts.source,
    agentId: opts.agentId,
    chars: opts.prompt.length,
    label: "open",
  });
  let opened = false;
  if (typeof window !== "undefined") {
    const w = window.open(CLAUDE_AI_NEW_URL, "_blank", "noopener,noreferrer");
    opened = Boolean(w);
  }
  return { copied, opened };
}

export async function copyProBridgePrompt(opts: {
  prompt: string;
  source: ProBridgeSource;
  agentId?: string;
}): Promise<boolean> {
  const ok = await copyText(opts.prompt);
  logProBridgeUsage({
    action: "copy",
    source: opts.source,
    agentId: opts.agentId,
    chars: opts.prompt.length,
    label: "estimate",
  });
  return ok;
}
