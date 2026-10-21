"use client";

import { useCallback, useEffect, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { api } from "@/lib/api";

type Board = Awaited<ReturnType<typeof api.occupancyBoard>>;

const ORDER = ["living", "dance", "kitchen", "hallway", "balcony"] as const;

export default function OccupancyPage() {
  const [board, setBoard] = useState<Board | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [drafts, setDrafts] = useState<Record<number, string>>({});

  const load = useCallback(() => {
    api
      .occupancyBoard()
      .then((data) => {
        setBoard(data);
        setErr(null);
      })
      .catch((e: Error) => setErr(e.message));
  }, []);

  useEffect(() => {
    load();
    const timer = setInterval(load, 10000);
    return () => clearInterval(timer);
  }, [load]);

  async function confirmSpot(id: number) {
    const raw = drafts[id];
    const count = Number(raw);
    if (!Number.isInteger(count) || count < 0) return;
    await api.occupancySpot(id, count);
    setDrafts((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    load();
  }

  const dance = board?.zones.find((z) => z.zone === "dance");
  const danceCount = dance?.count ?? 0;
  const sim = board?.sim_dance_peak ?? 30.42;
  const cap = board?.cap ?? 70;
  const bar = Math.min(100, (danceCount / cap) * 100);
  const simMark = Math.min(100, (sim / cap) * 100);

  return (
    <div>
      <h1 className="hero-brand" style={{ fontSize: "2rem", margin: 0 }}>
        Occupancy
      </h1>
      <p className="lede">
        Zone counts only. Dance sits inside living and is not added again. Sim line is the 50-guest run, not a 70-person forecast.
      </p>
      {err ? <div className="banner alert">{err}</div> : null}
      <div className="stats">
        <div className="stat">
          <div className="k">
            House <LabelTag label="estimate" />
          </div>
          <div className="v mono" data-testid="house-total">
            {board?.house_total ?? "—"}
          </div>
          <div className="s">{board?.house_note}</div>
        </div>
        <div className="stat">
          <div className="k">
            Cap <LabelTag label={board?.cap_label || "confirmed"} />
          </div>
          <div className="v mono">{cap}</div>
        </div>
        <div className="stat">
          <div className="k">
            Sim dance <LabelTag label={board?.sim_dance_label || "confirmed"} />
          </div>
          <div className="v mono">{sim}</div>
          <div className="s">50 guests</div>
        </div>
        <div className="stat">
          <div className="k">
            Score <LabelTag label={board?.scorecard.label || "open"} />
          </div>
          <div className="v mono" data-testid="score-verdict">
            {board?.scorecard.verdict ?? "—"}
          </div>
        </div>
      </div>
      <section className="panel">
        <h2>
          Dance inside the cap <span className="meta">polygons {board?.polygons_label ?? "open"}</span>
        </h2>
        <div className="occ-bar" aria-hidden="true">
          <span className="occ-fill" style={{ width: `${bar}%` }} />
          <span className="occ-sim" style={{ left: `${simMark}%` }} />
        </div>
        <p className="lede">Ice fill is the dance count. The tick is sim peak 30.42.</p>
      </section>
      <section className="panel">
        <h2>Zones</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Zone</th>
              <th>Count</th>
              <th>Conf</th>
              <th>Quality</th>
              <th>Age</th>
              <th>Label</th>
            </tr>
          </thead>
          <tbody>
            {ORDER.map((name) => {
              const zone = board?.zones.find((z) => z.zone === name);
              const quality = zone?.count_quality || "no_feed";
              return (
                <tr key={name}>
                  <td>
                    {name}
                    {name === "dance" ? " · inside living" : ""}
                  </td>
                  <td className="mono">{zone?.count ?? "—"}</td>
                  <td className="mono">{zone?.confidence ?? "—"}</td>
                  <td>
                    <span className={quality === "low" ? "q-low" : "dim"}>{quality}</span>
                  </td>
                  <td className="mono">{zone?.age_sec == null ? "—" : `${zone.age_sec}s`}</td>
                  <td>
                    <LabelTag label={zone?.label || "open"} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>
      <section className="panel">
        <h2>Spot check</h2>
        <p className="lede">Low-quality rows, plus 1 in 50 ok rows. Type the count you see. Nothing is saved but the number.</p>
        {(board?.spot_queue.length ?? 0) === 0 ? (
          <p className="lede">Queue empty.</p>
        ) : (
          <ul className="occ-queue">
            {board?.spot_queue.map((row) => (
              <li key={row.id}>
                <span className="mono">
                  {row.zone} · was {row.count} · {row.count_quality}
                </span>
                <input
                  aria-label={`count for ${row.zone}`}
                  inputMode="numeric"
                  value={drafts[row.id] ?? ""}
                  onChange={(e) => setDrafts((prev) => ({ ...prev, [row.id]: e.target.value }))}
                />
                <button type="button" className="occ-ok" onClick={() => confirmSpot(row.id)}>
                  Confirm
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
