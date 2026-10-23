# T-001 support · Friday venue tape (23 Oct) — code notes only

**Seat:** Cursor acting orchestrator  
**Timestamp (UTC):** 2026-10-20T19:49:22Z  
**Status:** PREP pointer — measurements not landed yet  
**Owners when live:** Alex/Jovanni measure · Codex sims · Cursor owns code support  
**Nothing** spent/sent/posted/published. **No venue address** in any file.

---

## What lands (expected inputs — do not invent numbers)

When tape comes back, expect labeled measurements for:

- Kitchen clear floor (sq ft / narrowest path)
- Hall clear floor / hall opening width
- DJ-wall length (re-tape vs 5 Oct “about 14 ft” assumption)
- Optional: Bed 3 door position, front-door location, ceiling height (~9 ft open)

Label every figure **confirmed** (on-site) vs **estimate**.

## Code support checklist (Cursor when numbers arrive)

1. **Room Studio** (`orch/context/studio/index.html`): enter kitchen/hall + DJ-wall into calibrate / layout; keep `DEFAULT_LAYOUT` updates intentional; localStorage key `afterimage-studio-v8`.
2. **Sims:** hand Codex the confirmed numbers for full matrix (1 vs 2 baths × early/spread/late × light/med/heavy) — Cursor does not invent sim outputs.
3. **API path (post T-018 merge):** if studio/sim jobs go through BFF, use existing `services/api` only (`/api/*` / studio+sims modules) — **do not** stand up a second API; **do not** touch Codex `data-platform/`.
4. **Metrics:** update `data/metrics.csv` capacity rows with source = “venue tape 23 Oct” (or actual date) + confirmed/estimate.
5. **SoT:** propose or record under Claude/acting SoT rules with outbox changelog + Pip verify flag — capacity vs pass cap 70 (T-003) may need a re-check, not an automatic change.

## Out of scope for this note

- Shopping, neighbour flyer text, spend
- Guest names / pass holder PII
- Publishing Studio artifact without Jovanni OK

## Cross-refs

- Board T-001 (Codex blocked historically on venue visit TBD)
- Cap 70 confirmed T-003 (acting brief 20 Oct) — tape may challenge comfort, not invent a new cap alone
- Handback: `orch/tasks/outbox/ACTING-ORCHESTRATOR_log.md`
