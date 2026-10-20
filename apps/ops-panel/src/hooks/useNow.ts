"use client";

import { useEffect, useState } from "react";
import { resolveNow, type ClockMode } from "@/lib/time";

export function useNow(mode: ClockMode, offsetMin: number, tickMs = 1000): Date {
  const [now, setNow] = useState(() => resolveNow(mode, offsetMin));

  useEffect(() => {
    setNow(resolveNow(mode, offsetMin));
    const id = window.setInterval(() => {
      setNow(resolveNow(mode, offsetMin));
    }, tickMs);
    return () => window.clearInterval(id);
  }, [mode, offsetMin, tickMs]);

  return now;
}
