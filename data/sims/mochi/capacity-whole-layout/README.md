# AFTERIMAGE 001: whole-layout capacity sim (Mochi, 20 Oct 2026)
**Source:** the floor plan model in `orch/context/assets/geom.py` (scale 0.875 in/px), plus the one real measurement: the living room at 14 × 18 ft 1 in ≈ 253 sq ft (5 Oct).
**Rule:** 7 sq ft per person, crew included. This is the fire-department rule given by Jovanni.
**Open spaces:** living room, kitchen, hall/entry, Bed 1, Bed 2, balcony. **Not counted:** Bed 3, both baths, laundry.

| Space | Usable sq ft (low / best / high) | How it was derived |
|---|---|---|
| Bed 1 + Bed 2 | 265 / 310 / 355 | 215 + 228 sq ft gross, with 60/70/80% of the floor clear once beds are pushed aside |
| Kitchen | 94 / 127 / 158 | Kitchen zone drawn around the fixtures, minus the fridge, counters, pantry and island (see `kitchen_hall_sim_output.json`) |
| Balcony | 35 / 40 / 48 | 48 sq ft gross |
| Living room | 190 / 205 / 215 | 253 sq ft measured, minus 40–60 for the decks, table and speakers |
| Hall / entry | 90 / 177 / 177 | The rest of the open plan's clear floor (430 sq ft) minus the living room; the low case counts only half, so the exit path stays clear |
| **Total** | **~675 / ~860 / ~950** | |
| **People at 7 sq ft** | **~96 / ~123 / ~136** | |

Bed 1 + Bed 2 + kitchen + balcony on their own come to about 477 sq ft, which holds about 68 people (range 63–73).

**Recommendation:** keep a hard cap of **70 passes**, crew included. The plan overstated the living room once already, and the crowd will bunch at the decks. Tape-measure the kitchen and hall to lock these numbers in.
