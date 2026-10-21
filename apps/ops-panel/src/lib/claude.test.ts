import { describe, expect, it } from "vitest";
import { mockAssist, resolveMode } from "./claude";

describe("claude mock", () => {
  it("answers budget questions with labeled numbers", () => {
    const r = mockAssist("What is the budget pool?");
    expect(r).toMatch(/\$450/);
    expect(r).toMatch(/confirmed/i);
    expect(r).toMatch(/estimate/i);
  });

  it("answers lineup questions", () => {
    const r = mockAssist("lineup order please");
    expect(r).toMatch(/iamariology/i);
    expect(r).toMatch(/Rohan Rali/);
    expect(r).toMatch(/Shubh Samtani/);
    expect(r).toMatch(/HE\/\/THEY/);
    expect(r).not.toMatch(/Glamz/);
  });

  it("defaults to mock without keys", () => {
    expect(resolveMode()).toBe("mock");
  });

  it("points free path at Pro bridge when no key", () => {
    const r = mockAssist("random crew question about lighting");
    expect(r).toMatch(/Pro bridge/i);
    expect(r).toMatch(/claude\.ai/i);
  });
});
