import { afterEach, describe, expect, it, vi } from "vitest";
import { apiBase } from "./api";

describe("api client", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("defaults to local FastAPI port", () => {
    expect(apiBase()).toMatch(/8787/);
  });

  it("prefers NEXT_PUBLIC_API_URL for cloud", () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "https://motion-ops-api.fly.dev/");
    vi.stubEnv("NEXT_PUBLIC_MOTION_API_URL", "http://127.0.0.1:8787");
    expect(apiBase()).toBe("https://motion-ops-api.fly.dev");
  });

  it("falls back to NEXT_PUBLIC_MOTION_API_URL alias", () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    vi.stubEnv("NEXT_PUBLIC_MOTION_API_URL", "https://api.example.com");
    expect(apiBase()).toBe("https://api.example.com");
  });
});
