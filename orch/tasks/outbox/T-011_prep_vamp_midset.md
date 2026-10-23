# T-011 · PREP ONLY — DJ VAMP mid-set (do not lock)

**Seat:** Cursor acting orchestrator  
**Timestamp (UTC):** 2026-10-20T19:49:22Z  
**Status:** PREP — **not a lineup lock**. Substance waits on DJ VAMP schedule reply.  
**Nothing** spent/sent/posted/published.

---

## Standing intent (RECORD — do not treat as lock)

- **Jovanni standing intent:** if VAMP can play, fits **mid set**.
- **Blocked on:** VAMP schedule reply (external). No confirmation in repo as of this prep (search: no `VAMP` artist line in SoT/outbox).

## Current locked core (already in SoT — cite only)

Running order (SoT Decided 17/18 Oct layers; times internal only — no set times on public flyer unless Jovanni asks):

1. **iamariology b2b raymixes** — open  
2. **Glamz** — mid / solo (confirmed play; free / no fee per Decided 18 Oct)  
3. **HE//THEY · co.b b2b NiiON** — headline  

## One-step merge diff (apply ONLY after Jovanni confirms VAMP)

When Jovanni says yes (and VAMP schedule fits), Claude/acting applies this as a single SoT patch — **not before**:

### A. `orch/context/SOURCE_OF_TRUTH_latest.md` — add under Decided (new dated block)

```markdown
## Decided <DATE> (Jovanni — VAMP confirmed)
- **DJ VAMP** joins the mid set (after openers, before HE//THEY). Schedule fit: confirmed by VAMP reply <pointer>.
- Internal running order: iamariology b2b raymixes → Glamz → **VAMP** → HE//THEY · co.b b2b NiiON.
  (Exact slot boundaries: open until Jovanni sets them; still no set times on public flyer.)
- Fee / promo credit for VAMP: <confirmed | estimate | open — fill from Jovanni only>.
- Promo: no naming VAMP on public surfaces until Jovanni OKs post.
```

### B. BOARD / metrics

- Board: mark T-011 lineup lock **done** only after the SoT block lands and Pip verifies.
- If a fee is confirmed, add a labeled money line (do not invent). DJ committed total may need re-reconcile vs T-003 $475 — **Pip**.

### C. Do NOT

- Do not edit flyer/reel/IG copy in this step without a separate Jovanni OK.
- Do not invent set times for the public flyer.
- Do not put venue address or guest names anywhere.

## Open questions for Pip / Jovanni

1. Does VAMP replace Glamz mid, share mid, or insert as a fourth slot?
2. Fee and promo credit wording?
3. Does $475 DJ committed (T-003) already include VAMP or not?

## Pointers

- Handback log: `orch/tasks/outbox/ACTING-ORCHESTRATOR_log.md`
- SoT lineup layers: `orch/context/SOURCE_OF_TRUTH_latest.md` (Decided 16–18 Oct)
