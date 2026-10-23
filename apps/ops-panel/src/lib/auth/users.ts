/**
 * Crew logins come from the MOTION_AUTH_USERS env var (server-only, never in git):
 *   [{"u":"jovanni","pw":"scrypt$16384$8$1$<salt>$<hash>","totp":"<BASE32>"}]
 * Generate an entry with `npm run auth:add-user -- <name>`.
 */
import { randomBytes, scryptSync, timingSafeEqual } from "node:crypto";

export type AuthUser = { u: string; pw: string; totp: string };

export function loadUsers(raw = process.env.MOTION_AUTH_USERS || ""): AuthUser[] {
  if (!raw.trim()) return [];
  try {
    const list = JSON.parse(raw) as AuthUser[];
    return Array.isArray(list) ? list.filter((x) => x && x.u && x.pw && x.totp) : [];
  } catch {
    return [];
  }
}

export function hashPassword(password: string, salt = randomBytes(16)): string {
  const [N, r, p] = [16384, 8, 1];
  const hash = scryptSync(password, salt, 32, { N, r, p });
  return `scrypt$${N}$${r}$${p}$${salt.toString("base64")}$${hash.toString("base64")}`;
}

// Used when the username is unknown, so a miss costs the same time as a hit.
const DUMMY = hashPassword("motion-dummy-password", Buffer.alloc(16));

export function verifyPassword(password: string, stored: string | undefined): boolean {
  const parts = (stored || DUMMY).split("$");
  if (parts.length !== 6 || parts[0] !== "scrypt") return false;
  const [, N, r, p, salt, hash] = parts;
  const want = Buffer.from(hash, "base64");
  const got = scryptSync(password, Buffer.from(salt, "base64"), want.length, {
    N: Number(N),
    r: Number(r),
    p: Number(p),
  });
  return timingSafeEqual(want, got) && stored !== undefined;
}
