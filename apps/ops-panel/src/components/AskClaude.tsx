"use client";

import { useEffect, useRef, useState } from "react";

type Msg = { role: "user" | "assistant"; content: string; mode?: string };

const STARTERS = [
  "What's the pool / spend / buffer?",
  "Remind me of the lineup order",
  "What is the 12:30 collision?",
  "Working cap vs planned passes?",
];

export function AskClaude() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      content:
        "Ask Claude with safe SoT context (no guest PII, no venue address). Live if ANTHROPIC_API_KEY / CLAUDE_API_KEY is set on the server; otherwise a deterministic mock proves the pipeline.",
      mode: "system",
    },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState<"live" | "mock" | "…">("…");
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/claude")
      .then((r) => r.json())
      .then((d: { mode?: "live" | "mock" }) => setMode(d.mode ?? "mock"))
      .catch(() => setMode("mock"));
  }, []);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight });
  }, [messages]);

  async function send(text: string) {
    const message = text.trim();
    if (!message || busy) return;
    setBusy(true);
    setInput("");
    const history = messages
      .filter((m) => m.mode !== "system")
      .map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { role: "user", content: message }]);
    try {
      const res = await fetch("/api/claude", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ message, history }),
      });
      const data = (await res.json()) as {
        ok: boolean;
        mode?: string;
        reply?: string;
        error?: string;
      };
      setMode((data.mode as "live" | "mock") || mode);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: data.ok
            ? (data.reply ?? "")
            : `Error: ${data.error ?? res.status}`,
          mode: data.mode,
        },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: `Network error: ${err instanceof Error ? err.message : "failed"}`,
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div className="head-row" style={{ marginBottom: 12 }}>
        <div>
          <h1
            style={{
              margin: 0,
              fontFamily: "var(--f-display)",
              fontStyle: "italic",
              fontSize: 28,
            }}
          >
            Ask Claude
          </h1>
          <p className="lede" style={{ marginBottom: 0 }}>
            Crew assist hooked to a server route. Keys stay server-side.
          </p>
        </div>
        <span className="mode-pill" data-mode={mode} data-testid="claude-mode">
          {mode === "live" ? "live API" : mode === "mock" ? "mock" : "…"}
        </span>
      </div>

      <section className="panel chat">
        <div className="chat-log" ref={logRef} data-testid="chat-log">
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              <div className="meta">
                {m.role === "user" ? "You" : "Claude"}
                {m.mode && m.mode !== "system" ? ` · ${m.mode}` : ""}
              </div>
              {m.content}
            </div>
          ))}
        </div>
        <div className="tools" style={{ marginBottom: 0 }}>
          {STARTERS.map((s) => (
            <button
              key={s}
              type="button"
              className="btn ghost"
              style={{ padding: "8px 10px", fontSize: 10 }}
              onClick={() => send(s)}
              disabled={busy}
            >
              {s}
            </button>
          ))}
        </div>
        <form
          className="chat-compose"
          onSubmit={(e) => {
            e.preventDefault();
            void send(input);
          }}
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about budget, lineup, welfare, capacity…"
            aria-label="Ask Claude"
            data-testid="claude-input"
            disabled={busy}
          />
          <button
            className="btn primary"
            type="submit"
            disabled={busy || !input.trim()}
            data-testid="claude-send"
          >
            {busy ? "Thinking…" : "Send"}
          </button>
        </form>
      </section>
    </div>
  );
}
