# py02 · Budget
Every number in MOTION is labelled confirmed / estimate / open. Here's a small version of the event budget.

Fill in `exercise.py`:
1. `total(items)`: the sum of every item's `cost` (ignore items whose cost is `None`, which means open).
2. `buffer(pool, items)`: `pool - total(items)`, rounded to 2 decimals.
3. `label_report(items)`: a dict of how much money is in each label, e.g. `{"confirmed": 241.42, "estimate": 150.0}` (round to 2 decimals; skip open items).
