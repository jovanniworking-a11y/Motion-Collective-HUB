"use client";

import { useCallback, useEffect, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { api } from "@/lib/api";

export default function MusePage() {
  const [layout, setLayout] = useState<{
    scen: Record<string, unknown>;
    sim_params: Record<string, unknown>;
    items: unknown[];
  } | null>(null);
  const [embedOk, setEmbedOk] = useState(false);
  const [kinds, setKinds] = useState<{ id: string }[]>([]);
  const [kind, setKind] = useState("smoke-stub");
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [jobResult, setJobResult] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(() => {
    api
      .studio()
      .then((d) => {
        setLayout(d.layout as typeof layout);
        setEmbedOk(!!d.paths.index_exists);
        setErr(null);
      })
      .catch((e: Error) => setErr(e.message));
    api
      .sims()
      .then((d) => setKinds(d.kinds))
      .catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function patchScen(field: string, value: string | number) {
    try {
      const res = await api.patchLayout({ scen: { [field]: value } });
      setLayout(res.layout as typeof layout);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    }
  }

  async function runSim() {
    setBusy(true);
    setJobResult(null);
    try {
      const { job } = await api.runSim(kind);
      setJobId(job.id);
      setJobStatus(job.status);
      for (let i = 0; i < 40; i++) {
        await new Promise((r) => setTimeout(r, 100));
        const j = await api.simJob(job.id);
        setJobStatus(j.job.status);
        if (j.job.status === "completed" || j.job.status === "failed") {
          setJobResult(JSON.stringify(j.job.result || j.job.error || j.job, null, 2));
          break;
        }
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1 className="hero-brand" style={{ fontSize: "2rem", margin: 0 }}>
        Muse 3D
      </h1>
      <p className="lede">
        Layout bridge + Studio embed. Sims stubbed unless{" "}
        <code>MOTION_SIM_EXECUTE=1</code>.
      </p>
      {err ? <div className="banner alert">{err}</div> : null}
      <div className="grid-2">
        <div>
          {embedOk ? (
            <iframe
              title="Room Studio"
              className="muse-frame"
              src={api.studioEmbedUrl()}
              sandbox="allow-scripts allow-same-origin"
              data-testid="muse-frame"
            />
          ) : (
            <div className="muse-frame panel" style={{ display: "grid", placeItems: "center" }} data-testid="muse-stub">
              <p className="lede" style={{ textAlign: "center" }}>
                Studio bridge — start API to embed{" "}
                <code>orch/context/studio/index.html</code>
              </p>
            </div>
          )}
        </div>
        <section className="panel" style={{ marginTop: 0 }}>
          <h2>
            Live controls <span className="meta">no address</span>
          </h2>
          <div className="tools">
            <label className="dim" style={{ fontSize: "0.8rem" }}>
              Baths{" "}
              <select
                className="field"
                style={{ width: "auto", display: "inline-block", padding: "0.35rem 0.5rem" }}
                value={Number(layout?.scen?.baths ?? 2)}
                onChange={(e) => void patchScen("baths", Number(e.target.value))}
                data-testid="muse-baths"
              >
                <option value={1}>1</option>
                <option value={2}>2</option>
              </select>
              <LabelTag label="estimate" />
            </label>
          </div>
          <p className="lede">
            Items: <strong className="mono">{layout?.items?.length ?? 0}</strong>
          </p>
          <div className="tools">
            <select
              className="field"
              style={{ maxWidth: 200 }}
              value={kind}
              onChange={(e) => setKind(e.target.value)}
              data-testid="sim-kind"
            >
              {(kinds.length ? kinds : [{ id: "smoke-stub" }]).map((k) => (
                <option key={k.id} value={k.id}>
                  {k.id}
                </option>
              ))}
            </select>
            <button type="button" className="btn primary" disabled={busy} onClick={() => void runSim()} data-testid="run-sim">
              {busy ? "Running…" : "Run sim"}
            </button>
          </div>
          {jobId ? (
            <p className="dim" style={{ fontSize: "0.8rem" }}>
              Job <code>{jobId}</code> · {jobStatus}
            </p>
          ) : null}
          {jobResult ? (
            <pre data-testid="sim-result" style={{ fontSize: "0.72rem", overflow: "auto", maxHeight: 160 }}>
              {jobResult}
            </pre>
          ) : null}
        </section>
      </div>
    </div>
  );
}
