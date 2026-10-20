import { OPS_DATA } from "./ops-data";

const TZ = OPS_DATA.event.tz;
/** 30 Oct 2026 is CDT (UTC−5). */
const CDT_OFFSET_H = 5;

export type ClockMode = "live" | "event" | "custom";

export function parseHM(hm: string): { h: number; m: number } {
  const [h, m] = hm.split(":").map(Number);
  return { h, m };
}

/** Event wall-clock → Date. Early morning (00–05) is Sat 31. */
export function eventDateTime(hm: string): Date {
  const { h, m } = parseHM(hm);
  const [Y, M, Day] = OPS_DATA.event.date.split("-").map(Number);
  if (h < 6) {
    return new Date(Date.UTC(Y, M - 1, Day + 1, h + CDT_OFFSET_H, m, 0));
  }
  return new Date(Date.UTC(Y, M - 1, Day, h + CDT_OFFSET_H, m, 0));
}

export function resolveNow(
  mode: ClockMode,
  offsetMin: number,
  real: Date = new Date(),
): Date {
  if (mode === "live") return real;
  if (mode === "custom") {
    return new Date(real.getTime() + offsetMin * 60000);
  }
  /* event: map current HH:MM:SS onto event night */
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: TZ,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).formatToParts(real);
  const get = (t: string) => Number(parts.find((p) => p.type === t)?.value ?? 0);
  let h = get("hour");
  if (h === 24) h = 0;
  const mi = get("minute");
  const s = get("second");
  const dayOffset = h < 6 ? 1 : 0;
  const [Y, M, Day] = OPS_DATA.event.date.split("-").map(Number);
  return new Date(Date.UTC(Y, M - 1, Day + dayOffset, h + CDT_OFFSET_H, mi, s));
}

export function fmtMoney(n: number): string {
  return (
    "$" +
    Number(n).toLocaleString("en-US", {
      minimumFractionDigits: n % 1 ? 2 : 0,
      maximumFractionDigits: 2,
    })
  );
}

export function fmtTime(d: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: TZ,
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(d);
}

export function fmtClock(d: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: TZ,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(d);
}

export function fmtDate(d: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: TZ,
    weekday: "short",
    month: "short",
    day: "numeric",
  }).format(d);
}

export function countdown(to: Date, from: Date = new Date()): string {
  const ms = to.getTime() - from.getTime();
  const sign = ms < 0 ? "−" : "";
  const abs = Math.abs(ms);
  const totalSec = Math.floor(abs / 1000);
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  if (h > 0) return `${sign}${h}h ${String(m).padStart(2, "0")}m`;
  return `${sign}${m}m ${String(s).padStart(2, "0")}s`;
}

/** Days / hours / minutes until doors (or past). */
export function doorsCountdown(from: Date = new Date()): {
  label: string;
  past: boolean;
  ms: number;
} {
  const doors = eventDateTime(OPS_DATA.event.doors);
  const ms = doors.getTime() - from.getTime();
  if (ms <= 0) {
    return { label: "Doors open / past", past: true, ms };
  }
  const totalSec = Math.floor(ms / 1000);
  const d = Math.floor(totalSec / 86400);
  const h = Math.floor((totalSec % 86400) / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const parts = [];
  if (d > 0) parts.push(`${d}d`);
  parts.push(`${h}h`, `${String(m).padStart(2, "0")}m`);
  return { label: parts.join(" "), past: false, ms };
}

export type WelfareSlot = {
  id: string;
  n: number;
  at: Date;
  collision: boolean;
};

export function welfareSlots(): WelfareSlot[] {
  const start = eventDateTime(OPS_DATA.welfare.start);
  const end = eventDateTime(OPS_DATA.welfare.end);
  const collision = eventDateTime(OPS_DATA.welfare.collisionAt);
  const slots: WelfareSlot[] = [];
  let t = new Date(start.getTime());
  let i = 1;
  while (t.getTime() <= end.getTime()) {
    const isCollision = Math.abs(t.getTime() - collision.getTime()) < 60000;
    slots.push({
      id: "w" + i,
      n: i,
      at: new Date(t.getTime()),
      collision: isCollision,
    });
    t = new Date(t.getTime() + OPS_DATA.welfare.intervalMin * 60000);
    i += 1;
  }
  return slots;
}
