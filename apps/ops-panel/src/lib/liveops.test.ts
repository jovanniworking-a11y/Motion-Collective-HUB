import { describe, expect, it } from "vitest";
import {
  READING_MAX_MS,
  STALE_MAX_MS,
  buildChecklist,
  counterStatus,
  deriveWsUrl,
  fmt12,
  mixedContentReason,
  parseCounterMessage,
  zonesFromObservations,
} from "./liveops";
import { OPS_DATA } from "./ops-data";

describe("counter status thresholds", () => {
  const now = 1_000_000;
  it("is offline with no data", () => {
    expect(counterStatus(null, now)).toBe("offline");
  });
  it("reads under 5s", () => {
    expect(counterStatus(now - 100, now, "green")).toBe("reading");
    expect(counterStatus(now - (READING_MAX_MS - 1), now)).toBe("reading");
  });
  it("is stale from 5s to 30s", () => {
    expect(counterStatus(now - READING_MAX_MS, now)).toBe("stale");
    expect(counterStatus(now - (STALE_MAX_MS - 1), now)).toBe("stale");
  });
  it("is offline at 30s and beyond", () => {
    expect(counterStatus(now - STALE_MAX_MS, now)).toBe("offline");
  });
  it("treats a red camera as stale even when fresh", () => {
    expect(counterStatus(now - 100, now, "red")).toBe("stale");
  });
});

describe("counter messages", () => {
  it("parses the server.py payload", () => {
    const p = parseCounterMessage(
      JSON.stringify({
        occupancy: 12, ins: 15, outs: 3, peak: 14, cap: 70, space_left: 58,
        ts: "2026-10-31T02:00:00Z", health: { camera: "green", counter_fps: 9.5 },
      }),
    );
    expect(p?.occupancy).toBe(12);
    expect(p?.cap).toBe(70);
    expect(p?.camera).toBe("green");
  });
  it("rejects junk and defaults cap to 70", () => {
    expect(parseCounterMessage("not json")).toBeNull();
    expect(parseCounterMessage({ occupancy: "NaN" })).toBeNull();
    expect(parseCounterMessage({ occupancy: 3 })?.cap).toBe(70);
  });
});

describe("urls", () => {
  it("derives the ws url and keeps the token", () => {
    expect(deriveWsUrl("http://127.0.0.1:8765/")).toBe("ws://127.0.0.1:8766/");
    expect(deriveWsUrl("http://192.168.1.20:8765/?token=a+b")).toBe(
      "ws://192.168.1.20:8766/?token=a+b",
    );
  });
  it("allows loopback, blocks LAN http from https", () => {
    expect(mixedContentReason("https:", "http://127.0.0.1:8765/")).toBeNull();
    expect(mixedContentReason("https:", "ws://localhost:8766/")).toBeNull();
    expect(mixedContentReason("https:", "http://192.168.1.20:8765/")).toMatch(/mixed content/);
    expect(mixedContentReason("http:", "http://192.168.1.20:8765/")).toBeNull();
  });
});

describe("zones + checklist", () => {
  it("keeps the newest count per zone", () => {
    const z = zonesFromObservations([
      { zone: "dance", crew_count: 30, created_at: 2 },
      { zone: "dance", crew_count: 10, created_at: 1 },
      { zone: "kitchen", crew_count: 8, created_at: 2 },
      { zone: "hall", crew_count: null },
    ]);
    expect(z.map((r) => [r.zone, r.count])).toEqual([["dance", 30], ["kitchen", 8]]);
  });
  it("orders the night past midnight", () => {
    const list = buildChecklist(OPS_DATA.runOfShow);
    const at = list.map((i) => i.at);
    expect(at.indexOf("21:00")).toBeLessThan(at.indexOf("00:15"));
    expect(at[at.length - 1]).toBe("02:00");
    expect(fmt12("00:15")).toBe("12:15 AM");
    expect(fmt12("21:00")).toBe("9:00 PM");
  });
});
