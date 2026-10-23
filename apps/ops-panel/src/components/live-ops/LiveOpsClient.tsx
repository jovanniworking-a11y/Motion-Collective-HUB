"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { VENUE_CAP } from "@/lib/capacity";
import { capacity } from "@/lib/counter";
import {
  type CheckItem,
  type LiveOpsSettings,
  type ZoneCount,
  DEFAULT_HQ_URL,
  READING_MAX_MS,
  STALE_MAX_MS,
  buildChecklist,
  deriveWsUrl,
  fmt12,
  loadChecks,
  loadSettings,
  mixedContentReason,
  saveChecks,
  saveSettings,
  zonesFromObservations,
} from "@/lib/liveops";
import { OPS_DATA } from "@/lib/ops-data";
import { useCounterFeed } from "@/hooks/useCounterFeed";
import s from "./live-ops.module.css";

const STATUS_TEXT = { reading: "Reading", stale: "Stale", offline: "Offline" } as const;
const ZONE_POLL_MS = 15_000;
const EMBED_TIMEOUT_MS = 6_000;

function ago(ms: number): string {
  const sec = Math.max(0, Math.round(ms / 1000));
  if (sec < 60) return `${sec}s ago`;
  const m = Math.floor(sec / 60);
  return m < 60 ? `${m}m ago` : `${Math.floor(m / 60)}h ago`;
}

function Meter({ count, label }: { count: number; label: string }) {
  const c = capacity(count, VENUE_CAP);
  return (
    <div className={s.meter}>
      <div className={s.meterRow}>
        <span className={s.label}>{label}</span>
        <span className={`${s.label} ${s.mono}`}>
          {count} / {VENUE_CAP} · {c.pct}%
        </span>
      </div>
      <div
        className={s.bar}
        role="meter"
        aria-label={`${label} against cap`}
        aria-valuemin={0}
        aria-valuemax={VENUE_CAP}
        aria-valuenow={count}
      >
        <i data-level={c.level} style={{ width: `${c.fill * 100}%` }} />
      </div>
    </div>
  );
}

