"use client";

import { useEffect, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { api } from "@/lib/api";

type UsagePayload = Awaited<ReturnType<typeof api.usage>>;

export default function UsagePage() {
  const [data, setData] = useState<UsagePayload | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api
      .usage()
      .then(setData)
      .catch((e: Error) => setErr(e.message));
  }, []);

  const maxCalls = Math.max(1, ...(data?.by_bot.map((b) => b.calls) || [1]));

  return (
    <div>
      <h1 className="hero-brand" style={{ fontSize: "2rem", margin: 0 }}>
        Usage
      </h1>
      <p className="lede">
        Metered calls per bot. confirmed = live API · estimate = mock/stub.
      </p>
      {err ? <div className="banner alert">{err}</div> : null}
      <div className="stats">
        <div className="stat">
          <div className="k">
            Calls <LabelTag label={(data?.totals.label as "estimate") || "estimate"} />
          </div>
          <div className="v mono" data-testid="usage-calls">
            {data?.totals.calls ?? "—"}
          </div>
        </div>
        <div className="stat">
          <div className="k">Tokens in</div>
          <div className="v mono">{data?.totals.tokens_in ?? "—"}</div>
        </div>
        <div className="stat">
          <div className="k">Tokens out</div>
          <div className="v mono">{data?.totals.tokens_out ?? "—"}</div>
        </div>
      </div>
      <section className="panel">
        <h2>
          By bot <span className="meta">SQLite</span>
        </h2>
        {!data || data.by_bot.length === 0 ? (
          <p className="lede">No calls yet — chat an agent to meter usage.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Bot</th>
                <th>Model</th>
                <th>Calls</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data.by_bot.map((b) => (
                <tr key={`${b.agent_id}-${b.model}`}>
                  <td>
                    {b.agent_id}
                    <span className="dim"> · {b.area}</span>
                  </td>
                  <td className="dim">{b.model}</td>
                  <td className="mono">{b.calls}</td>
                  <td style={{ width: "30%" }}>
                    <div className="bar">
                      <i style={{ width: `${(b.calls / maxCalls) * 100}%` }} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
