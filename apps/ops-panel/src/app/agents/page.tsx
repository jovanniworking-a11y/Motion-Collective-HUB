"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type Agent } from "@/lib/api";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api
      .agents()
      .then((d) => setAgents(d.agents))
      .catch((e: Error) => setErr(e.message));
  }, []);

  return (
    <div>
      <h1 className="hero-brand" style={{ fontSize: "2rem", margin: 0 }}>
        Agents
      </h1>
      <p className="lede">
        Area rooms — prompt, correct, or form the bot for that seat. Routed per{" "}
        <code>services/api/MODEL_ROUTING.md</code>.
      </p>
      {err ? (
        <section className="panel">
          <p style={{ color: "#ff8a82" }}>API unreachable: {err}</p>
          <p className="lede">
            Start:{" "}
            <code>
              python3 -m uvicorn app.main:app --app-dir services/api --port 8787
            </code>
          </p>
        </section>
      ) : (
        <div className="lib-grid" data-testid="agents-grid">
          {agents.map((a) => (
            <Link key={a.id} href={`/agents/${a.id}`} className="lib-card">
              <span className="src" style={{ color: "var(--red)" }}>
                {a.channel}
              </span>
              <h3>{a.name}</h3>
              <p>{a.description}</p>
              <span className="go">
                {a.default_model} · {a.worker} →
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
