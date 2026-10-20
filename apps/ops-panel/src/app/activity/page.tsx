"use client";

import { useEffect, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { api } from "@/lib/api";

type Act = Awaited<ReturnType<typeof api.activity>>;

export default function ActivityPage() {
  const [data, setData] = useState<Act | null>(null);
  const [err, setErr] = useState<string | null>(null);

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
    tick();
    const id = window.setInterval(tick, 5000);
    return () => {
      alive = false;
      window.clearInterval(id);
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
    </div>
  );
}
