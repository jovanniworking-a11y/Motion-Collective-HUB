"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { OPS_DATA } from "@/lib/ops-data";
import { loadOpsState } from "@/lib/storage";
import { CAP, roomLeft } from "@/lib/checkin";
import { doorsCountdown, fmtMoney } from "@/lib/time";

export function Dashboard() {
  const [checked, setChecked] = useState(0);
  const [cd, setCd] = useState(() => doorsCountdown());

  useEffect(() => {
    const s = loadOpsState();
    setChecked(s.checked.length);
    const id = window.setInterval(() => setCd(doorsCountdown()), 1000);
    return () => window.clearInterval(id);
  }, []);

  const left = roomLeft(checked);

  return (
    <div>
      <section className="hero-dash" aria-label="Event hero">
        <div className="hero-kicker">MOTION Collective</div>
        <h1 className="hero-brand">
          Devil&apos;s Night
          <br />
          <em>AFTERIMAGE 001</em>
        </h1>
        <p className="countdown-big mono" data-testid="doors-countdown">
          {cd.past ? "Event window" : cd.label}
        </p>
        <p className="hero-line">
          Fri 10.30.26 · doors 9 PM · hard stop 2 AM · invite-only. Local draft —
          nothing spends or posts from this panel.
        </p>
        <div className="hero-cta">
          <Link href="/night-of" className="btn primary">
            Night-Of Ops
          </Link>
          <Link href="/agents" className="btn ghost">
            Agents
          </Link>
          <Link href="/muse" className="btn ghost">
            Muse 3D
          </Link>
          <a href="/hq" className="btn ghost">
            OPEN HQ
          </a>
        </div>
      </section>

      <div className="tile-grid" data-testid="status-tiles">
        <div className={`tile ${checked >= CAP ? "hot" : checked > 0 ? "ok" : ""}`}>
          <div className="k">Checked in</div>
          <div className="v mono" data-testid="dash-checked">
            {checked}
          </div>
          <div className="s">
            of {CAP} cap <LabelTag label={OPS_DATA.capacity.workingCapLabel} />
          </div>
        </div>
        <div className={`tile ${left <= 5 ? "hot" : ""}`}>
          <div className="k">Room left</div>
          <div className="v mono">{left}</div>
          <div className="s">vs working cap</div>
        </div>
        <div className="tile">
          <div className="k">
            Pool <LabelTag label={OPS_DATA.budget.pool.label} />
          </div>
          <div className="v mono">{fmtMoney(OPS_DATA.budget.pool.amount)}</div>
          <div className="s">
            spend {fmtMoney(OPS_DATA.budget.spend.amount)}{" "}
            <LabelTag label={OPS_DATA.budget.spend.label} />
          </div>
        </div>
        <div className="tile">
          <div className="k">
            Buffer <LabelTag label={OPS_DATA.budget.buffer.label} />
          </div>
          <div className="v mono">{fmtMoney(OPS_DATA.budget.buffer.amount)}</div>
          <div className="s">pool − spend · estimate</div>
        </div>
      </div>

      <section className="panel" style={{ marginTop: 16 }}>
        <h2>
          Lineup <span className="meta">promo order · no public set times</span>
        </h2>
        <ul className="lineup-list">
          {OPS_DATA.lineupPublic.map((act, i) => (
            <li key={act.name}>
              <span className="slot mono">{String(i + 1).padStart(2, "0")}</span>
              <div>
                <span className="names">
                  {act.name}
                  {act.partner ? ` · ${act.partner}` : ""}
                </span>
                {act.credit ? <span className="credit">{act.credit}</span> : null}
              </div>
            </li>
          ))}
        </ul>
        <p className="lede" style={{ marginTop: 12, marginBottom: 0 }}>
          Crew set times live under Night-Of → Show. Passes planned{" "}
          {OPS_DATA.capacity.passesPlanned}{" "}
          <LabelTag label={OPS_DATA.capacity.passesPlannedLabel} />.
        </p>
      </section>
    </div>
  );
}
