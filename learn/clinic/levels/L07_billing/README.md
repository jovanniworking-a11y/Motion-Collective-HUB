# Billing · 125 XP
Money is stored in **whole cents** (ints), never floats: `0.1 + 0.2 != 0.3` in a computer, and a bill must add up exactly.

Write in `quest.py`:
1. `invoice(items, prices, discount_pct=0)`: `items` is a list of `(service, qty)`, `prices` maps service → cents.
   Return `{"lines": [(service, qty, line_cents), ...], "subtotal": c, "discount": c, "total": c}`.
   The discount is `subtotal * discount_pct / 100`, rounded to the nearest cent. Unknown service → `KeyError`.
2. `money(cents)` → `"$1,234.50"` (negative: `"-$12.00"`).
3. `balance(invoices, payments)`: total of all invoice totals minus all payments (cents).

<details><summary>Hint</summary>

`f"{cents / 100:,.2f}"` formats with commas. Round half up with `int(subtotal * pct / 100 + 0.5)` for positive numbers.
</details>
