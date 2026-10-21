/* Night-Of Ops seed — from data/events.csv + web/seed.json + SoT.
   Numbers labeled confirmed / estimate / open. No guest names, no venue address. */
window.OPS_DATA = {
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
    status: "planning"
  },
  capacity: {
    workingCap: 50,
    workingCapLabel: "estimate",
    passesPlanned: 70,
    passesPlannedLabel: "open",
    note: "Working cap ~50 until kitchen + hall measurement. Passes are numbers only — no guest names in this app."
  },
  budget: {
    pool: { amount: 450, label: "confirmed", note: "Jovanni + Haven + Alex · $150 each" },
    spend: { amount: 381.13, label: "estimate", note: "Reconciled sheet · drinks/ice/cups + decor + DIY + smoking" },
    buffer: { amount: 68.87, label: "estimate", note: "pool − spend" },
    lines: [
      { item: "Drinks, ice + cups (150-cocktail menu)", amount: 231.13, from: "pool", label: "estimate" },
      { item: "Decor (mirror ball, bulbs, cloth)", amount: 76, from: "pool", label: "estimate" },
      { item: "DIY (eye posters + labels)", amount: 30, from: "pool", label: "estimate" },
      { item: "Smoking (cigs, lighters, decals)", amount: 44, from: "pool", label: "estimate" },
      { item: "HE//THEY fee", amount: 300, from: "jovanni", label: "confirmed" },
      { item: "CDJs + mixer rental", amount: 345, from: "rental", label: "confirmed" }
    ]
  },
  /* Crew-only set / cue times. Do not put these on public promo. */
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
    { id: "r2601", at: "02:00", moment: "Load-out and reset", lead: "Alex", kind: "ops", end: "03:00" }
  ],
  welfare: {
    intervalMin: 30,
    start: "21:00",
    end: "02:00",
    collisionAt: "00:30",
    collisionNote: "Last entry closes, master fader check, and a welfare round land together. Assign cover before the round."
  }
};
