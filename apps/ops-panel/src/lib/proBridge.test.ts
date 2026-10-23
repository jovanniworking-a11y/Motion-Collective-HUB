import { describe, expect, it } from "vitest";
import {
  buildProBridgePrompt,
  CLAUDE_AI_NEW_URL,
  logProBridgeUsage,
  loadProBridgeUsage,
  PRO_BRIDGE_USAGE_KEY,
} from "./proBridge";

describe("proBridge", () => {
  it("builds a paste-ready prompt with safe SoT + question", () => {
    const p = buildProBridgePrompt({ question: "What's the pool?" });
    expect(p).toMatch(/Pro bridge/i);
    expect(p).toMatch(/\$498/);
    expect(p).toMatch(/What's the pool\?/);
    expect(p).not.toMatch(/guest name/i);
    expect(p.toLowerCase()).not.toMatch(/\d{3,5}\s+\w+\s+(st|ave|rd|blvd)/);
  });

  it("includes agent framing when provided", () => {
    const p = buildProBridgePrompt({
      question: "sim crowd",
      agent: {
        name: "Muse",
        channel: "#muse",
        area: "studio",
        description: "Room Studio sims",
      },
    });
    expect(p).toMatch(/#muse/);
    expect(p).toMatch(/Room Studio/);
  });

  it("points at the official Claude.ai new-chat URL", () => {
    expect(CLAUDE_AI_NEW_URL).toBe("https://claude.ai/new");
  });

  it("logs usage locally as pro-bridge (not API tokens)", () => {
    localStorage.removeItem(PRO_BRIDGE_USAGE_KEY);
    const ev = logProBridgeUsage({
      action: "open",
      source: "assist",
      chars: 1200,
    });
    expect(ev.provider).toBe("pro-bridge");
    expect(ev.label).toBe("open");
    const loaded = loadProBridgeUsage();
    expect(loaded).toHaveLength(1);
    expect(loaded[0].provider).toBe("pro-bridge");
    expect(loaded[0]).not.toHaveProperty("tokens_in");
  });
});
