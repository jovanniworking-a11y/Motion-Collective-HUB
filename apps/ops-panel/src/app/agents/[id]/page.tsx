"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import { ProBridgeActions } from "@/components/ProBridgeActions";
import { api, type Agent, type ChatMessage } from "@/lib/api";

export default function AgentRoomPage() {
  const id = String(useParams().id || "");
  const [agent, setAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [routeNote, setRouteNote] = useState<string | null>(null);
  const [apiLive, setApiLive] = useState<boolean | null>(null);

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

  useEffect(() => {
    /* Same key signal as Assist — panel Next route; agent API may still be mock. */
    fetch("/api/claude")
      .then((r) => r.json())
      .then((d: { mode?: string }) => setApiLive(d.mode === "live"))
      .catch(() => setApiLive(false));
  }, []);

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
        {apiLive === false ? (
          <span className="dim"> · Pro bridge mode (no panel API key)</span>
        ) : apiLive ? (
          <span className="dim"> · API key present on panel</span>
        ) : null}
      </p>
      {err ? <div className="banner alert">{err}</div> : null}
      <section className="panel" style={{ marginBottom: 14 }}>
        <ProBridgeActions
          compact
          question={prompt}
          source="agent"
          agentId={id || undefined}
          agent={
            agent
              ? {
                  name: agent.name,
                  channel: agent.channel,
                  description: agent.description,
                  area: agent.area,
                }
              : undefined
          }
          history={messages.map((m) => ({
            role: m.role === "user" ? "user" : "assistant",
            content: m.content,
          }))}
        />
      </section>
      <section className="panel chat">
        <div className="chat-log" data-testid="agent-chat-log">
          {messages.length === 0 ? (
            <p className="dim">
              No messages yet — Prompt uses the API mock (or live key on the
              FastAPI service). Prefer Open in Claude.ai for Pro/$0 API.
            </p>
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
