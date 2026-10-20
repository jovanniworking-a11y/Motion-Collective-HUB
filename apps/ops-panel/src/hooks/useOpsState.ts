"use client";

import { useCallback, useEffect, useState } from "react";
import {
  emptyOpsState,
  loadOpsState,
  saveOpsState,
  type OpsPersistedState,
} from "@/lib/storage";
import { togglePass } from "@/lib/checkin";

export function useOpsState() {
  const [state, setState] = useState<OpsPersistedState>(emptyOpsState);
  const [hydrated, setHydrated] = useState(false);
  const [undoStack, setUndoStack] = useState<{ n: number; wasIn: boolean }[]>(
    [],
  );

  useEffect(() => {
    setState(loadOpsState());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    saveOpsState(state);
  }, [state, hydrated]);

  const patch = useCallback((partial: Partial<OpsPersistedState>) => {
    setState((s) => ({ ...s, ...partial }));
  }, []);

  const checkIn = useCallback(
    (n: number, forceOverCap = false) => {
      setState((s) => {
        const wasIn = s.checked.includes(n);
        const { next, blocked } = togglePass(s.checked, n, forceOverCap);
        if (blocked) return s;
        setUndoStack((u) => [...u, { n, wasIn }]);
        return { ...s, checked: next };
      });
    },
    [],
  );

  const undoCheckIn = useCallback(() => {
    setUndoStack((u) => {
      const last = u[u.length - 1];
      if (!last) return u;
      setState((s) => {
        const set = new Set(s.checked);
        if (last.wasIn) set.add(last.n);
        else set.delete(last.n);
        return { ...s, checked: [...set].sort((a, b) => a - b) };
      });
      return u.slice(0, -1);
    });
  }, []);

  const resetCheckIn = useCallback(() => {
    setUndoStack([]);
    setState((s) => ({ ...s, checked: [] }));
  }, []);

  const logWelfare = useCallback((id: string) => {
    setState((s) => ({
      ...s,
      welfareLog: { ...s.welfareLog, [id]: new Date().toISOString() },
    }));
  }, []);

  const toggleWelfare = useCallback((id: string) => {
    setState((s) => {
      const next = { ...s.welfareLog };
      if (next[id]) delete next[id];
      else next[id] = new Date().toISOString();
      return { ...s, welfareLog: next };
    });
  }, []);

  const resetWelfare = useCallback(() => {
    setState((s) => ({ ...s, welfareLog: {} }));
  }, []);

  return {
    state,
    hydrated,
    patch,
    checkIn,
    undoCheckIn,
    resetCheckIn,
    logWelfare,
    toggleWelfare,
    resetWelfare,
    canUndo: undoStack.length > 0,
  };
}
