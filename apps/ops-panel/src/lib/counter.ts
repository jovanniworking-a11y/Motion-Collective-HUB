/** Pure helpers for the /counter-demo people counter. */

import { VENUE_CAP } from "./capacity";

export { VENUE_CAP };
export const MIN_PERSON_SCORE = 0.5;

export type Detection = {
  bbox: [number, number, number, number];
  class: string;
  score: number;
};

/** Keep only confident person detections. */
export function people<T extends Detection>(preds: T[], min = MIN_PERSON_SCORE): T[] {
  return preds.filter((p) => p.class === "person" && p.score >= min);
}

/** HH:MM:SS:FF at the given frame rate (default 30). */
export function timecode(ms: number, fps = 30): string {
  const safe = Math.max(0, Math.floor(ms));
  const totalSec = Math.floor(safe / 1000);
  const ff = Math.floor(((safe % 1000) / 1000) * fps);
  const hh = Math.floor(totalSec / 3600);
  const mm = Math.floor((totalSec % 3600) / 60);
  const ss = totalSec % 60;
  return [hh, mm, ss, ff].map((n) => String(n).padStart(2, "0")).join(":");
}

/** H:MM:SS / MM:SS session clock. */
export function duration(ms: number): string {
  const s = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  const mmss = `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  return h > 0 ? `${h}:${mmss}` : mmss;
}

export type CapacityLevel = "ok" | "near" | "over";

export function capacity(count: number, cap = VENUE_CAP) {
  const ratio = cap > 0 ? count / cap : 0;
  const level: CapacityLevel = ratio >= 1 ? "over" : ratio >= 0.8 ? "near" : "ok";
  return {
    ratio,
    pct: Math.round(ratio * 100),
    fill: Math.min(1, Math.max(0, ratio)),
    level,
  };
}

/** Map a getUserMedia failure to a readable message. */
export function cameraErrorMessage(err: unknown): string {
  const name =
    typeof err === "object" && err !== null && "name" in err
      ? String((err as { name: unknown }).name)
      : "";
  switch (name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
    case "SecurityError":
      return "Camera permission denied. Allow camera access for this site in the browser's address bar, then press Start again.";
    case "NotFoundError":
    case "DevicesNotFoundError":
    case "OverconstrainedError":
      return "No camera found. Connect a webcam, or try another device.";
    case "NotReadableError":
    case "TrackStartError":
    case "AbortError":
      return "The camera is busy or unavailable. Close other apps using it (Zoom, FaceTime, another tab) and try again.";
    default:
      return `Could not start the camera${err instanceof Error && err.message ? `: ${err.message}` : "."}`;
  }
}
