/**
 * Signed session cookie shared by the panel (Next middleware) and the API (FastAPI).
 * Token = base64url(JSON payload) + "." + base64url(HMAC-SHA256(secret, payload)).
 * Web Crypto only, so it runs in the Edge middleware and in Node.
 */

export const SESSION_COOKIE = "motion_session";
export const SESSION_TTL_SEC = 12 * 60 * 60;

export type SessionPayload = { u: string; iat: number; exp: number; v: 1 };

const enc = new TextEncoder();

function b64url(bytes: Uint8Array): string {
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromB64url(s: string): Uint8Array {
  const pad = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
  const bin = atob(pad);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function hmacKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, [
    "sign",
    "verify",
  ]);
}

/** Auth is required when a secret is set, and always on Vercel (fail closed if the secret is missing). */
export function authMode(env: Record<string, string | undefined> = process.env): "off" | "on" | "misconfigured" {
  const secret = env.MOTION_SESSION_SECRET || "";
  if (secret.length >= 32) return "on";
  if (secret || env.VERCEL) return "misconfigured";
  return "off";
}

export async function signSession(user: string, secret: string, now = Date.now()): Promise<string> {
  const iat = Math.floor(now / 1000);
  const payload: SessionPayload = { u: user, iat, exp: iat + SESSION_TTL_SEC, v: 1 };
  const body = b64url(enc.encode(JSON.stringify(payload)));
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", await hmacKey(secret), enc.encode(body)));
  return `${body}.${b64url(sig)}`;
}

export async function verifySession(
  token: string | undefined,
  secret: string,
  now = Date.now(),
): Promise<SessionPayload | null> {
  if (!token || !secret) return null;
  const [body, sig, extra] = token.split(".");
  if (!body || !sig || extra !== undefined) return null;
  try {
    const ok = await crypto.subtle.verify("HMAC", await hmacKey(secret), fromB64url(sig) as BufferSource, enc.encode(body));
    if (!ok) return null;
    const p = JSON.parse(new TextDecoder().decode(fromB64url(body))) as SessionPayload;
    if (p.v !== 1 || typeof p.u !== "string" || typeof p.exp !== "number") return null;
    if (p.exp <= Math.floor(now / 1000)) return null;
    return p;
  } catch {
    return null;
  }
}
