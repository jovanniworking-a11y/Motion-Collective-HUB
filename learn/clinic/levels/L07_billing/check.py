def run(q):
    inv = q.invoice([("consult", 1), ("trigger-point", 2)], q.PRICES, 10)
    assert inv["lines"] == [("consult", 1, 15000), ("trigger-point", 2, 9100)], f"lines: got {inv['lines']}"
    assert (inv["subtotal"], inv["discount"], inv["total"]) == (24100, 2410, 21690), f"totals: got {inv['subtotal'], inv['discount'], inv['total']}"
    assert q.invoice([("trigger-point", 1)], q.PRICES, 15)["discount"] == 683, "15% of $45.50 = $6.825 -> rounds to 683 cents"
    assert q.money(123450) == "$1,234.50" and q.money(5) == "$0.05" and q.money(-1200) == "-$12.00", "money formatting"
    assert q.balance([inv, q.invoice([("imaging-review", 1)], q.PRICES)], [10000, 5000]) == 21690 + 3500 - 15000, "balance"
    try: q.invoice([("massage", 1)], q.PRICES); raise AssertionError("an unknown service should raise KeyError")
    except KeyError: pass
