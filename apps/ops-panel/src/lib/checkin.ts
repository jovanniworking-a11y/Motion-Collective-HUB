import { PASS_COUNT as PASSES, VENUE_CAP } from "./capacity";

export const CAP = VENUE_CAP;
export const PASS_COUNT = PASSES;

export function togglePass(
  checked: number[],
  n: number,
  forceOverCap = false,
): { next: number[]; blocked: boolean } {
  const set = new Set(checked);
  if (set.has(n)) {
    set.delete(n);
    return { next: [...set].sort((a, b) => a - b), blocked: false };
  }
  if (set.size >= CAP && !forceOverCap) {
    return { next: checked, blocked: true };
  }
  set.add(n);
  return { next: [...set].sort((a, b) => a - b), blocked: false };
}

export function roomLeft(checkedCount: number): number {
  return Math.max(0, CAP - checkedCount);
}

export function passLabel(n: number): string {
  return String(n).padStart(3, "0");
}
