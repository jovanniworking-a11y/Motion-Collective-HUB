/**
 * Best-effort brute-force guard + TOTP replay guard (per server instance).
 * Serverless instances don't share memory, so this slows attacks rather than
 * stopping them outright; the password + 2FA pair is the real barrier.
 */
const MAX_FAILS = 5;
const LOCK_MS = 15 * 60 * 1000;

const fails = new Map<string, { n: number; until: number }>();
const usedSteps = new Map<string, number>();

export function isLocked(key: string, now = Date.now()): boolean {
  const f = fails.get(key);
  return !!f && f.until > now;
}

export function recordFail(key: string, now = Date.now()): void {
  const f = fails.get(key) || { n: 0, until: 0 };
  f.n += 1;
  if (f.n >= MAX_FAILS) {
    f.until = now + LOCK_MS;
    f.n = 0;
  }
  fails.set(key, f);
}

export function clearFails(key: string): void {
  fails.delete(key);
}

/** True if this user already used this (or a later) TOTP step — blocks code replay. */
export function stepReplayed(user: string, step: number): boolean {
  const last = usedSteps.get(user);
  if (last !== undefined && step <= last) return true;
  usedSteps.set(user, step);
  return false;
}

export function _resetLimits(): void {
  fails.clear();
  usedSteps.clear();
}
