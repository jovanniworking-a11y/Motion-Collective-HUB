import type { ClockMode } from "./time";

export const STORE_KEY = "motion-night-ops-v1";

export type OpsPersistedState = {
  checked: number[];
  welfareLog: Record<string, string>;
  clockMode: ClockMode;
  clockOffsetMin: number;
};

export function emptyOpsState(): OpsPersistedState {
  return {
    checked: [],
    welfareLog: {},
    clockMode: "live",
    clockOffsetMin: 0,
  };
}

export function loadOpsState(): OpsPersistedState {
  if (typeof window === "undefined") return emptyOpsState();
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (!raw) return emptyOpsState();
    const s = JSON.parse(raw) as Partial<OpsPersistedState>;
    return {
      checked: Array.isArray(s.checked) ? s.checked.map(Number) : [],
      welfareLog:
        s.welfareLog && typeof s.welfareLog === "object" ? s.welfareLog : {},
      clockMode: s.clockMode === "event" || s.clockMode === "custom" ? s.clockMode : "live",
      clockOffsetMin: Number.isFinite(s.clockOffsetMin) ? Number(s.clockOffsetMin) : 0,
    };
  } catch {
    return emptyOpsState();
  }
}

export function saveOpsState(state: OpsPersistedState): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORE_KEY, JSON.stringify(state));
}
