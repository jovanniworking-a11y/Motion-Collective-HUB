"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api, type Agent, type ChatMessage } from "@/lib/api";

export default function AgentRoomPage() {
  const id = String(useParams().id || "");
  const [agent, setAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [routeNote, setRouteNote] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!id) return;
    api
      .agent(id)
      .then((d) => {
        setAgent(d.agent);
        setMessages(d.history || []);
        setErr(null);
      })
      .catch((e: Error) => setErr(e.message));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function send(action: "prompt" | "correct" | "form") {
    if (!id || busy) return;
    const text =
      action === "prompt"
        ? prompt.trim()
        : prompt.trim() ||
          (action === "form"
            ? "Form standing preferences for this area."
            : "Apply this correction as a preference.");
    if (action === "prompt" && !text) return;
    setBusy(true);
    setErr(null);
    try {
      const res = await api.chat(id, text, action);
      setMessages(res.thread);
      setPrompt("");
      setRouteNote(`${res.route.model} — ${res.route.why}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void send("prompt");
  }

  return (
    <div>
      <p className="lede">
        <Link href="/agents">← Agents</Link>
      </p>
      <h1 className="hero-brand" style={{ fontSize: "2rem", margin: 0 }}>
        {agent?.channel || `#${id}`}
      </h1>
      <p className="lede">
        {agent?.description || "Loading…"}
        {agent ? (
          <span className="dim">
            {" "}
            · {agent.default_model} · {agent.worker}
          </span>
        ) : null}
      </p>
      {err ? <div className="banner alert">{err}</div> : null}
      <section className="panel chat">
        <div className="chat-log" data-testid="agent-chat-log">
          {messages.length === 0 ? (
            <p className="dim">No messages yet — prompt this area bot.</p>
          ) : (
            messages.map((m) => (
              <div
                key={m.id}
                className={`bubble ${m.role === "user" ? "user" : "assistant"}`}
              >
                <div className="meta">
                  {m.role}
                  {m.action && m.action !== "prompt" ? ` · ${m.action}` : ""}
                  {m.model ? ` · ${m.provider}:${m.model}` : ""}
                </div>
                {m.content}
              </div>
            ))
          )}
        </div>
        <form onSubmit={onSubmit}>
          <textarea
            className="field"
            rows={3}
            data-testid="agent-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={busy}
            placeholder={`Message ${agent?.channel || "agent"}…`}
          />
          <div className="tools">
            <button type="submit" className="btn primary" disabled={busy} data-testid="agent-send">
              {busy ? "Sending…" : "Prompt"}
            </button>
            <button type="button" className="btn ghost" disabled={busy} onClick={() => void send("correct")}>
              Correct
            </button>
            <button type="button" className="btn ghost" disabled={busy} onClick={() => void send("form")}>
              Form
            </button>
          </div>
          {routeNote ? (
            <p className="dim" style={{ fontSize: "0.78rem", marginTop: 8 }}>
              Route: {routeNote}
            </p>
          ) : null}
        </form>
      </section>
    </div>
  );
}
