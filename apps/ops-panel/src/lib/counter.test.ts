import { describe, expect, it } from "vitest";
import { cameraErrorMessage, capacity, duration, people, timecode } from "./counter";

describe("counter helpers", () => {
  it("filters to confident people", () => {
    const out = people([
      { bbox: [0, 0, 1, 1], class: "person", score: 0.87 },
      { bbox: [0, 0, 1, 1], class: "person", score: 0.49 },
      { bbox: [0, 0, 1, 1], class: "dog", score: 0.99 },
      { bbox: [0, 0, 1, 1], class: "person", score: 0.5 },
    ]);
    expect(out).toHaveLength(2);
  });

  it("formats timecode HH:MM:SS:FF", () => {
    expect(timecode(0)).toBe("00:00:00:00");
    expect(timecode(3_723_500)).toBe("01:02:03:15");
  });

  it("formats duration", () => {
    expect(duration(65_000)).toBe("01:05");
    expect(duration(3_665_000)).toBe("1:01:05");
  });

  it("grades capacity against 70", () => {
    expect(capacity(10).level).toBe("ok");
    expect(capacity(56).level).toBe("near");
    expect(capacity(70).level).toBe("over");
    expect(capacity(84).fill).toBe(1);
    expect(capacity(35).pct).toBe(50);
  });

  it("explains camera errors", () => {
    expect(cameraErrorMessage({ name: "NotAllowedError" })).toMatch(/permission denied/i);
    expect(cameraErrorMessage({ name: "NotFoundError" })).toMatch(/no camera/i);
  });
});
