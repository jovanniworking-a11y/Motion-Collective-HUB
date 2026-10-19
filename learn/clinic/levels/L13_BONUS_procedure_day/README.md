# ⭐ Bonus: procedure day · 150 XP
A pain clinic lives on procedure days (injections, nerve blocks, radiofrequency ablation). A case that isn't ready at the
door costs the room 30 minutes and frustrates everyone, so the software checks each case the day before.

**The clinical rules belong to Dr. Kim and the medical team.** This level is the admin logic that enforces whatever checklist they set;
the items below are placeholders to practise with.

Write in `quest.py`:
1. `missing(case)` → the list of what's missing, in this order (empty list = ready):
   - `"consent"` if `consent_signed` is not True
   - `"prior auth"` if `prior_auth` is not `"approved"` or `"not needed"`
   - if `sedation` is True: `"driver"` if `driver_confirmed` is not True, `"fasting"` if `npo_confirmed` is not True
   - `"blood thinner plan"` if `blood_thinner` is True and `blood_thinner_plan_confirmed` is not True
2. `room_schedule(cases, start="07:30", turnover=15)`: the procedure room runs cases back to back in the given order, with
   `turnover` minutes between cases. Each case has `minutes`. Return `[(start "HH:MM", end "HH:MM", name), ...]`.
   Cases that aren't ready (`missing(...)` not empty) are skipped and don't take room time.
