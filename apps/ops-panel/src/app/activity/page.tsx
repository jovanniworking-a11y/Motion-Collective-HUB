// @agent-provenance [2026-10-24T21:04:59Z] [agent:claude-code] [status:completed/verified_passed] [trace:tr_c3ee9ecae4e0488a]
// @summary: Close the four provenance limits: shared leases, guest denylist, coverage gate, agent registry
// @handoff: Jovanni: set MOTION_AGENT_TOKEN on Vercel api + GitHub secrets MOTION_API_URL/MOTION_AGENT_TOKEN; optional GUEST_DENYLIST
"use client";

import { useEffect, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { api, type AgentLease, type AgentStampBrief } from "@/lib/api";

type Act = Awaited<ReturnType<typeof api.activity>>;

function short(path: string): string {
  return path.length > 48 ? `…${path.slice(-47)}` : path;
}

export default function ActivityPage() {
  const [data, setData] = useState<Act | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [leases, setLeases] = useState<AgentLease[]>([]);
  const [stamps, setStamps] = useState<{ source: string; stamps: AgentStampBrief[] } | null>(null);

  useEffect(() => {
    let alive = true;
    const tick = () => {
      api
        .activity()
        .then((d) => {
          if (alive) {
            setData(d);
            setErr(null);
          }
        })
        .catch((e: Error) => {
          if (alive) setErr(e.message);
        });
    };
    const tickAgents = () => {
      api.agentLeases().then((d) => alive && setLeases(d.leases)).catch(() => undefined);
      api.agentStamps(15).then((d) => alive && setStamps(d)).catch(() => undefined);
    };
    tick();
    tickAgents();
    const agentsId = window.setInterval(tickAgents, 15000);
    const id = window.setInterval(tick, 5000);
    return () => {
      alive = false;
      window.clearInterval(id);
      window.clearInterval(agentsId);
    };
  }, []);

  return (
    <div>
      <h1 className="hero-brand" style={{ fontSize: "2rem", margin: 0 }}>
        Activity
      </h1>
      <p className="lede">
        Live runs + board / outbox from <code>orch/tasks/</code>.
      </p>
      {err ? <div className="banner alert">{err}</div> : null}
      <div className="stats">
        <div className="stat">
          <div className="k">
            Board <LabelTag label={(data?.label as "confirmed") || "open"} />
          </div>
          <div className="v mono" data-testid="activity-board">
            {data?.board_count ?? "—"}
          </div>
        </div>
        <div className="stat">
          <div className="k">Outbox</div>
          <div className="v mono">{data?.outbox_count ?? "—"}</div>
        </div>
        <div className="stat">
          <div className="k">Live</div>
          <div className="v mono">{data?.live_count ?? "—"}</div>
        </div>
      </div>
      <section className="panel" data-testid="activity-feed">
        {(data?.feed || []).map((item, i) => (
          <div key={`${item.kind}-${i}`} className="feed-item">
            <span className="kind">{item.kind}</span>
            <div>
              <div>{item.title}</div>
              {item.agent_id ? (
                <div className="dim" style={{ fontSize: "0.78rem" }}>
                  @{item.agent_id}
                </div>
              ) : null}
            </div>
            <span className="status">{item.status}</span>
          </div>
        ))}
      </section>
      <h2 style={{ marginTop: "1.5rem" }}>Who is editing what</h2>
      <section className="panel" data-testid="agent-leases">
        {leases.length === 0 ? (
          <div className="dim">No file is leased right now.</div>
        ) : (
          leases.map((l) => (
            <div key={l.resource} className="feed-item">
              <span className="kind">lease</span>
              <div>
                <div className="mono">{short(l.resource)}</div>
                <div className="dim" style={{ fontSize: "0.78rem" }}>
                  @{l.owner}
                </div>
              </div>
              <span className="status">{Math.max(0, Math.round(l.expires_at - Date.now() / 1000))}s left</span>
            </div>
          ))
        )}
      </section>
      <h2 style={{ marginTop: "1.5rem" }}>Agent work log</h2>
      <p className="dim" style={{ fontSize: "0.78rem" }}>
        From {stamps?.source === "database" ? "the shared database" : "the repo ledger"}. Newest first.
      </p>
      <section className="panel" data-testid="agent-stamps">
        {(stamps?.stamps || []).map((s) => (
          <div key={s.trace_id + s.timestamp_utc} className="feed-item">
            <span className="kind">{s.agent_id}</span>
            <div>
              <div>{s.intent}</div>
              <div className="dim mono" style={{ fontSize: "0.78rem" }}>
                {short(s.target_uri)}
                {s.next ? ` · next: ${s.next}` : ""}
                {s.failure_reason ? ` · why: ${s.failure_reason}` : ""}
              </div>
            </div>
            <span className="status">
              {s.status} / {s.verification_status.replace("verified_", "")}
            </span>
          </div>
        ))}
      </section>
    </div>
  );
}
