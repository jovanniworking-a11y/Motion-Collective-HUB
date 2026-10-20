"use client";

import { useMemo, useState } from "react";
import { LabelTag } from "@/components/LabelTag";
import { useOpsState } from "@/hooks/useOpsState";
import { useNow } from "@/hooks/useNow";
import { CAP, PASS_COUNT, passLabel, roomLeft } from "@/lib/checkin";
import { OPS_DATA } from "@/lib/ops-data";
import {
  countdown,
  eventDateTime,
  fmtClock,
  fmtDate,
  fmtMoney,
  fmtTime,
  welfareSlots,
} from "@/lib/time";

type Tab = "checkin" | "show" | "welfare" | "budget";

export function NightOfClient() {
  const {
    state,
    hydrated,
    patch,
    checkIn,
    undoCheckIn,
    resetCheckIn,
    logWelfare,
    toggleWelfare,
    resetWelfare,
    canUndo,
  } = useOpsState();
  const now = useNow(state.clockMode, state.clockOffsetMin);
  const [tab, setTab] = useState<Tab>("checkin");
  const [query, setQuery] = useState("");

  const checkedSet = useMemo(() => new Set(state.checked), [state.checked]);
  const slots = useMemo(() => welfareSlots(), []);
  const collision = eventDateTime(OPS_DATA.welfare.collisionAt);
  const minsToCollision = (collision.getTime() - now.getTime()) / 60000;
  const collisionSlot = slots.find((s) => s.collision);
  const collisionLogged = Boolean(
    collisionSlot && state.welfareLog[collisionSlot.id],
  );

  const ros = useMemo(
    () => OPS_DATA.runOfShow.map((r) => ({ ...r, atDate: eventDateTime(r.at) })),
    [],
  );

  let currentIdx = -1;
  for (let i = 0; i < ros.length; i++) {
    const start = ros[i].atDate;
    const end =
      i + 1 < ros.length
        ? ros[i + 1].atDate
        : new Date(start.getTime() + 60 * 60000);
    if (now >= start && now < end) currentIdx = i;
  }
  if (currentIdx < 0 && now >= ros[ros.length - 1].atDate) {
    currentIdx = ros.length - 1;
  }

  const upcoming = ros.find((r) => r.atDate > now) || ros[ros.length - 1];
  const due = slots.find((s) => !state.welfareLog[s.id] && s.at <= now);
  const nextRound =
    slots.find(
      (s) =>
        !state.welfareLog[s.id] &&
        s.at >= new Date(now.getTime() - 5 * 60000),
    ) || slots.find((s) => !state.welfareLog[s.id]);

  function onPassClick(n: number) {
    if (!checkedSet.has(n) && checkedSet.size >= CAP) {
      if (
        !window.confirm(
          `At working cap (${CAP}, estimate). Check in pass ${passLabel(n)} anyway?`,
        )
      ) {
        return;
      }
      checkIn(n, true);
      return;
    }
    checkIn(n);
  }

  function exportLog() {
    const payload = {
      exportedAt: new Date().toISOString(),
      event: OPS_DATA.event.id,
      checkedIn: state.checked,
      count: state.checked.length,
      cap: CAP,
      capLabel: OPS_DATA.capacity.workingCapLabel,
      welfareLog: state.welfareLog,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "motion-night-ops-log.json";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  if (!hydrated) {
    return <p className="lede">Loading local state…</p>;
  }

  return (
    <div>
      <div className="head-row" style={{ marginBottom: 12 }}>
        <div>
          <h1
            style={{
              margin: 0,
              fontFamily: "var(--f-display)",
              fontStyle: "italic",
              fontSize: 28,
            }}
          >
            Night-Of Ops
          </h1>
          <p className="lede" style={{ marginBottom: 0 }}>
            Passes, run-of-show, welfare, budget — device-local storage.
          </p>
        </div>
        <div className="mono" style={{ textAlign: "right" }}>
          <div style={{ fontSize: 18 }} data-testid="ops-clock">
            {fmtClock(now)}
          </div>
          <div className="dim" style={{ fontSize: 12 }}>
            {fmtDate(now)}
            {state.clockMode !== "live" ? " · sim" : ""}
          </div>
        </div>
      </div>

      {minsToCollision <= 45 && minsToCollision >= -15 ? (
        <div className="banner alert" data-testid="collision-banner">
          <strong>12:30 collision</strong> — last entry, master fader, and
          welfare round {collisionSlot?.n ?? ""} land together.{" "}
          {collisionLogged ? "Round logged." : "Log the round and assign cover."}
        </div>
      ) : minsToCollision > 45 && minsToCollision <= 90 ? (
        <div className="banner">
          <strong>Heads up</strong> — 12:30 collision window in{" "}
          {countdown(collision, now)}.
        </div>
      ) : null}

      <section className="stats" aria-live="polite">
        <div
          className={`stat ${checkedSet.size >= CAP ? "hot" : checkedSet.size > 0 ? "ok" : ""}`}
          id="statIn"
        >
          <div className="k">Checked in</div>
          <div className="v mono" data-testid="count-in">
            {checkedSet.size}
          </div>
          <div className="s">
            of {CAP} cap <LabelTag label="estimate" />
          </div>
        </div>
        <div className={`stat ${roomLeft(checkedSet.size) <= 5 ? "hot" : ""}`}>
          <div className="k">Room left</div>
          <div className="v mono">{roomLeft(checkedSet.size)}</div>
          <div className="s">vs working cap</div>
        </div>
        <div
          className={`stat ${upcoming.alert === "collision" || upcoming.kind === "cue" ? "hot" : ""}`}
        >
          <div className="k">Next cue</div>
          <div className="v mono" style={{ fontSize: 16 }}>
            {fmtTime(upcoming.atDate).replace(" ", "")}
          </div>
          <div className="s">{upcoming.moment}</div>
        </div>
      </section>

      <div className="ops-tabs" role="tablist">
        {(
          [
            ["checkin", "Door"],
            ["show", "Show"],
            ["welfare", "Welfare"],
            ["budget", "Budget"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={tab === id}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "checkin" && (
        <section className="panel" data-testid="checkin-panel">
          <h2>
            Pass check-in{" "}
            <span className="meta">
              001–{passLabel(PASS_COUNT)} · {checkedSet.size} in
            </span>
          </h2>
          <p className="lede">
            Numbered passes only — no guest names. Cap is the working estimate
            (~{CAP}).
          </p>
          <div className="tools">
            <input
              type="search"
              inputMode="numeric"
              placeholder="Jump to #"
              aria-label="Jump to pass number"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              data-testid="pass-search"
            />
            <button
              className="btn ghost"
              type="button"
              onClick={undoCheckIn}
              disabled={!canUndo}
            >
              Undo last
            </button>
            <button
              className="btn ghost"
              type="button"
              onClick={() => {
                if (window.confirm("Clear all check-ins on this device?")) {
                  resetCheckIn();
                }
              }}
            >
              Reset
            </button>
          </div>
          <div className="pass-grid" role="list">
            {Array.from({ length: PASS_COUNT }, (_, i) => i + 1)
              .filter((n) => {
                const q = query.replace(/\D/g, "");
                if (!q) return true;
                return passLabel(n).includes(q) || String(n) === q;
              })
              .map((n) => {
                const inn = checkedSet.has(n);
                const over = !inn && checkedSet.size >= CAP;
                return (
                  <button
                    key={n}
                    type="button"
                    className={`pass${inn ? " in" : ""}${over ? " over" : ""}`}
                    aria-pressed={inn}
                    data-testid={`pass-${n}`}
                    onClick={() => onPassClick(n)}
                  >
                    {passLabel(n)}
                  </button>
                );
              })}
          </div>
        </section>
      )}

      {tab === "show" && (
        <section className="panel">
          <h2>
            Run of show <span className="meta">crew times</span>
          </h2>
          <p className="lede">
            Doors 9 PM · last entry 12:30 · last pour 1:45 · hard stop 2 AM. Set
            times stay off public promo.
          </p>
          <ul className="timeline">
            {ros.map((r, i) => {
              const isNow = i === currentIdx;
              const isPast =
                !isNow &&
                (now > (ros[i + 1]?.atDate ?? r.atDate) || i < currentIdx);
              const cd =
                isNow
                  ? `NOW · ${countdown(ros[i + 1]?.atDate ?? eventDateTime(OPS_DATA.event.hardStop), now)} to next`
                  : now < r.atDate
                    ? `in ${countdown(r.atDate, now)}`
                    : "done";
              return (
                <li
                  key={r.id}
                  className={`${r.kind}${isNow ? " now" : ""}${isPast ? " past" : ""}`}
                >
                  <div className="when mono">{fmtTime(r.atDate)}</div>
                  <div className="moment">{r.moment}</div>
                  <div className="lead">
                    {r.lead}
                    {r.alert === "collision" ? " · collision window" : ""}
                  </div>
                  <div className="cd mono">{cd}</div>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {tab === "welfare" && (
        <section className="panel" data-testid="welfare-panel">
          <h2>
            Welfare rounds <span className="meta">every 30 min</span>
          </h2>
          <div className="welfare-next">
            <div className="caps">Next round</div>
            <div className="big mono" data-testid="welfare-countdown">
              {due
                ? "DUE NOW"
                : nextRound
                  ? countdown(nextRound.at, now)
                  : "Done"}
            </div>
            <div className="sub dim">
              {due
                ? `Round ${due.n} · ${fmtTime(due.at)}${due.collision ? " · COLLISION" : ""}`
                : nextRound
                  ? `Round ${nextRound.n} · ${fmtTime(nextRound.at)}${nextRound.collision ? " · " + OPS_DATA.welfare.collisionNote : ""}`
                  : "All rounds logged or past hard stop."}
            </div>
          </div>
          <div className="tools">
            <button
              className="btn primary"
              type="button"
              data-testid="log-round"
              onClick={() => {
                const target = due || nextRound;
                if (target) logWelfare(target.id);
              }}
            >
              Log this round
            </button>
            <button
              className="btn ghost"
              type="button"
              onClick={() => {
                if (window.confirm("Clear welfare log on this device?")) {
                  resetWelfare();
                }
              }}
            >
              Clear log
            </button>
          </div>
          <div className="round-list">
            {slots.map((s) => {
              const logged = state.welfareLog[s.id];
              return (
                <div
                  key={s.id}
                  className={`round${logged ? " done" : ""}${!logged && s.at <= now ? " due" : ""}${s.collision ? " collision" : ""}`}
                  data-testid={`round-${s.id}`}
                >
                  <div className="t mono">{fmtTime(s.at)}</div>
                  <div className="n">
                    <b>Round {s.n}</b>
                    {s.collision ? " · last entry + fader + round" : ""}
                    {logged ? (
                      <>
                        <br />
                        Logged {new Date(logged).toLocaleTimeString()}
                      </>
                    ) : null}
                  </div>
                  <button
                    className={`btn ${logged ? "ghost" : "primary"}`}
                    type="button"
                    onClick={() => toggleWelfare(s.id)}
                  >
                    {logged ? "Undo" : "Log"}
                  </button>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {tab === "budget" && (
        <section className="panel">
          <h2>
            Budget snapshot <span className="meta">read-only</span>
          </h2>
          <p className="lede">
            Pool money in the headline tiles; DJ fee and CDJ rental are outside
            the pool.
          </p>
          <div className="budget-grid">
            <div className="budget-tile">
              <div className="k">
                Pool <LabelTag label={OPS_DATA.budget.pool.label} />
              </div>
              <div className="v mono">
                {fmtMoney(OPS_DATA.budget.pool.amount)}
              </div>
            </div>
            <div className="budget-tile">
              <div className="k">
                Spend <LabelTag label={OPS_DATA.budget.spend.label} />
              </div>
              <div className="v mono">
                {fmtMoney(OPS_DATA.budget.spend.amount)}
              </div>
            </div>
            <div className="budget-tile">
              <div className="k">
                Buffer <LabelTag label={OPS_DATA.budget.buffer.label} />
              </div>
              <div className="v mono">
                {fmtMoney(OPS_DATA.budget.buffer.amount)}
              </div>
            </div>
          </div>
          <div className="lines">
            {OPS_DATA.budget.lines.map((line) => (
              <div className="line-row" key={line.item}>
                <div>
                  {line.item}
                  <div className="from">
                    {line.from} · <LabelTag label={line.label} />
                  </div>
                </div>
                <div className="amt mono">{fmtMoney(line.amount)}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="sim-bar">
        <label>
          Clock{" "}
          <select
            aria-label="Clock mode"
            value={state.clockMode}
            onChange={(e) =>
              patch({
                clockMode: e.target.value as "live" | "event" | "custom",
              })
            }
            data-testid="clock-mode"
          >
            <option value="live">Live</option>
            <option value="event">Jump to event night</option>
            <option value="custom">Custom offset</option>
          </select>
        </label>
        {state.clockMode === "custom" && (
          <label>
            Offset min{" "}
            <input
              type="number"
              step={15}
              value={state.clockOffsetMin}
              onChange={(e) =>
                patch({ clockOffsetMin: Number(e.target.value) || 0 })
              }
              style={{ width: "5.5rem" }}
            />
          </label>
        )}
        <button
          className="btn ghost"
          type="button"
          style={{ padding: "6px 10px", fontSize: 10 }}
          onClick={exportLog}
        >
          Export log
        </button>
      </div>
      <p className="lede" style={{ textAlign: "center", fontSize: 11 }}>
        Local draft · venue address never stored · guest PII stays out
      </p>
    </div>
  );
}
