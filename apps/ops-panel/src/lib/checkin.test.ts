import { describe, expect, it } from "vitest";
import { CAP, passLabel, roomLeft, togglePass } from "./checkin";

describe("check-in", () => {
  it("uses the confirmed door cap", () => {
    expect(CAP).toBe(70);
  });

  it("labels passes with three digits", () => {
    expect(passLabel(1)).toBe("001");
    expect(passLabel(50)).toBe("050");
  });

  it("toggles a pass in and out", () => {
    const a = togglePass([], 7);
    expect(a.blocked).toBe(false);
    expect(a.next).toEqual([7]);
    const b = togglePass(a.next, 7);
    expect(b.next).toEqual([]);
  });

  it("blocks over-cap unless forced", () => {
    const full = Array.from({ length: CAP }, (_, i) => i + 1);
    const blocked = togglePass(full, CAP + 1);
    expect(blocked.blocked).toBe(true);
    expect(blocked.next).toEqual(full);
    const forced = togglePass(full, CAP + 1, true);
    expect(forced.blocked).toBe(false);
    expect(forced.next).toContain(CAP + 1);
  });

  it("computes room left", () => {
    expect(roomLeft(0)).toBe(CAP);
    expect(roomLeft(CAP)).toBe(0);
    expect(roomLeft(CAP + 3)).toBe(0);
  });
});
