# T-003 · SoT / metrics cleanup — change-log (RECORD only)

**Seat:** Cursor acting orchestrator (Claude chat+Code out of usage)  
**Timestamp (UTC):** 2026-10-20T19:49:22Z  
**Branch:** `cursor/acting-orchestrator-4cc7`  
**Status:** draft for Pip hub verify — nothing spent/sent/posted/published  
**Policy:** RECORD only; no new policy originated.

---

## Pip flag (required)

**OPEN for Pip:** verify these SoT edits at the hub before the board treats them settled. Especially: DJ committed total **$475** (no prior `$475` string in repo; source = Jovanni/acting brief 20 Oct only) and personal-owes recomputation.

---

## What changed

| Layer | Field | Was (retired) | Now | Label | Source pointer |
|---|---|---|---|---|---|
| `data/metrics.csv` | `passes_issued` | 50 | **70** | confirmed | Jovanni/acting brief 20 Oct |
| `data/metrics.csv` | `dj_fees` | 300 | **475** | confirmed | Jovanni/acting brief 20 Oct (repo: no prior $475) |
| `data/metrics.csv` | `pool_spend` | 391.42 | **381.13** | estimate | Logistics Control 15 Oct; SoT Decided 16 Oct |
| `data/metrics.csv` | `pool_buffer` (added) | — / was 58.58 in SoT | **68.87** | estimate | Logistics Control 15 Oct; SoT Decided 16 Oct |
| `data/metrics.csv` | drinks roll-up | `drinks_with_tax` 171.88 | `drinks_ice_cups_with_tax` **231.13** | estimate | SoT Decided 16 Oct 150-cocktail |
| `orch/context/SOURCE_OF_TRUTH_latest.md` | Reconciled 20 Oct block + Money live snapshot | 13-Oct $391.42 / $58.58 / DJ-$300-only / cap-50 as live | reconciled set above | as labeled | same pointers; retired rows kept for audit |

## Why

Acting brief 20 Oct queue item 2: replace retired figures still living in `data/metrics.csv` and the SoT 13-Oct money/cap layer with the reconciled state already partially present in Decided 16 Oct / Logistics Control, plus cap-70 and DJ-$475 from the brief.

## Explicitly not invented

- Fee split of the **$175** above HE//THEY $300 inside the $475 total — **open**
- Jovanni personal cushion after $475 — **open** (14 Oct cushion figures not recalculated)
- No guest names; no venue address; no spend/send/post

## Files touched

- `data/metrics.csv`
- `orch/context/SOURCE_OF_TRUTH_latest.md`
- this changelog

## Cross-refs

- Backend merge (separate): default `claude/motion-files-consolidated-dx17w2` @ merge `06890c571aa3e7a2b2238b89db0962d0894badf0` (tip fold `9799bb6` / api `fc419bb`)
- Handback: `orch/tasks/outbox/ACTING-ORCHESTRATOR_log.md`
