import { describe, expect, it } from "vitest";
import { signSession, verifySession, authMode } from "./session";
import { base32Encode, hotp, verifyTotp } from "./totp";
import { hashPassword, verifyPassword, loadUsers } from "./users";
import { _resetLimits, isLocked, recordFail, stepReplayed } from "./limits";

const SECRET = "x".repeat(40);

describe("session cookie", () => {
  it("round-trips and rejects tampering / expiry / wrong secret", async () => {
    const t = await signSession("jovanni", SECRET, 1_000_000_000_000);
    expect((await verifySession(t, SECRET, 1_000_000_000_000))?.u).toBe("jovanni");
    expect(await verifySession(t, "y".repeat(40), 1_000_000_000_000)).toBeNull();
    const [b, s] = t.split(".");
    expect(await verifySession(`${b}x.${s}`, SECRET, 1_000_000_000_000)).toBeNull();
    expect(await verifySession(t, SECRET, 1_000_000_000_000 + 13 * 3600 * 1000)).toBeNull();
    expect(await verifySession(undefined, SECRET)).toBeNull();
  });

  it("fails closed on Vercel without a strong secret", () => {
    expect(authMode({})).toBe("off");
    expect(authMode({ VERCEL: "1" })).toBe("misconfigured");
    expect(authMode({ MOTION_SESSION_SECRET: "short" })).toBe("misconfigured");
    expect(authMode({ VERCEL: "1", MOTION_SESSION_SECRET: SECRET })).toBe("on");
  });
});

describe("TOTP (RFC 6238 vector)", () => {
  const key = Buffer.from("12345678901234567890");
  it("matches the RFC test values", () => {
    expect(hotp(key, 1)).toBe("287082"); // T = 59 s
    expect(hotp(key, Math.floor(1111111109 / 30))).toBe("081804");
  });
  it("accepts ±1 step, rejects others and bad input", () => {
    const b32 = base32Encode(key);
    const now = 1111111109 * 1000;
    expect(verifyTotp(b32, "081804", now)).not.toBeNull();
    expect(verifyTotp(b32, "081804", now + 30_000)).not.toBeNull();
    expect(verifyTotp(b32, "081804", now + 90_000)).toBeNull();
    expect(verifyTotp(b32, "12ab56", now)).toBeNull();
  });
});

describe("passwords + limits", () => {
  it("hashes with scrypt and verifies", () => {
    const h = hashPassword("correct horse battery");
    expect(verifyPassword("correct horse battery", h)).toBe(true);
    expect(verifyPassword("wrong", h)).toBe(false);
    expect(verifyPassword("anything", undefined)).toBe(false);
  });
  it("parses users and ignores junk", () => {
    expect(loadUsers("not json")).toEqual([]);
    expect(loadUsers('[{"u":"a","pw":"p","totp":"T"},{"u":"b"}]')).toHaveLength(1);
  });
  it("locks after 5 fails and blocks code replay", () => {
    _resetLimits();
    for (let i = 0; i < 5; i++) recordFail("ip:1", 0);
    expect(isLocked("ip:1", 1000)).toBe(true);
    expect(isLocked("ip:1", 16 * 60 * 1000)).toBe(false);
    expect(stepReplayed("a", 10)).toBe(false);
    expect(stepReplayed("a", 10)).toBe(true);
    expect(stepReplayed("a", 11)).toBe(false);
  });
});
