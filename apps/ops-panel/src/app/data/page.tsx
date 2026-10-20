"use client";

import { useCallback, useEffect, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { api } from "@/lib/api";

type SimRow = {
  id: number;
  kind: string;
  status: string;
  score: number | null;
  label: string;
};

type ObsRow = {
  id: number;
  zone: string;
  crew_count: number | null;
  density_est: number | null;
  image_path_hash: string | null;
  label: string;
};

export default function DataComparePage() {
  const [sims, setSims] = useState<SimRow[]>([]);
  const [obs, setObs] = useState<ObsRow[]>([]);
  const [compare, setCompare] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dbOk, setDbOk] = useState<boolean | null>(null);

  const refresh = useCallback(() => {
    api
      .dataHealth()
      .then((d) => setDbOk(!!d.ok))
      .catch(() => setDbOk(false));
    api
      .dataSims()
      .then((d) => setSims(d.sims as SimRow[]))
      .catch((e: Error) => setErr(e.message));
    api
      .dataObservations()
      .then((d) => setObs(d.observations as ObsRow[]))
      .catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function seedStub() {
    setBusy(true);
    setErr(null);
    try {
      await api.dataRunSim("smoke-stub");
      await api.dataIngestObservation({
        crew_count: 40,
        density_est: 0.5,
        zone: "dance",
        image_path: "stub://frame",
        label: "estimate",
      });
      await api.dataIngestFlow({ zone: "dance", count: 18, label: "estimate" });
      refresh();
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function runCompare() {
    setBusy(true);
    try {
      const c = await api.dataCompare();
      setCompare(JSON.stringify(c.metrics, null, 2));
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="hero-brand" style={{ fontSize: "2rem", margin: 0 }}>
        Data / Compare
      </h1>
      <p className="lede">
        Muse sim runs vs imaging counts. Privacy MVP: hashes + density only — no faces, no guest PII.
        Camera not ordered.
      </p>
      {err ? <div className="banner alert">{err}</div> : null}
      <p className="dim" style={{ fontSize: "0.8rem" }}>
        DB {dbOk === null ? "…" : dbOk ? "ready" : "down"} ·{" "}
        <LabelTag label="estimate" /> compare metrics until night-of ground truth
      </p>
      <div className="tools" style={{ marginBottom: "1rem" }}>
        <button type="button" className="btn primary" disabled={busy} onClick={() => void seedStub()} data-testid="data-seed">
          {busy ? "Working…" : "Seed stub sim + observation"}
        </button>
        <button type="button" className="btn" disabled={busy} onClick={() => void runCompare()} data-testid="data-compare">
          Compare
        </button>
      </div>
      <div className="grid-2">
        <section className="panel" style={{ marginTop: 0 }}>
          <h2>Sim runs</h2>
          <ul className="plain-list" data-testid="sim-list">
            {(sims.length ? sims : []).slice(0, 8).map((s) => (
              <li key={s.id}>
                <code>#{s.id}</code> {s.kind} · {s.status}
                {s.score != null ? ` · score ${s.score}` : ""}{" "}
                <LabelTag label={(s.label as "estimate" | "confirmed" | "open") || "estimate"} />
              </li>
            ))}
            {!sims.length ? <li className="dim">No rows yet</li> : null}
          </ul>
        </section>
        <section className="panel" style={{ marginTop: 0 }}>
          <h2>Observations</h2>
          <ul className="plain-list" data-testid="obs-list">
            {(obs.length ? obs : []).slice(0, 8).map((o) => (
              <li key={o.id}>
                <code>#{o.id}</code> {o.zone} · count {o.crew_count ?? "—"} · dens{" "}
                {o.density_est ?? "—"}
                {o.image_path_hash ? ` · hash ${o.image_path_hash.slice(0, 8)}…` : ""}{" "}
                <LabelTag label={(o.label as "estimate" | "confirmed" | "open") || "estimate"} />
              </li>
            ))}
            {!obs.length ? <li className="dim">No observations yet</li> : null}
          </ul>
        </section>
      </div>
      {compare ? (
        <pre data-testid="compare-metrics" style={{ fontSize: "0.75rem", overflow: "auto", maxHeight: 220 }}>
          {compare}
        </pre>
      ) : null}
    </div>
  );
}
