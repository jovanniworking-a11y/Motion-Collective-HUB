"use client";

import { useEffect, useRef, useState } from "react";
import {
  type CounterPayload,
  counterStatus,
  mixedContentReason,
  parseCounterMessage,
} from "@/lib/liveops";

export type CounterFeed = {
  payload: CounterPayload | null;
  lastAt: number | null;
  now: number;
  connected: boolean;
  blocked: string | null;
  status: ReturnType<typeof counterStatus>;
};

/** Subscribe to the door counter WebSocket. Reconnects with backoff; never throws. */
export function useCounterFeed(wsUrl: string): CounterFeed {
  const [payload, setPayload] = useState<CounterPayload | null>(null);
  const [lastAt, setLastAt] = useState<number | null>(null);
  const [connected, setConnected] = useState(false);
  const [blocked, setBlocked] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const tries = useRef(0);

  // 1 Hz clock so READING → STALE → OFFLINE advances with no new messages.
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  useEffect(() => {
    setConnected(false);
    setBlocked(null);
    if (!wsUrl) {
      setBlocked("No counter URL set.");
      return;
    }
    const reason = mixedContentReason(window.location.protocol, wsUrl);
    if (reason) {
      setBlocked(reason);
      return;
    }

    let sock: WebSocket | null = null;
    let timer: number | null = null;
    let closed = false;

    const schedule = () => {
      if (closed) return;
      const wait = Math.min(10_000, 1000 * 2 ** Math.min(tries.current, 4));
      tries.current += 1;
      timer = window.setTimeout(connect, wait);
    };

    function connect() {
      if (closed) return;
      try {
        sock = new WebSocket(wsUrl);
      } catch (err) {
        setBlocked(
          err instanceof Error && err.name === "SecurityError"
            ? "The browser blocked this socket (insecure ws:// from an HTTPS page)."
            : "Counter URL is not a valid ws:// or wss:// address.",
        );
        return;
      }
      sock.onopen = () => {
        tries.current = 0;
        setConnected(true);
      };
      sock.onmessage = (ev) => {
        const p = parseCounterMessage(typeof ev.data === "string" ? ev.data : "");
        if (!p) return;
        setPayload(p);
        setLastAt(Date.now());
      };
      sock.onclose = () => {
        setConnected(false);
        schedule();
      };
      sock.onerror = () => {
        /* onclose follows; keep the last count on screen */
      };
    }

    connect();
    return () => {
      closed = true;
      if (timer !== null) window.clearTimeout(timer);
      if (sock) {
        sock.onclose = null;
        sock.close();
      }
    };
  }, [wsUrl]);

  return {
    payload,
    lastAt,
    now,
    connected,
    blocked,
    status: counterStatus(lastAt, now, payload?.camera),
  };
}
