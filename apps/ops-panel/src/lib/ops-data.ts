/**
 * Night-Of / Operations seed — from ops/data.js + web/seed.json + SoT.
 * Numbers labeled confirmed / estimate / open.
 * No guest names, no venue address.
 */

export type ConfidenceLabel = "confirmed" | "estimate" | "open";

export type MoneyLine = {
  item: string;
  amount: number;
  from: "pool" | "jovanni" | "rental";
  label: ConfidenceLabel;
};

export type RunMoment = {
  id: string;
  at: string;
  moment: string;
  lead: string;
  kind: "ops" | "set" | "cue";
  alert?: "collision";
  end?: string;
};

export type LibraryItem = {
  id: string;
  title: string;
  source: string;
  type: string;
  description: string;
  url: string;
  pinned?: boolean;
  tags?: string[];
};

export const OPS_DATA = {
  event: {
    id: "E001",
    name: "Devil's Night",
    series: "AFTERIMAGE 001",
    date: "2026-10-30",
    tz: "America/Chicago",
    doors: "21:00",
    lastEntry: "00:30",
    lastPour: "01:45",
    hardStop: "02:00",
    status: "planning" as const,
  },
  capacity: {
    workingCap: 50,
    workingCapLabel: "estimate" as ConfidenceLabel,
    passesPlanned: 70,
    passesPlannedLabel: "open" as ConfidenceLabel,
    note: "Working cap ~50 until kitchen + hall measurement. Passes are numbers only — no guest names in this app.",
  },
  budget: {
    pool: {
      amount: 450,
      label: "confirmed" as ConfidenceLabel,
      note: "Jovanni + Haven + Alex · $150 each",
    },
    spend: {
      amount: 381.13,
      label: "estimate" as ConfidenceLabel,
      note: "Reconciled sheet · drinks/ice/cups + decor + DIY + smoking",
    },
    buffer: {
      amount: 68.87,
      label: "estimate" as ConfidenceLabel,
      note: "pool − spend",
    },
    lines: [
      {
        item: "Drinks, ice + cups (150-cocktail menu)",
        amount: 231.13,
        from: "pool",
        label: "estimate",
      },
      {
        item: "Decor (mirror ball, bulbs, cloth)",
        amount: 76,
        from: "pool",
        label: "estimate",
      },
      {
        item: "DIY (eye posters + labels)",
        amount: 30,
        from: "pool",
        label: "estimate",
      },
      {
        item: "Smoking (cigs, lighters, decals)",
        amount: 44,
        from: "pool",
        label: "estimate",
      },
      {
        item: "HE//THEY fee",
        amount: 300,
        from: "jovanni",
        label: "confirmed",
      },
      {
        item: "CDJs + mixer rental",
        amount: 345,
        from: "rental",
        label: "confirmed",
      },
    ] as MoneyLine[],
  },
  /** Crew-only set / cue times. Do not put these on public promo. */
  runOfShow: [
    { id: "r1800", at: "18:00", moment: "Load-in and room reset", lead: "Alex", kind: "ops" },
    { id: "r1900", at: "19:00", moment: "System build and cable check", lead: "Jovanni", kind: "ops" },
    { id: "r1945", at: "19:45", moment: "Sound check", lead: "HE//THEY / Jovanni", kind: "ops" },
    { id: "r2030", at: "20:30", moment: "Crew briefing", lead: "Alex", kind: "ops" },
    { id: "r2100", at: "21:00", moment: "Doors · iamariology b2b raymixes", lead: "iamariology b2b raymixes", kind: "set" },
    { id: "r2300", at: "23:00", moment: "Rohan Rali b2b Shubh Samtani", lead: "Rohan Rali b2b Shubh Samtani", kind: "set" },
    { id: "r2415", at: "00:15", moment: "HE//THEY · co.b b2b NiiON", lead: "HE//THEY", kind: "set" },
    { id: "r2430", at: "00:30", moment: "Last entry", lead: "Door / welfare", kind: "cue", alert: "collision" },
    { id: "r2530", at: "01:30", moment: "Costume winner", lead: "Jovanni", kind: "cue" },
    { id: "r2545", at: "01:45", moment: "Last pour", lead: "Water lead", kind: "cue" },
    { id: "r2600", at: "02:00", moment: "Last song · hard stop", lead: "Jovanni / Alex", kind: "cue" },
    { id: "r2601", at: "02:00", moment: "Load-out and reset", lead: "Alex", kind: "ops", end: "03:00" },
  ] as RunMoment[],
  lineupPublic: [
    { name: "iamariology", credit: "b2b", partner: "raymixes" },
    { name: "Rohan Rali", credit: "b2b", partner: "Shubh Samtani" },
    { name: "HE//THEY", credit: "co.b b2b NiiON", partner: null },
  ],
  welfare: {
    intervalMin: 30,
    start: "21:00",
    end: "02:00",
    collisionAt: "00:30",
    collisionNote:
      "Last entry closes, master fader check, and a welfare round land together. Assign cover before the round.",
  },
} as const;

