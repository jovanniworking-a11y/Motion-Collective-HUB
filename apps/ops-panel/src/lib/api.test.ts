import { afterEach, describe, expect, it, vi } from "vitest";
import { apiBase } from "./api";

describe("api client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uses a same-origin base in the browser", () => {
    expect(typeof window).not.toBe("undefined");
    expect(apiBase()).toBe("");
  });

  it("defaults to the local FastAPI port outside the browser", () => {
    vi.stubGlobal("window", undefined);
    expect(apiBase()).toBe("http://127.0.0.1:8787");
  });
});
