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
    expect(r).toMatch(/Glamz/);
    expect(r).toMatch(/HE\/\/THEY/);
  });

  it("defaults to mock without keys", () => {
    expect(resolveMode()).toBe("mock");
  });
});
