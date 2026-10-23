import { CLAUDE_SAFE_CONTEXT } from "./ops-data";

export type ClaudeMode = "live" | "mock";

export type AssistRequest = {
  message: string;
  history?: { role: "user" | "assistant"; content: string }[];
};

export type AssistResponse = {
  ok: true;
  mode: ClaudeMode;
  reply: string;
  model?: string;
};

export type AssistError = {
  ok: false;
  mode: ClaudeMode;
  error: string;
};

function getApiKey(): string | undefined {
  return (
    process.env.ANTHROPIC_API_KEY ||
    process.env.CLAUDE_API_KEY ||
    undefined
  );
}

export function resolveMode(): ClaudeMode {
  return getApiKey() ? "live" : "mock";
}

/** Deterministic mock — proves UI + pipeline without spend. */
export function mockAssist(message: string): string {
  const q = message.toLowerCase();
  if (!q.trim()) {
    return "Ask a crew question — budget, lineup, welfare, capacity, or run-of-show. (mock · no API key)";
  }
  if (q.includes("budget") || q.includes("pool") || q.includes("buffer")) {
    return [
      "Budget snapshot (mock):",
      "• Pool $498 — confirmed plan (3 × $166; Haven received, Alex + Jovanni promised)",
      "• Spend ~$381.13 — estimate",
      "• Buffer ~$116.87 — estimate",
      "• DJ fees $475 (HE//THEY $300 + Rohan $175) + CDJs $345 sit outside the pool, paid by Jovanni (confirmed).",
      "Nothing spends from this panel — Jovanni OK required.",
    ].join("\n");
  }
  if (q.includes("lineup") || q.includes("set") || q.includes("dj")) {
    return [
      "Lineup (promo order, mock):",
      "1. iamariology b2b raymixes",
      "2. Rohan Rali b2b Shubh Samtani (Rohan $175)",
      "3. HE//THEY · co.b b2b NiiON",
      "Crew times (internal): doors 21:00 · Rohan Rali b2b Shubh Samtani 23:00–00:15 · HE//THEY 00:15. Keep set times off public promo.",
    ].join("\n");
  }
  if (q.includes("welfare") || q.includes("collision") || q.includes("12:30")) {
    return [
      "Welfare (mock): rounds every 30 min from doors 21:00 to hard stop 02:00.",
      "12:30 collision: last entry closes + master fader check + welfare round — assign cover before the window.",
      "Log rounds in Night-Of → Welfare; state stays on-device.",
    ].join("\n");
  }
  if (q.includes("cap") || q.includes("pass") || q.includes("door")) {
    return [
      "Capacity (mock): door cap 70 (confirmed). Passes 001–070 (confirmed).",
      "Check-in stores pass numbers only — no guest names, no venue address.",
    ].join("\n");
  }
  return [
    "MOTION ops assist (Pro bridge mode · no ANTHROPIC_API_KEY / CLAUDE_API_KEY).",
    `You asked: “${message.trim().slice(0, 200)}”`,
    "",
    "Safe context loaded: event hours, lineup order, labeled money numbers, welfare cadence — no guest PII.",
    "For a real Claude answer at $0 API cost: use Open in Claude.ai / Copy prompt (Claude.ai Pro/Max in the browser).",
    "Claude.ai Pro ≠ Anthropic API — they are separate products. Optional: set ANTHROPIC_API_KEY for in-panel API mode (billed).",
    "Draft only; never spend/post without Jovanni.",
  ].join("\n");
}

export async function liveAssist(
  message: string,
  history: AssistRequest["history"] = [],
): Promise<{ reply: string; model: string }> {
  const key = getApiKey();
  if (!key) throw new Error("No API key");

  const model = process.env.CLAUDE_MODEL || "claude-sonnet-5-5";
  const messages = [
    ...(history ?? []).map((h) => ({
      role: h.role,
      content: h.content,
    })),
    { role: "user" as const, content: message },
  ];

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": key,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model,
      max_tokens: 1024,
      system: `You are the MOTION Collective crew ops assistant for AFTERIMAGE 001 / Devil's Night. Answer briefly from the context. Never invent a venue address or guest names. Label numbers confirmed/estimate/open. Never encourage spending, posting, or publishing without Jovanni's OK.\n\n${CLAUDE_SAFE_CONTEXT}`,
      messages,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Anthropic ${res.status}: ${text.slice(0, 200)}`);
  }

  const data = (await res.json()) as {
    content?: { type: string; text?: string }[];
  };
  const reply =
    data.content
      ?.filter((c) => c.type === "text")
      .map((c) => c.text ?? "")
      .join("\n")
      .trim() || "(empty reply)";
  return { reply, model };
}
