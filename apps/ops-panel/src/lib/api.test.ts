import { describe, expect, it } from "vitest";
import { apiBase } from "./api";

describe("api client", () => {
  it("defaults to local FastAPI port", () => {
    expect(apiBase()).toMatch(/8787/);
  });
});