export function LiveOpsClient() {
  const [settings, setSettings] = useState<LiveOpsSettings>({ hqUrl: DEFAULT_HQ_URL, wsUrl: "" });
  const [draft, setDraft] = useState<LiveOpsSettings>(settings);
  const [ready, setReady] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const loaded = loadSettings();
    setSettings(loaded);
    setDraft(loaded);
    setChecks(loadChecks());
    setReady(true);
  }, []);

  const wsUrl = settings.wsUrl.trim() || deriveWsUrl(settings.hqUrl);
  const feed = useCounterFeed(ready ? wsUrl : "");
  const p = feed.payload;
  const occ = p?.occupancy ?? 0;

  /* ---- zones from the api (internet-dependent; degrades quietly) ---- */
  const [zones, setZones] = useState<ZoneCount[]>([]);
  const [zonesErr, setZonesErr] = useState<string | null>(null);
  const [zonesAt, setZonesAt] = useState<number | null>(null);
  useEffect(() => {
    let cancelled = false;
    const pull = () =>
      api
        .dataObservations()
        .then((r) => {
          if (cancelled) return;
          setZones(zonesFromObservations(r.observations));
          setZonesErr(null);
          setZonesAt(Date.now());
        })
        .catch(() => {
          if (!cancelled) setZonesErr("API unreachable — showing the last zone counts received.");
        });
    pull();
    const id = window.setInterval(pull, ZONE_POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  /* ---- HQ embed (opt-in so phones don't hit the local-network prompt) ---- */
  const [embedOn, setEmbedOn] = useState(false);
  const [embedLoaded, setEmbedLoaded] = useState(false);
  const [embedTimedOut, setEmbedTimedOut] = useState(false);
  const [pageProto, setPageProto] = useState("https:");
  useEffect(() => setPageProto(window.location.protocol), []);
  const hqBlocked = mixedContentReason(pageProto, settings.hqUrl);
  const embedTimer = useRef<number | null>(null);

  useEffect(() => {
    setEmbedLoaded(false);
    setEmbedTimedOut(false);
    if (!embedOn || hqBlocked) return;
    embedTimer.current = window.setTimeout(() => setEmbedTimedOut(true), EMBED_TIMEOUT_MS);
    return () => {
      if (embedTimer.current !== null) window.clearTimeout(embedTimer.current);
    };
  }, [embedOn, hqBlocked, settings.hqUrl]);

  /* ---- checklist ---- */
  const items: CheckItem[] = useMemo(() => buildChecklist(OPS_DATA.runOfShow), []);
  const [checks, setChecks] = useState<Record<string, number>>({});
  const toggle = useCallback((id: string) => {
    setChecks((prev) => {
      const next = { ...prev };
      if (next[id]) delete next[id];
      else next[id] = Date.now();
      saveChecks(next);
      return next;
    });
  }, []);
  const resetChecks = () => {
    if (!window.confirm("Clear every check on this device?")) return;
    setChecks({});
    saveChecks({});
  };
  const done = items.filter((i) => checks[i.id]).length;

  const onSave = (e: React.FormEvent) => {
    e.preventDefault();
    const next = { hqUrl: draft.hqUrl.trim() || DEFAULT_HQ_URL, wsUrl: draft.wsUrl.trim() };
    setSettings(next);
    setDraft(next);
    saveSettings(next);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2000);
  };

  const age = feed.lastAt === null ? null : feed.now - feed.lastAt;

  return (
    <section className={s.page} aria-labelledby="liveops-title">
      <header className={s.head}>
        <p className={s.kicker}>Devil&apos;s Night · AFTERIMAGE 001 · Fri 30 Oct · 9 PM–2 AM</p>
        <h1 id="liveops-title" className={s.title}>
          Live ops
        </h1>
      </header>

      {/* ---------- counter ---------- */}
      <div className={s.block} data-testid="counter-block">
        <div className={s.status} data-status={feed.status} data-testid="counter-status" role="status">
          <i aria-hidden="true" />
          Counter · {STATUS_TEXT[feed.status]}
        </div>
        <p className={s.sub}>
          {age === null
            ? feed.blocked ?? (feed.connected ? "Connected · waiting for data" : "No data yet · retrying")
            : `Last data ${ago(age)}${p?.camera === "red" ? " · camera red, count held" : ""}${
                feed.connected ? "" : " · reconnecting"
              }`}
        </p>

        <div className={s.big} aria-live="polite">
          <span className={s.bigNum} data-level={capacity(occ).level} data-dim={feed.status !== "reading"}>
            {p ? occ : "—"}
          </span>
          <span className={s.label}>In the house · cap {VENUE_CAP}</span>
        </div>

        <Meter count={occ} label="House" />

        <dl className={s.stats}>
          <div>
            <dt>In</dt>
            <dd>{p?.ins ?? "—"}</dd>
          </div>
          <div>
            <dt>Out</dt>
            <dd>{p?.outs ?? "—"}</dd>
          </div>
          <div>
            <dt>Peak</dt>
            <dd>{p?.peak ?? "—"}</dd>
          </div>
          <div>
            <dt>Space left</dt>
            <dd>{p ? Math.max(0, VENUE_CAP - occ) : "—"}</dd>
          </div>
          <div>
            <dt>Camera</dt>
            <dd>{p ? p.camera : "—"}</dd>
          </div>
          <div>
            <dt>FPS</dt>
            <dd>{p ? p.fps : "—"}</dd>
          </div>
        </dl>
        {p && p.cap !== VENUE_CAP && (
          <p className={s.warn}>
            Counter reports cap {p.cap}. Panel uses {VENUE_CAP}. Fix CAP in the counter before doors.
          </p>
        )}
      </div>

      {/* ---------- zones ---------- */}
      <div className={s.block} data-testid="zones-block">
        <h2 className={s.h2}>Zones</h2>
        <div className={s.zones}>
          <Meter count={occ} label="Door counter · house" />
          {zones.map((z) => (
            <Meter key={z.zone} count={z.count} label={`${z.zone} · ${z.label}`} />
          ))}
        </div>
        <p className={s.sub}>
          {zonesErr ??
            (zones.length
              ? `Zone counts from the data API · updated ${zonesAt ? ago(feed.now - zonesAt) : "—"}`
              : "No zone observations in the data API yet. The door counter covers the whole house.")}
        </p>
      </div>

      {/* ---------- HQ ---------- */}
      <div className={s.block} data-testid="hq-block">
        <h2 className={s.h2}>HQ</h2>
        <div className={s.row}>
          <a className={s.btn} href={settings.hqUrl} target="_blank" rel="noopener noreferrer">
            Open HQ
          </a>
          <Link className={`${s.btn} ${s.ghost}`} href="/counter-demo">
            Browser counter
          </Link>
          {!hqBlocked && (
            <button type="button" className={`${s.btn} ${s.ghost}`} onClick={() => setEmbedOn((v) => !v)}>
              {embedOn ? "Hide embed" : "Show HQ here"}
            </button>
          )}
        </div>
        {hqBlocked && <p className={s.sub}>{hqBlocked}</p>}
        {embedOn && !hqBlocked && (
          <>
            <iframe
              className={s.frame}
              src={settings.hqUrl}
              title="HQ dashboard"
              onLoad={() => {
                setEmbedLoaded(true);
                if (embedTimer.current !== null) window.clearTimeout(embedTimer.current);
              }}
            />
            {embedTimedOut && !embedLoaded && (
              <p className={s.warn}>HQ didn&apos;t load in the frame. Use Open HQ. Is the counter running on this machine?</p>
            )}
          </>
        )}
        <details className={s.settings}>
          <summary>Settings</summary>
          <form onSubmit={onSave}>
            <label>
              <span className={s.label}>HQ URL</span>
              <input
                className={s.input}
                inputMode="url"
                autoComplete="off"
                spellCheck={false}
                value={draft.hqUrl}
                onChange={(e) => setDraft({ ...draft, hqUrl: e.target.value })}
                placeholder="http://127.0.0.1:8765/"
              />
            </label>
            <label>
              <span className={s.label}>Counter socket (blank = from HQ URL)</span>
              <input
                className={s.input}
                inputMode="url"
                autoComplete="off"
                spellCheck={false}
                value={draft.wsUrl}
                onChange={(e) => setDraft({ ...draft, wsUrl: e.target.value })}
                placeholder={deriveWsUrl(draft.hqUrl) || "ws://127.0.0.1:8766/"}
              />
            </label>
            <button type="submit" className={s.btn}>
              {saved ? "Saved" : "Save"}
            </button>
            <p className={s.fine}>
              Saved on this device only. A ?token= in these URLs is stored in this browser — booth PC only.
              Now using {wsUrl || "—"}.
            </p>
          </form>
        </details>
      </div>

      {/* ---------- run of show ---------- */}
      <div className={s.block} data-testid="ros-block">
        <h2 className={s.h2}>Run of show</h2>
        <p className={s.sub}>
          {done} / {items.length} done · saved on this device
        </p>
        <ul className={s.checklist}>
          {items.map((it) => {
            const on = Boolean(checks[it.id]);
            return (
              <li key={it.id}>
                <button
                  type="button"
                  className={s.check}
                  aria-pressed={on}
                  data-on={on}
                  onClick={() => toggle(it.id)}
                >
                  <span className={s.box} aria-hidden="true" />
                  <span className={`${s.when} ${s.mono}`}>{fmt12(it.at)}</span>
                  <span className={s.what}>
                    {it.text}
                    <small>
                      {it.lead}
                      {it.template ? " · template" : ""}
                      {on ? ` · ✓ ${new Date(checks[it.id]).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}` : ""}
                    </small>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
        <button type="button" className={`${s.btn} ${s.ghost}`} onClick={resetChecks}>
          Reset checks
        </button>
        <p className={s.fine}>
          Times from the crew run of show (ops-data seed, America/Chicago). Rows marked template are
          live-ops checks added here — edit in src/lib/liveops.ts.
        </p>
      </div>

      <p className={s.fine}>
        Reading under {READING_MAX_MS / 1000}s · stale to {STALE_MAX_MS / 1000}s · offline after. The
        counter is LAN-only: from this HTTPS site the browser reaches it only on the booth PC itself
        (127.0.0.1). Other devices use Open HQ.
      </p>
    </section>
  );
}
