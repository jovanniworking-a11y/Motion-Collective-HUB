import { describe, expect, it } from "vitest";
import { countdown, eventDateTime, welfareSlots } from "./time";

describe("time helpers", () => {
  it("maps early-morning cues to Sat 31", () => {
    const doors = eventDateTime("21:00");
    const lastEntry = eventDateTime("00:30");
    expect(lastEntry.getTime()).toBeGreaterThan(doors.getTime());
  });

  it("builds welfare slots including 12:30 collision", () => {
    const slots = welfareSlots();
    expect(slots.length).toBeGreaterThan(5);
    const hit = slots.find((s) => s.collision);
    expect(hit).toBeTruthy();
  });

  it("formats countdown", () => {
    const from = new Date("2026-10-30T20:00:00Z");
    const to = new Date(from.getTime() + 90 * 1000);
    expect(countdown(to, from)).toMatch(/1m/);
  });
});