export type OpsData = typeof OPS_DATA;

/** Safe SoT excerpts for Claude assist — no guest PII, no venue address. */
export const CLAUDE_SAFE_CONTEXT = `
MOTION Collective · Devil's Night · AFTERIMAGE 001 (crew assist context)

Event: Friday 30 October 2026. Doors 9:00 PM, last entry 12:30 AM, last pour 1:45 AM, hard stop 2:00 AM (America/Chicago).
Venue: private Rio apartment — address never stored or shared in this system; day-of by DM only.
Passes: numbered 001–070 planned (open); working door cap ~50 (estimate) until kitchen+hall measurement.

Lineup (promo order, no public set times):
1. iamariology b2b raymixes
2. Rohan Rali b2b Shubh Samtani (no fee)
3. HE//THEY · co.b b2b NiiON (headliner, fee $300 confirmed, paid by Jovanni not from pool)

Crew set times (internal only): doors/open 21:00 · Rohan Rali b2b Shubh Samtani 23:00–00:15 · HE//THEY 00:15.

Money: pool $450 confirmed (Jovanni/Haven/Alex $150 each). Pool spend ~$381.13 estimate, buffer ~$68.87 estimate.
Outside pool: HE//THEY $300 confirmed; CDJ rental $345 confirmed (Rock n Roll Rentals). Middle set has no fee.
Drinks: 150-cocktail menu locked (90 lemonades + 60 Palomas) — ~$231.13 estimate incl tax for drinks/ice/cups.
Retired figures, do not quote: $391.42, $171.88, $58.58.

Rules: never spend/send/post without Jovanni OK. Draft only. No haze/fog/lasers. Brand: night #060B13, ice, red accent ≤10%, Bodoni Moda + Jost.
Costume prize $40 (confirmed 16 Oct); judging 1:30 AM (originality 40 / execution 30 / commitment 30).
Welfare: 30-min rounds doors→hard stop; 12:30 collision (last entry + fader + welfare).

No unconfirmed names on promo. Guest personal data never in git or this app.
`.trim();

export const LIBRARY_SEED: LibraryItem[] = [
  {
    id: "room-studio",
    title: "Afterimage Room Studio",
    source: "Claude",
    type: "app",
    url: "https://claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV",
    description:
      "3D plan of the Rio room at real size, gear drag-and-drop, drink-spot ranking and night crowd sims.",
    pinned: true,
    tags: ["venue", "sim", "3D"],
  },
  {
    id: "logistics-control",
    title: "Logistics Control (15 Oct)",
    source: "Drive",
    type: "sheet",
    url: "https://docs.google.com/spreadsheets/d/1Bcdu-27ykECBOqn2Ih5thULI0TQx_AxmARQd-dWmZRo/edit",
    description:
      "Newest working board: run of show, roles, 150-cocktail menu, venue visit checklist.",
    pinned: true,
    tags: ["run of show", "budget", "roles"],
  },
  {
    id: "sot",
    title: "Current lock",
    source: "GitHub",
    type: "doc",
    url: "https://github.com/jovanniworking-a11y/Motion-Collective-HUB/blob/main/orch/context/CURRENT_LOCK.md",
    description:
      "21 Oct lineup and money lock. Wins over older Source of Truth paragraphs.",
    pinned: true,
    tags: ["decisions", "core"],
  },
  {
    id: "board",
    title: "Task board",
    source: "GitHub",
    type: "doc",
    url: "https://github.com/jovanniworking-a11y/Motion-Collective-HUB/blob/main/orch/tasks/BOARD.md",
    description: "T-001 to T-010+, owners and status for the agent orchestra.",
    pinned: false,
    tags: ["tasks"],
  },
  {
    id: "crew-hub",
    title: "Legacy crew hub (static)",
    source: "Repo",
    type: "app",
    url: "/legacy-note",
    description: "Original web/index.html catalog — superseded by this ops panel for day-to-day work.",
    pinned: false,
    tags: ["legacy"],
  },
  {
    id: "fx-library",
    title: "FX Library",
    source: "Claude",
    type: "app",
    url: "https://claude.ai/artifact/2Wn5UpD5rwZaQ9XsBUFFeH",
    description: "Effects gallery + cut rules + crew loop.",
    pinned: false,
    tags: ["creative", "fx"],
  },
];
